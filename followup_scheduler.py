#!/usr/bin/env python3
"""
followup_scheduler.py — Cadence-Based Follow-Up Engine for clstr.in Outreach OS
================================================================================
Transforms the outreach system from reactive automation into persistent
relationship orchestration. Computes follow-up timing, manages cadence rules,
and presents a review queue — never auto-sends without approval.

Usage:
    python followup_scheduler.py scan           # Compute which followups are due
    python followup_scheduler.py queue          # Show the current follow-up queue
    python followup_scheduler.py review         # Interactive review mode
    python followup_scheduler.py status         # Show scheduling status summary
    python followup_scheduler.py backfill       # Set initial followup_at for existing data
    python followup_scheduler.py scan --dry-run # Preview without writing

Zero external dependencies — uses Python stdlib only.
"""

import sys
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from outreach_db import OutreachDB, VALID_STAGES

log = logging.getLogger("followup_scheduler")


# ═══════════════════════════════════════════════════════════════════
# CADENCE RULES — the heart of relationship timing
# ═══════════════════════════════════════════════════════════════════

class CadenceRules:
    """
    Defines the follow-up cadence for each pipeline stage.

    Each rule maps: (current_stage, trigger) → (delay_days, next_stage)
    Trigger is checked by the scheduler when scanning.
    """

    # Stage transition rules for NO-REPLY scenarios
    # Format: current_stage → (delay_days, next_stage)
    NO_REPLY_CADENCE = {
        "opener_sent":   (3,  "followup_1"),
        "followup_1":    (5,  "followup_2"),
        "followup_2":    (7,  "followup_3"),
        "followup_3":    (0,  "dead"),         # Auto-archive: max attempts reached
    }

    # Stage transition rules for REPLIED scenarios
    REPLY_CADENCE = {
        "replied":       (2,  "interested"),    # Warm reply → fast follow-up
        "interested":    (0,  None),            # Manual: wait for form response
        "form_sent":     (0,  None),            # Manual: wait for conversion
    }

    # Deferred re-engagement
    DEFERRED_DELAY_DAYS = 14  # Re-engage after 14 days
    DEFERRED_NEXT_STAGE = "re_engage"

    # Max follow-up attempts before auto-archive
    MAX_FOLLOWUP_ATTEMPTS = 3  # opener + 3 followups = 4 total touches

    @classmethod
    def get_no_reply_transition(cls, current_stage: str) -> Optional[tuple[int, str]]:
        """Get the next transition for a no-reply scenario."""
        return cls.NO_REPLY_CADENCE.get(current_stage)

    @classmethod
    def get_stage_delay(cls, current_stage: str) -> Optional[int]:
        """Get delay in days for a stage's follow-up."""
        rule = cls.NO_REPLY_CADENCE.get(current_stage)
        if rule:
            return rule[0]
        return None


# ═══════════════════════════════════════════════════════════════════
# SCHEDULER ENGINE
# ═══════════════════════════════════════════════════════════════════

