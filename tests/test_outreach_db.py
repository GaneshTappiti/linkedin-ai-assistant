#!/usr/bin/env python3
"""
Tests for outreach_db.py — SQLite Memory Layer
"""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, date, timedelta

# Ensure we can import from parent
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from outreach_db import (
    OutreachDB, validate_name, normalize_name, normalize_url,
    REJECTED_NAMES,
)


@pytest.fixture
def db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_outreach.db"
    database = OutreachDB(db_path)
    yield database
    database.close()


# ═══════════════════════════════════════════════════════════════════
# NAME VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════

class TestNameValidation:
    def test_valid_names(self):
        assert validate_name("Rachit Jain") is True
        assert validate_name("Ganesh") is True
        assert validate_name("Sai Teja") is True

    def test_rejected_names(self):
        """HARD FAIL on placeholder names — this is the 'there' bug fix."""
        assert validate_name("there") is False
        assert validate_name("There") is False
        assert validate_name("THERE") is False
        assert validate_name("LinkedIn Member") is False
        assert validate_name("linkedin member") is False
        assert validate_name("unknown") is False
        assert validate_name("") is False
        assert validate_name(None) is False
        assert validate_name("   ") is False
        assert validate_name("n/a") is False
        assert validate_name("a") is False  # Single char
        assert validate_name("12345") is False  # Numbers only

    def test_normalize_name_removes_degree(self):
        assert normalize_name("Piyush Kumar • 2nd") == "Piyush Kumar"
        assert normalize_name("RANJAN KUMAR • 2nd") == "RANJAN KUMAR"
        assert normalize_name("Rachit Jain") == "Rachit Jain"

    def test_normalize_url(self):
        assert normalize_url("https://www.linkedin.com/in/rachit/") == "https://www.linkedin.com/in/rachit"
        assert normalize_url("https://www.linkedin.com/in/rachit?foo=bar") == "https://www.linkedin.com/in/rachit"
        assert normalize_url("https://www.linkedin.com/in/rachit/?utm=abc") == "https://www.linkedin.com/in/rachit"


# ═══════════════════════════════════════════════════════════════════
# PROSPECT OPERATIONS
# ═══════════════════════════════════════════════════════════════════

class TestProspects:
    def test_record_and_retrieve(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/testuser",
            name="Test User",
            college="IIT Delhi",
            signal_type="tedx",
            role_fit="Campus Ambassador",
        )
        assert pid > 0

        prospect = db.get_prospect_by_url("https://www.linkedin.com/in/testuser")
        assert prospect is not None
        assert prospect["name"] == "Test User"
        assert prospect["college"] == "IIT Delhi"

    def test_duplicate_detection(self, db):
        db.record_prospect(
            profile_url="https://www.linkedin.com/in/dupe",
            name="Dupe User",
        )
        assert db.is_duplicate("https://www.linkedin.com/in/dupe") is True
        assert db.is_duplicate("https://www.linkedin.com/in/nodupe") is False

    def test_upsert_updates_existing(self, db):
        pid1 = db.record_prospect(
            profile_url="https://www.linkedin.com/in/upsert",
            name="Original Name",
        )
        pid2 = db.record_prospect(
            profile_url="https://www.linkedin.com/in/upsert",
            name="Updated Name",
            college="New College",
        )
        assert pid1 == pid2

        prospect = db.get_prospect_by_url("https://www.linkedin.com/in/upsert")
        assert prospect["name"] == "Updated Name"
        assert prospect["college"] == "New College"

    def test_reject_bad_name(self, db):
        """The 'there' bug — must HARD FAIL."""
        with pytest.raises(ValueError, match="failed identity validation"):
            db.record_prospect(
                profile_url="https://www.linkedin.com/in/badname",
                name="there",
            )

    def test_url_normalization_on_dedup(self, db):
        db.record_prospect(
            profile_url="https://www.linkedin.com/in/normalize/",
            name="Normalized User",
        )
        # Should match even with trailing slash stripped
        assert db.is_duplicate("https://www.linkedin.com/in/normalize") is True
        assert db.is_duplicate("https://www.linkedin.com/in/normalize/?utm=x") is True


# ═══════════════════════════════════════════════════════════════════
# MESSAGE OPERATIONS
# ═══════════════════════════════════════════════════════════════════

