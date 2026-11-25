#!/usr/bin/env python3
"""
migrate_to_sqlite.py — One-time migration from flat JSON to SQLite
==================================================================
Reads existing JSON tracking files and imports all data into the new
SQLite database. Original files are renamed to .json.bak (not deleted).

Run once:
    python migrate_to_sqlite.py

Safe to run multiple times — uses UPSERT logic, won't create duplicates.
"""

import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

from outreach_db import OutreachDB, normalize_url, normalize_name, validate_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("migrate")

# Source files
MESSAGED_PROFILES = Path("data-tracking/messaged_profiles.json")
OUTREACH_LOG = Path("data-tracking/outreach_log.json")
SENT_CANDIDATES = Path("data-tracking/sent_candidates.json")


def migrate_messaged_profiles(db: OutreachDB) -> int:
    """Import messaged_profiles.json — just a list of URLs."""
    if not MESSAGED_PROFILES.exists():
        log.info("No messaged_profiles.json found — skipping")
        return 0

    urls = json.loads(MESSAGED_PROFILES.read_text())
    count = 0
    for url in urls:
        url = normalize_url(url)
        if not db.is_duplicate(url):
            # Insert as prospect with minimal data (name unknown from this file)
            try:
                db.conn.execute("""
                    INSERT OR IGNORE INTO prospects
                        (profile_url, name, first_seen_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (url, None, datetime.now().isoformat(), datetime.now().isoformat()))
                count += 1
            except Exception as e:
                log.warning(f"  Skip URL {url}: {e}")
    db.conn.commit()
    log.info(f"Migrated {count} URLs from messaged_profiles.json")
    return count


def migrate_outreach_log(db: OutreachDB) -> int:
    """Import outreach_log.json — has candidate details and messages sent."""
    if not OUTREACH_LOG.exists():
        log.info("No outreach_log.json found — skipping")
        return 0

    data = json.loads(OUTREACH_LOG.read_text())
    count = 0

    # Handle both old format (outreach_log array) and new format (results array)
    entries = data.get("outreach_log", data.get("results", []))
    candidates = data.get("candidates", [])

    # First pass: import candidates with full profile data
    for cand in candidates:
        url = normalize_url(cand.get("url", ""))
        if not url:
            continue

        name = cand.get("name", "")
        # Don't validate name here — legacy data has "there" entries
        # We still want to record them, just mark them

        existing = db.get_prospect_by_url(url)
        if existing:
            # Update with any additional data
            db.conn.execute("""
                UPDATE prospects SET
                    college = COALESCE(?, college),
                    signal_type = COALESCE(?, signal_type),
                    specific_signal = COALESCE(?, specific_signal),
                    role_fit = COALESCE(?, role_fit),
                    score = COALESCE(?, score),
                    score_band = COALESCE(?, score_band),
                    updated_at = ?
                WHERE profile_url = ?
            """, (
                cand.get("college"), cand.get("signal_type"),
                cand.get("specific_signal"), cand.get("role_fit"),
                cand.get("score", {}).get("score") if isinstance(cand.get("score"), dict) else cand.get("score"),
                cand.get("score", {}).get("band") if isinstance(cand.get("score"), dict) else cand.get("score_band"),
                datetime.now().isoformat(), url
            ))
        else:
            score_val = cand.get("score")
            if isinstance(score_val, dict):
                score_num = score_val.get("score")
                score_band = score_val.get("band")
            else:
                score_num = score_val
                score_band = cand.get("score_band")

            db.conn.execute("""
                INSERT OR IGNORE INTO prospects
                    (profile_url, name, college, signal_type, specific_signal,
                     role_fit, score, score_band, first_seen_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url, name, cand.get("college"), cand.get("signal_type"),
                cand.get("specific_signal"), cand.get("role_fit"),
                score_num, score_band,
                cand.get("extracted_at", datetime.now().isoformat()),
                datetime.now().isoformat()
            ))

    db.conn.commit()

    # Second pass: import sent messages
    for entry in entries:
        url = normalize_url(entry.get("profile_url", ""))
        if not url:
            continue

        prospect = db.get_prospect_by_url(url)
        if not prospect:
            # Create minimal prospect record
            db.conn.execute("""
                INSERT OR IGNORE INTO prospects
                    (profile_url, first_seen_at, updated_at)
                VALUES (?, ?, ?)
            """, (url, datetime.now().isoformat(), datetime.now().isoformat()))
            db.conn.commit()
            prospect = db.get_prospect_by_url(url)

        if prospect:
            msg_text = entry.get("message_sent") or entry.get("message", "")
            sent_at = entry.get("sent_at", datetime.now().isoformat())

            # Check if this message already exists (idempotent migration)
            existing_msg = db.conn.execute("""
                SELECT 1 FROM messages
                WHERE prospect_id = ? AND message_text = ? AND direction = 'outbound'
            """, (prospect["id"], msg_text)).fetchone()

            if not existing_msg and msg_text:
                db.conn.execute("""
                    INSERT INTO messages
                        (prospect_id, direction, message_text, sent_at, approved_by)
                    VALUES (?, 'outbound', ?, ?, 'legacy')
                """, (prospect["id"], msg_text, sent_at))
                count += 1

                # Create pipeline entry
                db.conn.execute("""
                    INSERT OR IGNORE INTO pipeline
                        (prospect_id, stage, updated_at)
                    VALUES (?, 'opener_sent', ?)
                """, (prospect["id"], datetime.now().isoformat()))

    db.conn.commit()
    log.info(f"Migrated {count} messages from outreach_log.json")
    return count