class FollowUpScheduler:
    """
    Scans the pipeline and computes which follow-ups are due.
    Never sends automatically — produces a queue for review.
    """

    def __init__(self, db: OutreachDB, dry_run: bool = False):
        self.db = db
        self.dry_run = dry_run

    # ─────────────────────────────────────────────────────────────
    # SCAN — compute what's due
    # ─────────────────────────────────────────────────────────────
    def scan(self) -> list[dict]:
        """
        Scan the pipeline and identify prospects due for follow-up action.
        Returns a list of actions to take.

        An action looks like:
            {
                "prospect_id": 123,
                "name": "John",
                "current_stage": "opener_sent",
                "next_stage": "followup_1",
                "action": "schedule_followup" | "archive",
                "delay_days": 3,
                "reason": "No reply after 3 days",
            }
        """
        actions = []
        now = datetime.now()

        # Get all active pipeline entries (not dead/converted)
        rows = self.db.conn.execute("""
            SELECT p.id as prospect_id, p.name, p.profile_url, p.college,
                   pl.stage, pl.next_followup_at, pl.followup_count,
                   pl.sentiment, pl.lead_score
            FROM pipeline pl
            JOIN prospects p ON p.id = pl.prospect_id
            WHERE pl.stage NOT IN ('converted', 'dead')
            ORDER BY pl.updated_at ASC
        """).fetchall()

        for row in rows:
            r = dict(row)
            prospect_id = r["prospect_id"]
            current_stage = r["stage"]
            next_followup = r["next_followup_at"]
            followup_count = r["followup_count"] or 0

            # Skip prospects with a future follow-up already scheduled
            if next_followup:
                try:
                    followup_dt = datetime.fromisoformat(next_followup)
                    if followup_dt > now:
                        continue  # Not due yet
                except (ValueError, TypeError):
                    pass

            # Check if this prospect has a reply (inbound message)
            has_reply = self.db.conn.execute("""
                SELECT 1 FROM messages
                WHERE prospect_id = ? AND direction = 'inbound'
            """, (prospect_id,)).fetchone()

            if has_reply:
                # Don't auto-schedule follow-ups for prospects who replied
                # These should be handled manually or by the inbox agent
                continue

            # Get no-reply transition rule
            transition = CadenceRules.get_no_reply_transition(current_stage)
            if not transition:
                continue

            delay_days, next_stage = transition

            # Check if follow-up is actually due (based on last activity)
            if next_followup:
                # Has a scheduled followup that's past due → take action
                action_type = "archive" if next_stage == "dead" else "schedule_followup"
                actions.append({
                    "prospect_id": prospect_id,
                    "name": r["name"] or "?",
                    "college": r.get("college") or "—",
                    "profile_url": r["profile_url"],
                    "current_stage": current_stage,
                    "next_stage": next_stage,
                    "action": action_type,
                    "delay_days": delay_days,
                    "followup_count": followup_count,
                    "reason": f"No reply — advancing from {current_stage}",
                })
            else:
                # No follow-up scheduled at all — needs initial scheduling
                # Calculate based on when opener was sent
                first_sent = self.db.get_first_outbound_at(prospect_id)
                if first_sent:
                    try:
                        sent_dt = datetime.fromisoformat(first_sent)
                        due_dt = sent_dt + timedelta(days=delay_days)
                        if due_dt <= now:
                            # Already overdue
                            action_type = "archive" if next_stage == "dead" else "schedule_followup"
                            days_overdue = (now - due_dt).days
                            actions.append({
                                "prospect_id": prospect_id,
                                "name": r["name"] or "?",
                                "college": r.get("college") or "—",
                                "profile_url": r["profile_url"],
                                "current_stage": current_stage,
                                "next_stage": next_stage,
                                "action": action_type,
                                "delay_days": 0,  # Due now
                                "followup_count": followup_count,
                                "reason": f"Overdue by {days_overdue}d (sent {first_sent[:10]})",
                            })
                    except (ValueError, TypeError):
                        pass

        return actions

    # ─────────────────────────────────────────────────────────────
    # APPLY ACTIONS — execute computed transitions
    # ─────────────────────────────────────────────────────────────
    def apply_action(self, action: dict):
        """Apply a single follow-up action to the database."""
        if self.dry_run:
            log.info(f"DRY-RUN: Would apply {action['action']} for {action['name']}")
            return

        prospect_id = action["prospect_id"]
        next_stage = action["next_stage"]
        delay_days = action["delay_days"]

        if action["action"] == "archive":
            self.db.advance_pipeline_stage(prospect_id, "dead")
            log.info(f"Archived: {action['name']} (max follow-ups reached)")
        elif action["action"] == "schedule_followup":
            # Advance stage and schedule next follow-up
            next_transition = CadenceRules.get_no_reply_transition(next_stage)
            if next_transition:
                next_delay = next_transition[0]
                next_followup = (datetime.now() + timedelta(days=next_delay)).isoformat()
            else:
                next_followup = None

            self.db.advance_pipeline_stage(
                prospect_id, next_stage,
                next_followup_at=next_followup,
            )
            log.info(
                f"Advanced: {action['name']} → {next_stage}"
                f"{f' (next followup in {next_transition[0]}d)' if next_transition else ''}"
            )

    # ─────────────────────────────────────────────────────────────
    # BACKFILL — set initial followup_at for existing data
    # ─────────────────────────────────────────────────────────────
    def backfill(self) -> list[dict]:
        """
        For existing opener_sent prospects with no next_followup_at:
        compute when followup should be based on when opener was sent.
        Returns list of backfill actions taken.
        """
        now = datetime.now()
        results = []

        rows = self.db.conn.execute("""
            SELECT p.id, p.name, pl.stage
            FROM pipeline pl
            JOIN prospects p ON p.id = pl.prospect_id
            WHERE pl.stage = 'opener_sent'
              AND pl.next_followup_at IS NULL
        """).fetchall()

        for row in rows:
            r = dict(row)
            prospect_id = r["id"]
            name = r["name"] or "?"

            first_sent = self.db.get_first_outbound_at(prospect_id)
            if not first_sent:
                continue

            try:
                sent_dt = datetime.fromisoformat(first_sent)
                due_dt = sent_dt + timedelta(days=CadenceRules.NO_REPLY_CADENCE["opener_sent"][0])

                if due_dt <= now:
                    # Already overdue — set to now (immediately due)
                    followup_at = now.isoformat()
                    status = "OVERDUE"
                else:
                    followup_at = due_dt.isoformat()
                    status = "SCHEDULED"

                if not self.dry_run:
                    self.db.conn.execute("""
                        UPDATE pipeline SET next_followup_at = ?, updated_at = ?
                        WHERE prospect_id = ?
                    """, (followup_at, now.isoformat(), prospect_id))
                    self.db.conn.commit()

                results.append({
                    "prospect_id": prospect_id,
                    "name": name,
                    "sent_at": first_sent[:10],
                    "followup_at": followup_at[:10],
                    "status": status,
                })
                log.info(f"Backfill: {name} → {status} (sent {first_sent[:10]}, due {followup_at[:10]})")

            except (ValueError, TypeError) as e:
                log.warning(f"Backfill skipped for {name}: {e}")

        return results

    # ─────────────────────────────────────────────────────────────
    # STATUS — summary of scheduling state
    # ─────────────────────────────────────────────────────────────
    def get_status(self) -> dict:
        """Get a summary of the scheduling state."""
        now = datetime.now()

        # Count by state
        total_active = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM pipeline
            WHERE stage NOT IN ('dead', 'converted')
        """).fetchone()["c"]

        scheduled = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM pipeline
            WHERE next_followup_at IS NOT NULL
              AND stage NOT IN ('dead', 'converted')
        """).fetchone()["c"]

        unscheduled = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM pipeline
            WHERE next_followup_at IS NULL
              AND stage NOT IN ('dead', 'converted', 'new')
        """).fetchone()["c"]

        due_now = len(self.db.get_followup_queue())
        overdue_7d = len(self.db.get_overdue_followups(7))

        # Stage breakdown for active pipeline
        stages = self.db.conn.execute("""
            SELECT stage, COUNT(*) as c FROM pipeline
            WHERE stage NOT IN ('dead', 'converted')
            GROUP BY stage ORDER BY c DESC
        """).fetchall()

        return {
            "total_active": total_active,
            "scheduled": scheduled,
            "unscheduled": unscheduled,
            "due_now": due_now,
            "overdue_7d": overdue_7d,
            "stages": {r["stage"]: r["c"] for r in stages},
        }


# ═══════════════════════════════════════════════════════════════════
# CLI — Interactive Review Mode
# ═══════════════════════════════════════════════════════════════════

def _force_utf8():
    """Force UTF-8 output on Windows."""
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )


def cmd_scan(scheduler: FollowUpScheduler, dry_run: bool):
    """Scan pipeline and show computed follow-up actions."""
    actions = scheduler.scan()

    if not actions:
        print("\n  No follow-up actions needed right now.")
        print("  All prospects are either:")
        print("    - Already scheduled for future follow-up")
        print("    - Converted, dead, or replied")
        return

    print(f"\n  Found {len(actions)} follow-up action(s):\n")
    print(f"  {'Name':<22} {'Current':<14} {'Next':<14} {'Action':<12} Reason")
    print(f"  {'─'*22} {'─'*14} {'─'*14} {'─'*12} {'─'*30}")

    for a in actions:
        name = (a["name"] or "?")[:20]
        print(
            f"  {name:<22} {a['current_stage']:<14} {a['next_stage']:<14} "
            f"{a['action']:<12} {a['reason']}"
        )

    if dry_run:
        print(f"\n  DRY-RUN: No changes made.")
    else:
        print(f"\n  Apply all actions? [y/N]: ", end="")
        try:
            choice = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = "n"

        if choice in ("y", "yes"):
            for a in actions:
                scheduler.apply_action(a)
            print(f"  Applied {len(actions)} action(s).")
        else:
            print(f"  Cancelled.")


def cmd_queue(db: OutreachDB):
    """Show the current follow-up queue."""
    queue = db.get_followup_queue()

    if not queue:
        print("\n  Follow-up queue is empty.")
        print("  Run 'python followup_scheduler.py scan' to compute actions.")
        return

    print(f"\n  Follow-Up Queue ({len(queue)} due now):\n")
    print(f"  {'#':<4} {'Name':<22} {'Stage':<14} {'Score':<6} {'Attempts':<9} Due")
    print(f"  {'─'*4} {'─'*22} {'─'*14} {'─'*6} {'─'*9} {'─'*12}")

    for i, q in enumerate(queue, 1):
        name = (q.get("name") or "?")[:20]
        score = q.get("lead_score") or "—"
        attempts = q.get("followup_count") or 0
        due = (q.get("next_followup_at") or "?")[:10]
        print(f"  {i:<4} {name:<22} {q['stage']:<14} {str(score):<6} {attempts:<9} {due}")


def cmd_review(scheduler: FollowUpScheduler):
    """Interactive review of each follow-up action."""
    actions = scheduler.scan()

    if not actions:
        print("\n  No follow-up actions to review.")
        return

    print(f"\n  Reviewing {len(actions)} follow-up action(s)...\n")
    applied = 0
    skipped = 0

    for i, a in enumerate(actions, 1):
        border = "─" * 55
        print(f"\n  ┌{border}┐")
        print(f"  │  Follow-Up Review #{i}/{len(actions):<36}│")
        print(f"  │{' ' * 55}│")
        print(f"  │  Name:    {(a['name'] or '?'):<44}│")
        print(f"  │  College: {(a.get('college') or '—'):<44}│")
        print(f"  │  Stage:   {a['current_stage']:<16} → {a['next_stage']:<22}│")
        print(f"  │  Action:  {a['action']:<44}│")
        print(f"  │  Reason:  {a['reason'][:44]:<44}│")
        print(f"  │{' ' * 55}│")
        print(f"  │  [A]pply  [S]kip  [Q]uit{' ' * 30}│")
        print(f"  └{border}┘")

        try:
            choice = input("\n    Your choice: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = "q"

        if choice in ("a", "apply", ""):
            scheduler.apply_action(a)
            print(f"    ✓ Applied")
            applied += 1
        elif choice in ("s", "skip"):
            print(f"    ⊘ Skipped")
            skipped += 1
        elif choice in ("q", "quit"):
            print(f"    ■ Quitting review...")
            break

    print(f"\n  Review complete: {applied} applied, {skipped} skipped")


def cmd_status(scheduler: FollowUpScheduler):
    """Show scheduling status summary."""
    status = scheduler.get_status()

    print(f"\n  ┌─ FOLLOW-UP SCHEDULER STATUS ─────────────────────────┐")
    print(f"  │  Active Pipeline:    {status['total_active']:<4}                              │")
    print(f"  │  Scheduled:          {status['scheduled']:<4}                              │")
    print(f"  │  Unscheduled:        {status['unscheduled']:<4}                              │")
    print(f"  │  Due Now:            {status['due_now']:<4}                              │")
    print(f"  │  Overdue (>7d):      {status['overdue_7d']:<4}                              │")
    print(f"  │                                                       │")
    print(f"  │  Active Stages:                                       │")

    for stage, count in status["stages"].items():
        print(f"  │    {stage:<20} {count:>3}                              │")

    print(f"  └───────────────────────────────────────────────────────┘")

    # Cadence rules reference
    print(f"\n  Cadence Rules:")
    print(f"    opener_sent → followup_1   3 days")
    print(f"    followup_1  → followup_2   5 days")
    print(f"    followup_2  → followup_3   7 days")
    print(f"    followup_3  → dead         auto-archive")
    print(f"    deferred    → re_engage    14 days")


def cmd_backfill(scheduler: FollowUpScheduler, dry_run: bool):
    """Backfill initial followup_at for existing prospects."""
    results = scheduler.backfill()

    if not results:
        print("\n  No prospects need backfilling.")
        print("  All opener_sent prospects already have follow-up dates.")
        return

    print(f"\n  Backfill Results ({len(results)} prospects):\n")
    print(f"  {'Name':<22} {'Sent':<12} {'Follow-Up':<12} Status")
    print(f"  {'─'*22} {'─'*12} {'─'*12} {'─'*12}")

    overdue = 0
    scheduled = 0
    for r in results:
        print(f"  {r['name']:<22} {r['sent_at']:<12} {r['followup_at']:<12} {r['status']}")
        if r["status"] == "OVERDUE":
            overdue += 1
        else:
            scheduled += 1

    print(f"\n  Summary: {overdue} overdue (immediately due), {scheduled} scheduled")
    if dry_run:
        print(f"  DRY-RUN: No changes were made.")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    _force_utf8()

    parser = argparse.ArgumentParser(
        description="Outreach OS — Follow-Up Scheduler"
    )
    parser.add_argument(
        "command",
        choices=["scan", "queue", "review", "status", "backfill"],
        help="Command to run",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview actions without making changes",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

    db = OutreachDB()
    scheduler = FollowUpScheduler(db, dry_run=args.dry_run)

    try:
        if args.command == "scan":
            cmd_scan(scheduler, args.dry_run)
        elif args.command == "queue":
            cmd_queue(db)
        elif args.command == "review":
            cmd_review(scheduler)
        elif args.command == "status":
            cmd_status(scheduler)
        elif args.command == "backfill":
            cmd_backfill(scheduler, args.dry_run)
    finally:
        db.close()


if __name__ == "__main__":
    main()
