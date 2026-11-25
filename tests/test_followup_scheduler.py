#!/usr/bin/env python3
"""
tests/test_followup_scheduler.py — Tests for the Follow-Up Scheduler
=====================================================================
Tests cadence rules, stage transitions, backfill logic, queue priority,
auto-archival, and overdue detection.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from outreach_db import OutreachDB, VALID_STAGES
from followup_scheduler import FollowUpScheduler, CadenceRules


@pytest.fixture
def db(tmp_path):
    """Create a temporary test DB."""
    db_path = tmp_path / "test_scheduler.db"
    return OutreachDB(db_path)


@pytest.fixture
def scheduler(db):
    """Create a scheduler with test DB (dry_run=False)."""
    return FollowUpScheduler(db, dry_run=False)


@pytest.fixture
def scheduler_dry(db):
    """Create a scheduler with test DB (dry_run=True)."""
    return FollowUpScheduler(db, dry_run=True)


def _create_prospect(db, name="Test User", url_suffix="test", stage="opener_sent",
                     days_ago_sent=5, next_followup_at=None):
    """Helper: create a prospect with a pipeline entry and a backdated message."""
    pid = db.record_prospect(
        profile_url=f"https://linkedin.com/in/{url_suffix}",
        name=name,
        college="Test College",
    )
    db.update_pipeline(pid, stage, next_followup_at=next_followup_at)

    # Insert a backdated outbound message
    sent_at = (datetime.now() - timedelta(days=days_ago_sent)).isoformat()
    db.conn.execute("""
        INSERT INTO messages (prospect_id, direction, message_text, sent_at)
        VALUES (?, 'outbound', 'Hey test message', ?)
    """, (pid, sent_at))
    db.conn.commit()

    return pid


# ═══════════════════════════════════════════════════════════════════
# CADENCE RULES
# ═══════════════════════════════════════════════════════════════════

class TestCadenceRules:
    """Test the cadence rule definitions."""

    def test_opener_sent_transition(self):
        result = CadenceRules.get_no_reply_transition("opener_sent")
        assert result == (3, "followup_1")

    def test_followup_1_transition(self):
        result = CadenceRules.get_no_reply_transition("followup_1")
        assert result == (5, "followup_2")

    def test_followup_2_transition(self):
        result = CadenceRules.get_no_reply_transition("followup_2")
        assert result == (7, "followup_3")

    def test_followup_3_archives(self):
        result = CadenceRules.get_no_reply_transition("followup_3")
        assert result == (0, "dead")

    def test_no_transition_for_dead(self):
        result = CadenceRules.get_no_reply_transition("dead")
        assert result is None

    def test_no_transition_for_converted(self):
        result = CadenceRules.get_no_reply_transition("converted")
        assert result is None

    def test_all_cadence_stages_are_valid(self):
        for stage in CadenceRules.NO_REPLY_CADENCE:
            assert stage in VALID_STAGES
        for _, next_stage in CadenceRules.NO_REPLY_CADENCE.values():
            assert next_stage in VALID_STAGES


# ═══════════════════════════════════════════════════════════════════
# SCAN
# ═══════════════════════════════════════════════════════════════════

class TestScan:
    """Test the scan command logic."""

    def test_scan_finds_overdue_openers(self, db, scheduler):
        """Should find opener_sent prospects overdue for follow-up."""
        _create_prospect(db, name="Overdue User", url_suffix="overdue", days_ago_sent=5)
        actions = scheduler.scan()
        assert len(actions) == 1
        assert actions[0]["current_stage"] == "opener_sent"
        assert actions[0]["next_stage"] == "followup_1"
        assert actions[0]["action"] == "schedule_followup"

    def test_scan_skips_future_followups(self, db, scheduler):
        """Should skip prospects with future follow-up dates."""
        future = (datetime.now() + timedelta(days=2)).isoformat()
        _create_prospect(
            db, name="Future User", url_suffix="future",
            days_ago_sent=1, next_followup_at=future,
        )
        actions = scheduler.scan()
        assert len(actions) == 0

    def test_scan_skips_replied_prospects(self, db, scheduler):
        """Should skip prospects who have replied."""
        pid = _create_prospect(db, name="Replied User", url_suffix="replied", days_ago_sent=5)
        # Add an inbound reply
        db.record_message(pid, "inbound", "Hey, interested!")
        actions = scheduler.scan()
        assert len(actions) == 0

    def test_scan_handles_past_due_followup(self, db, scheduler):
        """Should act on past-due scheduled followups."""
        past = (datetime.now() - timedelta(days=2)).isoformat()
        _create_prospect(
            db, name="Past Due", url_suffix="pastdue",
            days_ago_sent=10, next_followup_at=past,
        )
        actions = scheduler.scan()
        assert len(actions) == 1
        assert actions[0]["action"] == "schedule_followup"

    def test_scan_empty_pipeline(self, db, scheduler):
        """Should return empty list for empty pipeline."""
        actions = scheduler.scan()
        assert actions == []


# ═══════════════════════════════════════════════════════════════════
# APPLY ACTIONS
# ═══════════════════════════════════════════════════════════════════

class TestApplyActions:
    """Test applying follow-up actions."""

    def test_apply_schedule_followup(self, db, scheduler):
        """Applying a schedule_followup should advance the pipeline stage."""
        pid = _create_prospect(db, name="Advance User", url_suffix="advance", days_ago_sent=5)
        actions = scheduler.scan()
        assert len(actions) == 1

        scheduler.apply_action(actions[0])

        # Verify stage changed
        row = db.conn.execute(
            "SELECT stage, followup_count, next_followup_at FROM pipeline WHERE prospect_id = ?",
            (pid,)
        ).fetchone()
        assert row["stage"] == "followup_1"
        assert row["followup_count"] == 1
        assert row["next_followup_at"] is not None  # Should have next followup scheduled

    def test_apply_archive(self, db, scheduler):
        """Applying an archive action should set stage to dead."""
        pid = _create_prospect(
            db, name="Archive User", url_suffix="archive",
            stage="followup_3", days_ago_sent=20,
        )
        # Set a past-due followup
        past = (datetime.now() - timedelta(days=1)).isoformat()
        db.conn.execute(
            "UPDATE pipeline SET next_followup_at = ? WHERE prospect_id = ?",
            (past, pid)
        )
        db.conn.commit()

        actions = scheduler.scan()
        archive_actions = [a for a in actions if a["action"] == "archive"]
        assert len(archive_actions) == 1

        scheduler.apply_action(archive_actions[0])

        row = db.conn.execute(
            "SELECT stage FROM pipeline WHERE prospect_id = ?", (pid,)
        ).fetchone()
        assert row["stage"] == "dead"

    def test_dry_run_no_changes(self, db, scheduler_dry):
        """Dry-run should not modify the database."""
        pid = _create_prospect(
            db, name="DryRun User", url_suffix="dryrun", days_ago_sent=5,
        )
        actions = scheduler_dry.scan()
        assert len(actions) == 1

        scheduler_dry.apply_action(actions[0])

        # Stage should NOT have changed
        row = db.conn.execute(
            "SELECT stage FROM pipeline WHERE prospect_id = ?", (pid,)
        ).fetchone()
        assert row["stage"] == "opener_sent"


# ═══════════════════════════════════════════════════════════════════
# BACKFILL
# ═══════════════════════════════════════════════════════════════════

class TestBackfill:
    """Test backfill logic for existing data."""

    def test_backfill_sets_followup_dates(self, db, scheduler):
        """Backfill should set next_followup_at for unscheduled opener_sent."""
        _create_prospect(db, name="Backfill User", url_suffix="backfill", days_ago_sent=5)
        results = scheduler.backfill()

        assert len(results) == 1
        assert results[0]["status"] == "OVERDUE"

        # Verify DB was updated
        row = db.conn.execute(
            "SELECT next_followup_at FROM pipeline WHERE prospect_id = ?",
            (results[0]["prospect_id"],)
        ).fetchone()
        assert row["next_followup_at"] is not None

    def test_backfill_skips_already_scheduled(self, db, scheduler):
        """Backfill should skip prospects that already have follow-up dates."""
        future = (datetime.now() + timedelta(days=2)).isoformat()
        _create_prospect(
            db, name="Scheduled User", url_suffix="scheduled",
            days_ago_sent=5, next_followup_at=future,
        )
        results = scheduler.backfill()
        assert len(results) == 0

    def test_backfill_dry_run(self, db, scheduler_dry):
        """Dry-run backfill should not modify DB."""
        pid = _create_prospect(
            db, name="DryBackfill User", url_suffix="dryback", days_ago_sent=5,
        )
        results = scheduler_dry.backfill()
        assert len(results) == 1

        # DB should NOT be updated
        row = db.conn.execute(
            "SELECT next_followup_at FROM pipeline WHERE prospect_id = ?", (pid,)
        ).fetchone()
        assert row["next_followup_at"] is None

    def test_backfill_recent_not_overdue(self, db, scheduler):
        """Prospect sent 1 day ago should be scheduled but NOT overdue (3-day cadence)."""
        _create_prospect(
            db, name="Recent User", url_suffix="recent", days_ago_sent=1,
        )
        results = scheduler.backfill()
        # Should be scheduled as SCHEDULED (not OVERDUE) since due date is 2 days away
        assert len(results) == 1
        assert results[0]["status"] == "SCHEDULED"


# ═══════════════════════════════════════════════════════════════════
# QUEUE & OVERDUE
# ═══════════════════════════════════════════════════════════════════

class TestQueueAndOverdue:
    """Test queue ordering and overdue detection."""

    def test_queue_priority_by_lead_score(self, db):
        """Higher lead score should appear first in queue."""
        pid1 = _create_prospect(db, name="Low Score", url_suffix="low", days_ago_sent=5)
        pid2 = _create_prospect(db, name="High Score", url_suffix="high", days_ago_sent=5)

        now = datetime.now().isoformat()
        db.update_pipeline(pid1, "opener_sent", lead_score=30, next_followup_at=now)
        db.update_pipeline(pid2, "opener_sent", lead_score=90, next_followup_at=now)

        queue = db.get_followup_queue()
        assert len(queue) == 2
        assert queue[0]["name"] == "High Score"
        assert queue[1]["name"] == "Low Score"

    def test_overdue_detection(self, db):
        """Should detect follow-ups overdue by N days."""
        pid = _create_prospect(db, name="Overdue", url_suffix="overdue7", days_ago_sent=20)
        ten_days_ago = (datetime.now() - timedelta(days=10)).isoformat()
        db.update_pipeline(pid, "opener_sent", next_followup_at=ten_days_ago)

        overdue = db.get_overdue_followups(7)
        assert len(overdue) == 1
        assert overdue[0]["name"] == "Overdue"

    def test_not_overdue_within_window(self, db):
        """Should not flag follow-ups within the acceptable window."""
        pid = _create_prospect(db, name="Recent", url_suffix="recent7", days_ago_sent=5)
        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        db.update_pipeline(pid, "opener_sent", next_followup_at=two_days_ago)

        overdue = db.get_overdue_followups(7)
        assert len(overdue) == 0


# ═══════════════════════════════════════════════════════════════════
# STAGE TRANSITIONS
# ═══════════════════════════════════════════════════════════════════

class TestStageTransitions:
    """Test advance_pipeline_stage and related DB methods."""

    def test_advance_stage_increments_count(self, db):
        """Should increment followup_count on each advance."""
        pid = _create_prospect(db, name="Counter", url_suffix="counter", days_ago_sent=5)
        db.advance_pipeline_stage(pid, "followup_1")

        row = db.conn.execute(
            "SELECT followup_count, last_followup_stage FROM pipeline WHERE prospect_id = ?",
            (pid,)
        ).fetchone()
        assert row["followup_count"] == 1
        assert row["last_followup_stage"] == "opener_sent"

    def test_double_advance(self, db):
        """Two advances should result in count=2."""
        pid = _create_prospect(db, name="Double", url_suffix="double", days_ago_sent=10)
        db.advance_pipeline_stage(pid, "followup_1")
        db.advance_pipeline_stage(pid, "followup_2")

        row = db.conn.execute(
            "SELECT stage, followup_count, last_followup_stage FROM pipeline WHERE prospect_id = ?",
            (pid,)
        ).fetchone()
        assert row["stage"] == "followup_2"
        assert row["followup_count"] == 2
        assert row["last_followup_stage"] == "followup_1"

    def test_invalid_stage_raises(self, db):
        """Should raise ValueError for invalid stage."""
        pid = _create_prospect(db, name="Invalid", url_suffix="invalid", days_ago_sent=5)
        with pytest.raises(ValueError, match="Invalid stage"):
            db.advance_pipeline_stage(pid, "nonexistent_stage")

    def test_schedule_followup_sets_date(self, db):
        """schedule_followup should set future date."""
        pid = _create_prospect(db, name="Schedule", url_suffix="schedule", days_ago_sent=5)
        db.schedule_followup(pid, delay_days=3)

        row = db.conn.execute(
            "SELECT next_followup_at FROM pipeline WHERE prospect_id = ?", (pid,)
        ).fetchone()
        assert row["next_followup_at"] is not None

        followup_dt = datetime.fromisoformat(row["next_followup_at"])
        # Should be approximately 3 days from now
        assert (followup_dt - datetime.now()).days in (2, 3)

    def test_archive_stale_prospects(self, db):
        """Should auto-archive prospects exceeding max attempts."""
        pid = _create_prospect(db, name="Stale", url_suffix="stale", days_ago_sent=30)
        # Simulate 3 follow-ups
        db.advance_pipeline_stage(pid, "followup_1")
        db.advance_pipeline_stage(pid, "followup_2")
        db.advance_pipeline_stage(pid, "followup_3")

        archived = db.archive_stale_prospects(max_attempts=3)
        assert archived == 1

        row = db.conn.execute(
            "SELECT stage FROM pipeline WHERE prospect_id = ?", (pid,)
        ).fetchone()
        assert row["stage"] == "dead"

    def test_relationship_age(self, db):
        """Should return days since first contact."""
        pid = _create_prospect(db, name="Old Friend", url_suffix="old", days_ago_sent=10)
        age = db.get_relationship_age(pid)
        assert age == 10

    def test_relationship_age_no_contact(self, db):
        """Should return None if never contacted."""
        pid = db.record_prospect(
            profile_url="https://linkedin.com/in/nocontact",
            name="No Contact",
        )
        age = db.get_relationship_age(pid)
        assert age is None


# ═══════════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════════

class TestStatus:
    """Test the get_status method."""

    def test_status_empty_db(self, db, scheduler):
        status = scheduler.get_status()
        assert status["total_active"] == 0
        assert status["scheduled"] == 0
        assert status["unscheduled"] == 0
        assert status["due_now"] == 0

    def test_status_with_data(self, db, scheduler):
        _create_prospect(db, name="Status User", url_suffix="status", days_ago_sent=5)
        status = scheduler.get_status()
        assert status["total_active"] == 1
        assert status["unscheduled"] == 1
        assert "opener_sent" in status["stages"]