def migrate_sent_candidates(db: OutreachDB) -> int:
    """Import sent_candidates.json — rich candidate data from legacy script."""
    if not SENT_CANDIDATES.exists():
        log.info("No sent_candidates.json found — skipping")
        return 0

    candidates = json.loads(SENT_CANDIDATES.read_text())
    count = 0

    for cand in candidates:
        url = normalize_url(cand.get("url", ""))
        if not url:
            continue

        name = normalize_name(cand.get("name", ""))
        is_student = cand.get("is_current_student")
        inferred_year = cand.get("inferred_current_year")

        existing = db.get_prospect_by_url(url)
        if existing:
            # Update with richer data
            db.conn.execute("""
                UPDATE prospects SET
                    name = COALESCE(NULLIF(?, ''), name),
                    specific_signal = COALESCE(?, specific_signal),
                    score = COALESCE(?, score),
                    score_band = COALESCE(?, score_band),
                    is_current_student = COALESCE(?, is_current_student),
                    inferred_year = COALESCE(?, inferred_year),
                    updated_at = ?
                WHERE profile_url = ?
            """, (
                name, cand.get("specific_signal"), cand.get("score"),
                cand.get("score_band"), is_student, inferred_year,
                datetime.now().isoformat(), url
            ))
        else:
            db.conn.execute("""
                INSERT OR IGNORE INTO prospects
                    (profile_url, name, specific_signal, score, score_band,
                     is_current_student, inferred_year, first_seen_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url, name, cand.get("specific_signal"), cand.get("score"),
                cand.get("score_band"), is_student, inferred_year,
                cand.get("timestamp", datetime.now().isoformat()),
                datetime.now().isoformat()
            ))

        db.conn.commit()

        # Map legacy status to pipeline stage
        status = cand.get("status", "")
        stage_map = {
            "no_message": "new",
            "connection_failed": "dead",
            "deferred_low_score": "deferred",
            "sent": "opener_sent",
            "dm_sent": "opener_sent",
        }
        stage = stage_map.get(status, "new")

        prospect = db.get_prospect_by_url(url)
        if prospect:
            db.conn.execute("""
                INSERT OR IGNORE INTO pipeline
                    (prospect_id, stage, updated_at)
                VALUES (?, ?, ?)
            """, (prospect["id"], stage, datetime.now().isoformat()))

        count += 1

    db.conn.commit()
    log.info(f"Migrated {count} candidates from sent_candidates.json")
    return count


def backup_json_files():
    """Rename original JSON files to .json.bak — keeps them, doesn't delete."""
    for f in [MESSAGED_PROFILES, OUTREACH_LOG, SENT_CANDIDATES]:
        if f.exists():
            bak = f.with_suffix(".json.bak")
            if not bak.exists():
                shutil.copy2(str(f), str(bak))
                log.info(f"Backed up: {f.name} → {bak.name}")
            else:
                log.info(f"Backup already exists: {bak.name} (skipping)")


def main():
    log.info("=" * 60)
    log.info("Migration: Flat JSON → SQLite")
    log.info("=" * 60)

    db = OutreachDB()

    try:
        # Run migrations
        p1 = migrate_messaged_profiles(db)
        p2 = migrate_outreach_log(db)
        p3 = migrate_sent_candidates(db)

        # Validate
        stats = db.get_stats()
        log.info("")
        log.info("─" * 40)
        log.info("MIGRATION COMPLETE")
        log.info(f"  Total prospects: {stats['total_prospects']}")
        log.info(f"  Total messages:  {stats['total_messaged']}")
        log.info(f"  Pipeline stages: {stats['pipeline']}")
        log.info("─" * 40)

        # Backup originals
        backup_json_files()

        log.info("")
        log.info("✓ Migration successful. SQLite database: data-tracking/outreach.db")
        log.info("  Original JSON files backed up as .json.bak")
        log.info("  You can safely continue using the new system.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
