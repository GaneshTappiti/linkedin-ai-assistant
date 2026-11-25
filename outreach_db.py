#!/usr/bin/env python3
"""
outreach_db.py — SQLite Memory Layer for clstr.in Outreach OS
=============================================================
Replaces all flat JSON files with a structured, queryable SQLite database.
Provides durable memory, crash recovery, deduplication, daily limit
enforcement, and full conversation history tracking.

Zero external dependencies — uses Python's built-in sqlite3.

Tables:
  - prospects: every person we've ever encountered
  - messages: every message sent or received
  - pipeline: follow-up stage tracking per prospect
  - sessions: agent run tracking with crash recovery
  - checkpoints: resume capability after crashes
  - approvals: human-in-the-loop approval queue
"""

import sqlite3
import uuid
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

log = logging.getLogger("outreach_db")

DB_PATH = Path("data-tracking/outreach.db")

# ═══════════════════════════════════════════════════════════════════
# IDENTITY VALIDATION — hard-fail on garbage names
# ═══════════════════════════════════════════════════════════════════
REJECTED_NAMES = {
    "there", "linkedin member", "linkedin user", "unknown",
    "name", "user", "member", "n/a", "na", "none", "",
}

VALID_STAGES = {
    "new", "opener_sent", "followup_1", "followup_2", "followup_3",
    "awaiting_reply", "replied", "interested", "form_sent",
    "converted", "dead", "deferred", "re_engage", "busy",
}


def validate_name(name: str) -> bool:
    """
    Layered identity validation. Returns True if name is acceptable.

    HARD FAIL on:
      - Empty/None
      - Known placeholder strings ("there", "LinkedIn Member", etc.)
      - Single character names
      - Names that are just numbers
    """
    if not name or not name.strip():
        return False
    cleaned = name.strip().lower()
    if cleaned in REJECTED_NAMES:
        return False
    if len(cleaned) < 2:
        return False
    if cleaned.replace(" ", "").isdigit():
        return False
    # Reject names containing "• 2nd", "• 3rd" etc. (LinkedIn connection indicators)
    if "•" in name:
        # Strip the connection indicator but keep the name
        pass  # We'll clean this in normalize_name
    return True


def normalize_name(name: str) -> str:
    """Clean up LinkedIn artifacts from names."""
    if not name:
        return ""
    # Remove connection degree indicators
    for suffix in [" • 1st", " • 2nd", " • 3rd", " • 1st+", " • 2nd+"]:
        if suffix.lower() in name.lower():
            idx = name.lower().index(suffix.lower())
            name = name[:idx]
    return name.strip()


def normalize_url(url: str) -> str:
    """Normalize LinkedIn profile URL for dedup consistency."""
    if not url:
        return ""
    url = url.split("?")[0].rstrip("/")
    # Ensure consistent format
    if not url.startswith("https://"):
        if url.startswith("http://"):
            url = url.replace("http://", "https://", 1)
        elif url.startswith("www."):
            url = "https://" + url
        elif url.startswith("linkedin.com"):
            url = "https://www." + url
    return url