class TestMessages:
    def test_record_and_retrieve_messages(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/msguser",
            name="Msg User",
        )
        mid = db.record_message(pid, "outbound", "hey bro, what's up?")
        assert mid > 0

        history = db.get_conversation_history(pid)
        assert len(history) == 1
        assert history[0]["direction"] == "outbound"
        assert history[0]["message_text"] == "hey bro, what's up?"

    def test_has_been_messaged(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/messaged",
            name="Messaged User",
        )
        assert db.has_been_messaged("https://www.linkedin.com/in/messaged") is False

        db.record_message(pid, "outbound", "test message")
        assert db.has_been_messaged("https://www.linkedin.com/in/messaged") is True

    def test_conversation_order(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/convo",
            name="Convo User",
        )
        db.record_message(pid, "outbound", "first")
        db.record_message(pid, "inbound", "second")
        db.record_message(pid, "outbound", "third")

        history = db.get_conversation_history(pid)
        assert len(history) == 3
        assert history[0]["message_text"] == "first"
        assert history[1]["message_text"] == "second"
        assert history[2]["message_text"] == "third"


# ═══════════════════════════════════════════════════════════════════
# DAILY LIMIT ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════

class TestDailyLimits:
    def test_can_send_today_empty(self, db):
        can, remaining = db.can_send_today(15)
        assert can is True
        assert remaining == 15

    def test_daily_count_tracks(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/daily",
            name="Daily User",
        )
        for i in range(5):
            db.record_message(pid, "outbound", f"msg {i}")

        assert db.get_daily_send_count() == 5
        can, remaining = db.can_send_today(15)
        assert can is True
        assert remaining == 10

    def test_daily_limit_enforced(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/limit",
            name="Limit User",
        )
        for i in range(15):
            db.record_message(pid, "outbound", f"msg {i}")

        can, remaining = db.can_send_today(15)
        assert can is False
        assert remaining == 0


# ═══════════════════════════════════════════════════════════════════
# SESSION & CRASH RECOVERY
# ═══════════════════════════════════════════════════════════════════

class TestSessions:
    def test_session_lifecycle(self, db):
        sid = db.start_session("outreach")
        assert sid is not None

        db.end_session(sid, "completed")

        # Verify session is no longer running
        row = db.conn.execute(
            "SELECT status FROM sessions WHERE id = ?", (sid,)
        ).fetchone()
        assert row["status"] == "completed"

    def test_crash_recovery(self, db):
        # Start a session but don't end it (simulates crash)
        sid = db.start_session("outreach")

        # On next startup, recover crashed sessions
        count = db.recover_crashed_sessions()
        assert count == 1

        row = db.conn.execute(
            "SELECT status FROM sessions WHERE id = ?", (sid,)
        ).fetchone()
        assert row["status"] == "crashed"

    def test_checkpoint_save_and_retrieve(self, db):
        sid = db.start_session("outreach")
        db.save_checkpoint(sid, "message_sent", '{"url": "test"}')

        cp = db.get_last_checkpoint(sid)
        assert cp is not None
        assert cp["step"] == "message_sent"
        assert cp["data"] == '{"url": "test"}'


# ═══════════════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════════════

class TestPipeline:
    def test_pipeline_lifecycle(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/pipeline",
            name="Pipeline User",
        )
        db.update_pipeline(pid, "opener_sent")

        # Update to interested
        db.update_pipeline(pid, "interested", sentiment="positive", lead_score=8)

        # Verify
        row = db.conn.execute(
            "SELECT * FROM pipeline WHERE prospect_id = ?", (pid,)
        ).fetchone()
        assert row["stage"] == "interested"
        assert row["sentiment"] == "positive"
        assert row["lead_score"] == 8


# ═══════════════════════════════════════════════════════════════════
# APPROVALS
# ═══════════════════════════════════════════════════════════════════

class TestApprovals:
    def test_approval_queue(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/approval",
            name="Approval User",
        )
        aid = db.create_approval(pid, "hey bro, test message")
        assert aid > 0

        # Approve it
        db.approve_message(aid)
        msg = db.get_approved_message(aid)
        assert msg == "hey bro, test message"

    def test_approval_with_edit(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/edited",
            name="Edited User",
        )
        aid = db.create_approval(pid, "original draft")
        db.approve_message(aid, final_message="edited version")

        msg = db.get_approved_message(aid)
        assert msg == "edited version"

    def test_skip_returns_none(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/skipped",
            name="Skipped User",
        )
        aid = db.create_approval(pid, "this will be skipped")
        db.skip_approval(aid)

        msg = db.get_approved_message(aid)
        assert msg is None


# ═══════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════

class TestStats:
    def test_stats_empty(self, db):
        stats = db.get_stats()
        assert stats["total_prospects"] == 0
        assert stats["total_messaged"] == 0
        assert stats["today_sent"] == 0

    def test_stats_after_activity(self, db):
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/stats",
            name="Stats User",
        )
        db.record_message(pid, "outbound", "test")
        db.update_pipeline(pid, "opener_sent")

        stats = db.get_stats()
        assert stats["total_prospects"] == 1
        assert stats["total_messaged"] == 1
        assert stats["today_sent"] == 1
        assert stats["pipeline"]["opener_sent"] == 1
