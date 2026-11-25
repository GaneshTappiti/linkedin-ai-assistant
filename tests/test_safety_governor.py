#!/usr/bin/env python3
"""
Tests for safety_governor.py — Safety Enforcement
"""

import os
import pytest
import sys
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from outreach_db import OutreachDB
from safety_governor import SafetyGovernor


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test_safety.db"
    database = OutreachDB(db_path)
    yield database
    database.close()


@pytest.fixture
def gov(db):
    return SafetyGovernor(db)


class TestSessionStart:
    def test_can_start_fresh(self, gov):
        ok, reason = gov.can_start_session("outreach")
        assert ok is True
        assert "OK" in reason

    def test_blocked_by_daily_limit(self, db, gov):
        """Fill up the daily limit, then verify session is blocked."""
        pid = db.record_prospect(
            profile_url="https://www.linkedin.com/in/limit",
            name="Limit User",
        )
        for i in range(10):
            db.record_message(pid, "outbound", f"msg {i}")

        ok, reason = gov.can_start_session("outreach")
        assert ok is False
        assert "Daily limit" in reason

    def test_cooldown_check(self, db, gov):
        """After a session ends, cooldown should block immediate restart."""
        sid = db.start_session("outreach")
        db.end_session(sid, "completed")

        ok, reason = gov.can_start_session("outreach")
        assert ok is False
        assert "Cooldown" in reason or "Wait" in reason


class TestMessageSafety:
    def test_can_send_initially(self, gov):
        ok, reason = gov.can_send_message()
        assert ok is True

    def test_session_limit_enforced(self, gov):
        """After MAX_PER_ROUND sends, should block."""
        for i in range(5):
            gov.record_send_success()

        ok, reason = gov.can_send_message()
        assert ok is False
        assert "Session limit" in reason

    def test_consecutive_failure_stop(self, gov):
        """After MAX_CONSECUTIVE_FAILURES, should stop."""
        for i in range(3):
            can_continue = gov.record_failure()

        assert can_continue is False

        ok, reason = gov.can_send_message()
        assert ok is False
        assert "failures" in reason.lower()

    def test_failure_reset_on_success(self, gov):
        gov.record_failure()
        gov.record_failure()
        gov.record_send_success()  # Should reset counter

        ok, _ = gov.can_send_message()
        assert ok is True


class TestRandomStop:
    def test_no_stop_before_3_messages(self, gov):
        """Random stop should never trigger before 3 messages."""
        for _ in range(100):
            assert gov.should_random_stop() is False

    def test_random_stop_possible_after_3(self, gov):
        """After 3 messages, random stop should be possible."""
        gov._session_send_count = 5
        results = [gov.should_random_stop() for _ in range(1000)]
        # With 10% probability, at least some should be True in 1000 tries
        assert any(results)
        # But most should be False
        assert sum(results) < 200  # Roughly 10% ± margin


class TestDelays:
    def test_human_delay_range(self, gov):
        for _ in range(50):
            d = gov.get_human_delay()
            assert d >= gov.MIN_DELAY_BETWEEN_DMS
            # Max is MIN + possible extended pause (up to 30s extra)
            assert d <= gov.MAX_DELAY_BETWEEN_DMS + 30

    def test_typing_delay_range(self, gov):
        for _ in range(50):
            d = gov.get_typing_delay_ms()
            assert 30 <= d <= 80


class TestStatus:
    def test_status_reporting(self, gov):
        status = gov.get_status()
        assert status["session_sent"] == 0
        assert status["session_limit"] == 5
        assert status["can_send"] is True

        gov.record_send_success()
        status = gov.get_status()
        assert status["session_sent"] == 1


class TestPhase1Checks:
    def test_can_send_new_opener(self, gov):
        ok, msg = gov.can_send_new_opener()
        assert ok is True
        assert "remaining today" in msg

    def test_can_send_followup(self, gov):
        ok, msg = gov.can_send_followup()
        assert ok is True
        assert "remaining today" in msg

    def test_check_session_time(self, gov):
        ok, elapsed = gov.check_session_time()
        assert ok is True
        assert elapsed >= 0.0

        # Simulate old session
        gov._session_started_at = datetime.now() - timedelta(minutes=45)
        ok, elapsed = gov.check_session_time()
        assert ok is False
        assert elapsed >= 45.0

    def test_phase1_status(self, gov):
        status = gov.get_phase1_status()
        assert status["openers_ok"] is True
        assert status["followups_ok"] is True
        assert status["session_time_ok"] is True
        assert status["daily_limit"] == 10
        assert status["openers_limit"] == 3
        assert status["followups_limit"] == 5