# ═══════════════════════════════════════════════════════════════════
# DATABASE CLASS
# ═══════════════════════════════════════════════════════════════════
class OutreachDB:
    """SQLite-backed persistent memory for the outreach system."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()
        self._migrate_schema()

    def _create_tables(self):
        """Create all tables if they don't exist."""
        self.conn.executescript("""
            -- Every prospect we've ever encountered
            CREATE TABLE IF NOT EXISTS prospects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT UNIQUE NOT NULL,
                name TEXT,
                college TEXT,
                headline TEXT,
                signal_type TEXT,
                specific_signal TEXT,
                role_fit TEXT,
                score INTEGER,
                score_band TEXT,
                is_current_student BOOLEAN,
                inferred_year INTEGER,
                first_seen_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            -- Every message sent or received
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL REFERENCES prospects(id),
                direction TEXT NOT NULL CHECK(direction IN ('outbound', 'inbound')),
                message_text TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                session_id TEXT,
                approved_by TEXT  -- NULL = pending, 'human' = manually approved, 'auto' = auto-sent
            );

            -- Follow-up pipeline tracking
            CREATE TABLE IF NOT EXISTS pipeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL UNIQUE REFERENCES prospects(id),
                stage TEXT NOT NULL DEFAULT 'opener_sent',
                sentiment TEXT,
                lead_score INTEGER,
                next_followup_at TEXT,
                updated_at TEXT NOT NULL
            );
            -- Stages: new, opener_sent, followup_1, followup_2, followup_3,
            --         awaiting_reply, replied, interested, form_sent,
            --         converted, dead, deferred, re_engage, busy

            -- Agent session tracking with crash recovery
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                messages_sent INTEGER DEFAULT 0,
                agent_type TEXT NOT NULL CHECK(agent_type IN ('outreach', 'inbox')),
                status TEXT DEFAULT 'running'
                    CHECK(status IN ('running', 'completed', 'crashed', 'stopped'))
            );

            -- Checkpoint for crash recovery / resume
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id),
                step TEXT NOT NULL,
                data TEXT,  -- JSON blob of state at this checkpoint
                created_at TEXT NOT NULL
            );

            -- Human approval queue
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL REFERENCES prospects(id),
                draft_message TEXT NOT NULL,
                signal_type TEXT,
                role_fit TEXT,
                status TEXT DEFAULT 'pending'
                    CHECK(status IN ('pending', 'approved', 'edited', 'skipped')),
                final_message TEXT,  -- What was actually sent (may differ if edited)
                reviewed_at TEXT,
                created_at TEXT NOT NULL
            );

            -- Indexes for fast lookups
            CREATE INDEX IF NOT EXISTS idx_prospects_url ON prospects(profile_url);
            CREATE INDEX IF NOT EXISTS idx_messages_prospect ON messages(prospect_id);
            CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);
            CREATE INDEX IF NOT EXISTS idx_pipeline_stage ON pipeline(stage);
            CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
            CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
        """)
        self.conn.commit()

    def _migrate_schema(self):
        """Run incremental schema migrations. Safe to call multiple times."""
        # Check which columns exist on pipeline table
        cols = {row[1] for row in self.conn.execute("PRAGMA table_info(pipeline)").fetchall()}

        if "followup_count" not in cols:
            self.conn.execute("ALTER TABLE pipeline ADD COLUMN followup_count INTEGER DEFAULT 0")
            log.info("Migration: added pipeline.followup_count")

        if "last_followup_stage" not in cols:
            self.conn.execute("ALTER TABLE pipeline ADD COLUMN last_followup_stage TEXT")
            log.info("Migration: added pipeline.last_followup_stage")

        self.conn.commit()

    # ───────────────────────────────────────────────────────────────
    # CONTEXT MANAGER — for transactions
    # ───────────────────────────────────────────────────────────────
    @contextmanager
    def transaction(self):
        """Atomic transaction context manager."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    # ───────────────────────────────────────────────────────────────
    # PROSPECT OPERATIONS
    # ───────────────────────────────────────────────────────────────
    def is_duplicate(self, url: str) -> bool:
        """Check if a profile URL has already been recorded."""
        url = normalize_url(url)
        row = self.conn.execute(
            "SELECT 1 FROM prospects WHERE profile_url = ?", (url,)
        ).fetchone()
        return row is not None

    def has_been_messaged(self, url: str) -> bool:
        """Check if we've already sent a message to this profile."""
        url = normalize_url(url)
        row = self.conn.execute("""
            SELECT 1 FROM messages m
            JOIN prospects p ON m.prospect_id = p.id
            WHERE p.profile_url = ? AND m.direction = 'outbound'
        """, (url,)).fetchone()
        return row is not None

    def record_prospect(
        self,
        profile_url: str,
        name: str,
        college: str = None,
        headline: str = None,
        signal_type: str = None,
        specific_signal: str = None,
        role_fit: str = None,
        score: int = None,
        score_band: str = None,
        is_current_student: bool = None,
        inferred_year: int = None,
    ) -> int:
        """
        Insert or update a prospect. Returns prospect ID.
        HARD FAILS if name validation fails.
        """
        url = normalize_url(profile_url)
        clean_name = normalize_name(name)

        if not validate_name(clean_name):
            raise ValueError(
                f"REJECTED: Name '{name}' failed identity validation. "
                f"URL: {url}. This message will NOT be sent."
            )

        now = datetime.now().isoformat()

        # Upsert — insert or update if exists
        existing = self.conn.execute(
            "SELECT id FROM prospects WHERE profile_url = ?", (url,)
        ).fetchone()

        if existing:
            self.conn.execute("""
                UPDATE prospects SET
                    name = COALESCE(?, name),
                    college = COALESCE(?, college),
                    headline = COALESCE(?, headline),
                    signal_type = COALESCE(?, signal_type),
                    specific_signal = COALESCE(?, specific_signal),
                    role_fit = COALESCE(?, role_fit),
                    score = COALESCE(?, score),
                    score_band = COALESCE(?, score_band),
                    is_current_student = COALESCE(?, is_current_student),
                    inferred_year = COALESCE(?, inferred_year),
                    updated_at = ?
                WHERE id = ?
            """, (clean_name, college, headline, signal_type, specific_signal,
                  role_fit, score, score_band, is_current_student, inferred_year,
                  now, existing["id"]))
            self.conn.commit()
            return existing["id"]
        else:
            cursor = self.conn.execute("""
                INSERT INTO prospects
                    (profile_url, name, college, headline, signal_type,
                     specific_signal, role_fit, score, score_band,
                     is_current_student, inferred_year, first_seen_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (url, clean_name, college, headline, signal_type, specific_signal,
                  role_fit, score, score_band, is_current_student, inferred_year,
                  now, now))
            self.conn.commit()
            return cursor.lastrowid

    def get_prospect_by_url(self, url: str) -> Optional[dict]:
        """Get prospect data by URL."""
        url = normalize_url(url)
        row = self.conn.execute(
            "SELECT * FROM prospects WHERE profile_url = ?", (url,)
        ).fetchone()
        return dict(row) if row else None

    def get_all_messaged_urls(self) -> set:
        """Get all profile URLs that have been messaged (for dedup compat)."""
        rows = self.conn.execute("""
            SELECT DISTINCT p.profile_url FROM prospects p
            JOIN messages m ON m.prospect_id = p.id
            WHERE m.direction = 'outbound'
        """).fetchall()
        return {row["profile_url"] for row in rows}

    # ───────────────────────────────────────────────────────────────
    # MESSAGE OPERATIONS
    # ───────────────────────────────────────────────────────────────
    def record_message(
        self,
        prospect_id: int,
        direction: str,
        message_text: str,
        session_id: str = None,
        approved_by: str = None,
    ) -> int:
        """Record a sent or received message. Returns message ID."""
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            INSERT INTO messages (prospect_id, direction, message_text, sent_at,
                                  session_id, approved_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (prospect_id, direction, message_text, now, session_id, approved_by))
        self.conn.commit()
        return cursor.lastrowid

    def get_conversation_history(self, prospect_id: int) -> list[dict]:
        """Get full conversation history for a prospect, chronologically."""
        rows = self.conn.execute("""
            SELECT * FROM messages
            WHERE prospect_id = ?
            ORDER BY sent_at ASC
        """, (prospect_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_last_message(self, prospect_id: int) -> Optional[dict]:
        """Get the most recent message in a conversation."""
        row = self.conn.execute("""
            SELECT * FROM messages
            WHERE prospect_id = ?
            ORDER BY sent_at DESC LIMIT 1
        """, (prospect_id,)).fetchone()
        return dict(row) if row else None

    # ───────────────────────────────────────────────────────────────
    # PIPELINE OPERATIONS
    # ───────────────────────────────────────────────────────────────
    def update_pipeline(
        self,
        prospect_id: int,
        stage: str,
        sentiment: str = None,
        lead_score: int = None,
        next_followup_at: str = None,
    ):
        """Update or create pipeline entry for a prospect."""
        now = datetime.now().isoformat()
        existing = self.conn.execute(
            "SELECT 1 FROM pipeline WHERE prospect_id = ?", (prospect_id,)
        ).fetchone()

        if existing:
            self.conn.execute("""
                UPDATE pipeline SET
                    stage = ?, sentiment = COALESCE(?, sentiment),
                    lead_score = COALESCE(?, lead_score),
                    next_followup_at = COALESCE(?, next_followup_at),
                    updated_at = ?
                WHERE prospect_id = ?
            """, (stage, sentiment, lead_score, next_followup_at, now, prospect_id))
        else:
            self.conn.execute("""
                INSERT INTO pipeline
                    (prospect_id, stage, sentiment, lead_score, next_followup_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (prospect_id, stage, sentiment, lead_score, next_followup_at, now))
        self.conn.commit()

    def get_pending_followups(self) -> list[dict]:
        """Get prospects that are due for follow-up."""
        now = datetime.now().isoformat()
        rows = self.conn.execute("""
            SELECT p.*, pl.stage, pl.sentiment, pl.lead_score,
                   pl.next_followup_at, pl.followup_count
            FROM pipeline pl
            JOIN prospects p ON p.id = pl.prospect_id
            WHERE pl.next_followup_at <= ?
              AND pl.stage NOT IN ('converted', 'dead')
            ORDER BY pl.lead_score DESC NULLS LAST
        """, (now,)).fetchall()
        return [dict(r) for r in rows]

    def get_followup_queue(self) -> list[dict]:
        """
        Get the prioritized follow-up queue: prospects due RIGHT NOW.
        Sorted by: lead_score DESC, days_overdue DESC, followup_count ASC.
        """
        now = datetime.now().isoformat()
        rows = self.conn.execute("""
            SELECT p.id, p.profile_url, p.name, p.college, p.headline,
                   pl.stage, pl.sentiment, pl.lead_score,
                   pl.next_followup_at, pl.followup_count,
                   pl.updated_at as pipeline_updated_at
            FROM pipeline pl
            JOIN prospects p ON p.id = pl.prospect_id
            WHERE pl.next_followup_at <= ?
              AND pl.stage NOT IN ('converted', 'dead')
            ORDER BY
                pl.lead_score DESC NULLS LAST,
                pl.next_followup_at ASC,
                pl.followup_count ASC
        """, (now,)).fetchall()
        return [dict(r) for r in rows]

    def get_overdue_followups(self, days: int = 7) -> list[dict]:
        """Get prospects with follow-ups overdue by N+ days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = self.conn.execute("""
            SELECT p.id, p.name, p.profile_url,
                   pl.stage, pl.next_followup_at, pl.followup_count
            FROM pipeline pl
            JOIN prospects p ON p.id = pl.prospect_id
            WHERE pl.next_followup_at IS NOT NULL
              AND pl.next_followup_at < ?
              AND pl.stage NOT IN ('converted', 'dead')
            ORDER BY pl.next_followup_at ASC
        """, (cutoff,)).fetchall()
        return [dict(r) for r in rows]

    def advance_pipeline_stage(
        self,
        prospect_id: int,
        new_stage: str,
        next_followup_at: str = None,
        sentiment: str = None,
    ):
        """
        Transition a prospect to a new pipeline stage.
        Increments followup_count and tracks the previous stage.
        """
        if new_stage not in VALID_STAGES:
            raise ValueError(f"Invalid stage: {new_stage}. Valid: {VALID_STAGES}")

        now = datetime.now().isoformat()
        existing = self.conn.execute(
            "SELECT stage, followup_count FROM pipeline WHERE prospect_id = ?",
            (prospect_id,)
        ).fetchone()

        if existing:
            current_stage = existing["stage"]
            count = (existing["followup_count"] or 0) + 1
            self.conn.execute("""
                UPDATE pipeline SET
                    stage = ?,
                    last_followup_stage = ?,
                    followup_count = ?,
                    next_followup_at = ?,
                    sentiment = COALESCE(?, sentiment),
                    updated_at = ?
                WHERE prospect_id = ?
            """, (new_stage, current_stage, count,
                  next_followup_at, sentiment, now, prospect_id))
        else:
            self.conn.execute("""
                INSERT INTO pipeline
                    (prospect_id, stage, followup_count, next_followup_at,
                     sentiment, updated_at)
                VALUES (?, ?, 1, ?, ?, ?)
            """, (prospect_id, new_stage, next_followup_at, sentiment, now))
        self.conn.commit()
        log.info(f"Pipeline advance: prospect {prospect_id} → {new_stage}")

    def schedule_followup(self, prospect_id: int, delay_days: int):
        """Set next_followup_at to now + delay_days."""
        followup_at = (datetime.now() + timedelta(days=delay_days)).isoformat()
        self.conn.execute("""
            UPDATE pipeline SET next_followup_at = ?, updated_at = ?
            WHERE prospect_id = ?
        """, (followup_at, datetime.now().isoformat(), prospect_id))
        self.conn.commit()
        log.info(f"Scheduled follow-up for prospect {prospect_id} in {delay_days} days")

    def archive_stale_prospects(self, max_attempts: int = 3) -> int:
        """
        Auto-move prospects to 'dead' after max_attempts follow-ups with no reply.
        Returns count of archived prospects.
        """
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            UPDATE pipeline SET
                stage = 'dead',
                last_followup_stage = stage,
                updated_at = ?
            WHERE followup_count >= ?
              AND stage NOT IN ('converted', 'dead', 'interested', 'replied', 'form_sent')
        """, (now, max_attempts))
        self.conn.commit()
        count = cursor.rowcount
        if count > 0:
            log.info(f"Archived {count} stale prospects (>= {max_attempts} follow-ups)")
        return count

    def get_relationship_age(self, prospect_id: int) -> Optional[int]:
        """Get days since first outbound contact. Returns None if never contacted."""
        row = self.conn.execute("""
            SELECT MIN(sent_at) as first_contact
            FROM messages
            WHERE prospect_id = ? AND direction = 'outbound'
        """, (prospect_id,)).fetchone()
        if row and row["first_contact"]:
            first = datetime.fromisoformat(row["first_contact"])
            return (datetime.now() - first).days
        return None

    def get_first_outbound_at(self, prospect_id: int) -> Optional[str]:
        """Get timestamp of first outbound message to a prospect."""
        row = self.conn.execute("""
            SELECT MIN(sent_at) as first
            FROM messages
            WHERE prospect_id = ? AND direction = 'outbound'
        """, (prospect_id,)).fetchone()
        return row["first"] if row else None

    # ───────────────────────────────────────────────────────────────
    # SESSION & CHECKPOINT OPERATIONS
    # ───────────────────────────────────────────────────────────────
    def start_session(self, agent_type: str) -> str:
        """Start a new agent session. Returns session ID."""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        self.conn.execute("""
            INSERT INTO sessions (id, started_at, agent_type, status)
            VALUES (?, ?, ?, 'running')
        """, (session_id, now, agent_type))
        self.conn.commit()
        log.info(f"Session started: {session_id} ({agent_type})")
        return session_id

    def end_session(self, session_id: str, status: str = "completed"):
        """Mark a session as complete or stopped."""
        now = datetime.now().isoformat()
        sent = self.conn.execute(
            "SELECT COUNT(*) as c FROM messages WHERE session_id = ? AND direction = 'outbound'",
            (session_id,)
        ).fetchone()["c"]
        self.conn.execute("""
            UPDATE sessions SET ended_at = ?, status = ?, messages_sent = ?
            WHERE id = ?
        """, (now, status, sent, session_id))
        self.conn.commit()
        log.info(f"Session ended: {session_id} → {status} ({sent} messages)")

    def recover_crashed_sessions(self):
        """Mark any 'running' sessions as 'crashed'. Call on startup."""
        crashed = self.conn.execute(
            "SELECT id FROM sessions WHERE status = 'running'"
        ).fetchall()
        for row in crashed:
            self.conn.execute(
                "UPDATE sessions SET status = 'crashed', ended_at = ? WHERE id = ?",
                (datetime.now().isoformat(), row["id"])
            )
            log.warning(f"Recovered crashed session: {row['id']}")
        self.conn.commit()
        return len(crashed)

    def save_checkpoint(self, session_id: str, step: str, data: str = None):
        """Save a checkpoint for crash recovery."""
        now = datetime.now().isoformat()
        self.conn.execute("""
            INSERT INTO checkpoints (session_id, step, data, created_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, step, data, now))
        self.conn.commit()

    def get_last_checkpoint(self, session_id: str) -> Optional[dict]:
        """Get the most recent checkpoint for a session."""
        row = self.conn.execute("""
            SELECT * FROM checkpoints
            WHERE session_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (session_id,)).fetchone()
        return dict(row) if row else None

    # ───────────────────────────────────────────────────────────────
    # APPROVAL QUEUE OPERATIONS
    # ───────────────────────────────────────────────────────────────
    def create_approval(
        self,
        prospect_id: int,
        draft_message: str,
        signal_type: str = None,
        role_fit: str = None,
    ) -> int:
        """Add a draft message to the approval queue. Returns approval ID."""
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            INSERT INTO approvals
                (prospect_id, draft_message, signal_type, role_fit, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (prospect_id, draft_message, signal_type, role_fit, now))
        self.conn.commit()
        return cursor.lastrowid

    def approve_message(self, approval_id: int, final_message: str = None):
        """Mark an approval as approved, optionally with an edited message."""
        now = datetime.now().isoformat()
        if final_message:
            self.conn.execute("""
                UPDATE approvals SET status = 'edited', final_message = ?, reviewed_at = ?
                WHERE id = ?
            """, (final_message, now, approval_id))
        else:
            self.conn.execute("""
                UPDATE approvals SET status = 'approved', reviewed_at = ? WHERE id = ?
            """, (now, approval_id))
        self.conn.commit()

    def skip_approval(self, approval_id: int):
        """Mark an approval as skipped."""
        now = datetime.now().isoformat()
        self.conn.execute("""
            UPDATE approvals SET status = 'skipped', reviewed_at = ? WHERE id = ?
        """, (now, approval_id))
        self.conn.commit()

    def get_approved_message(self, approval_id: int) -> Optional[str]:
        """Get the final message to send (edited version or original draft)."""
        row = self.conn.execute(
            "SELECT draft_message, final_message, status FROM approvals WHERE id = ?",
            (approval_id,)
        ).fetchone()
        if not row or row["status"] == "skipped":
            return None
        return row["final_message"] or row["draft_message"]

    # ───────────────────────────────────────────────────────────────
    # DAILY LIMIT ENFORCEMENT
    # ───────────────────────────────────────────────────────────────
    def get_daily_send_count(self, target_date: date = None) -> int:
        """Get number of outbound messages sent on a specific date."""
        if target_date is None:
            target_date = date.today()
        date_str = target_date.isoformat()
        row = self.conn.execute("""
            SELECT COUNT(*) as c FROM messages
            WHERE direction = 'outbound'
              AND DATE(sent_at) = ?
        """, (date_str,)).fetchone()
        return row["c"]

    def can_send_today(self, max_daily: int = 10) -> tuple[bool, int]:
        """Check if we can send more messages today. Returns (can_send, remaining)."""
        sent = self.get_daily_send_count()
        remaining = max(0, max_daily - sent)
        return remaining > 0, remaining

    def get_daily_opener_count(self, target_date: date = None) -> int:
        """
        Get count of NEW cold openers sent today.
        These are outbound messages to prospects whose pipeline stage is 'opener_sent'
        or 'new' — i.e., first contact.
        """
        if target_date is None:
            target_date = date.today()
        date_str = target_date.isoformat()
        row = self.conn.execute("""
            SELECT COUNT(*) as c FROM messages m
            JOIN pipeline pl ON pl.prospect_id = m.prospect_id
            WHERE m.direction = 'outbound'
              AND DATE(m.sent_at) = ?
              AND pl.stage IN ('opener_sent', 'new')
              AND pl.followup_count = 0
        """, (date_str,)).fetchone()
        return row["c"]

    def get_daily_followup_count(self, target_date: date = None) -> int:
        """
        Get count of follow-up messages sent today.
        These are outbound messages to prospects past the opener stage.
        """
        if target_date is None:
            target_date = date.today()
        date_str = target_date.isoformat()
        row = self.conn.execute("""
            SELECT COUNT(*) as c FROM messages m
            JOIN pipeline pl ON pl.prospect_id = m.prospect_id
            WHERE m.direction = 'outbound'
              AND DATE(m.sent_at) = ?
              AND (pl.followup_count > 0
                   OR pl.stage IN ('followup_1', 'followup_2', 'followup_3'))
        """, (date_str,)).fetchone()
        return row["c"]

    def get_last_session_end(self, agent_type: str = None) -> Optional[datetime]:
        """Get the end time of the most recent completed session."""
        query = "SELECT ended_at FROM sessions WHERE status IN ('completed', 'stopped')"
        params = []
        if agent_type:
            query += " AND agent_type = ?"
            params.append(agent_type)
        query += " ORDER BY ended_at DESC LIMIT 1"
        row = self.conn.execute(query, params).fetchone()
        if row and row["ended_at"]:
            return datetime.fromisoformat(row["ended_at"])
        return None

    # ───────────────────────────────────────────────────────────────
    # ANALYTICS / REPORTING
    # ───────────────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        """Get overall outreach statistics."""
        total_prospects = self.conn.execute(
            "SELECT COUNT(*) as c FROM prospects"
        ).fetchone()["c"]
        total_messaged = self.conn.execute(
            "SELECT COUNT(DISTINCT prospect_id) as c FROM messages WHERE direction = 'outbound'"
        ).fetchone()["c"]
        total_replies = self.conn.execute(
            "SELECT COUNT(DISTINCT prospect_id) as c FROM messages WHERE direction = 'inbound'"
        ).fetchone()["c"]
        today_sent = self.get_daily_send_count()
        total_sessions = self.conn.execute(
            "SELECT COUNT(*) as c FROM sessions"
        ).fetchone()["c"]
        crashed_sessions = self.conn.execute(
            "SELECT COUNT(*) as c FROM sessions WHERE status = 'crashed'"
        ).fetchone()["c"]

        # Pipeline breakdown
        pipeline_stats = {}
        rows = self.conn.execute(
            "SELECT stage, COUNT(*) as c FROM pipeline GROUP BY stage"
        ).fetchall()
        for row in rows:
            pipeline_stats[row["stage"]] = row["c"]

        return {
            "total_prospects": total_prospects,
            "total_messaged": total_messaged,
            "total_replies": total_replies,
            "today_sent": today_sent,
            "total_sessions": total_sessions,
            "crashed_sessions": crashed_sessions,
            "pipeline": pipeline_stats,
        }

    # ───────────────────────────────────────────────────────────────
    # CLEANUP
    # ───────────────────────────────────────────────────────────────
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
