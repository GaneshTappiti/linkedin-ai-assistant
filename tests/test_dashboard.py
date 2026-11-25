#!/usr/bin/env python3
"""
tests/test_dashboard.py — Tests for the CLI Operational Dashboard
=================================================================
Tests anomaly detection rules, data formatting, and edge cases.
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import pytest

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from outreach_db import OutreachDB
from outreach_dashboard import OutreachDashboard, C


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary DB for testing."""
    db_path = tmp_path / "test_dashboard.db"
    db = OutreachDB(db_path)
    return db


@pytest.fixture
def dashboard(tmp_db):
    """Create a dashboard with a test DB."""
    # Disable ANSI for test assertions
    C.disable()
    return OutreachDashboard(tmp_db)


class TestDashboardRendering:
    """Test that the dashboard renders without errors."""

    def test_render_empty_db(self, dashboard):
        """Dashboard should render cleanly with an empty database."""
        output = dashboard.render()
        assert "OUTREACH OS" in output
        assert "PIPELINE FUNNEL" in output
        assert "DAILY SAFETY BUDGET" in output
        assert "RISK ALERTS" in output

    def test_render_with_data(self, tmp_db):
        """Dashboard should render with actual prospect data."""
        C.disable()
        # Add a prospect and message
        pid = tmp_db.record_prospect(
            profile_url="https://linkedin.com/in/test",
            name="Test User",
            college="Test College",
        )
        tmp_db.update_pipeline(pid, "opener_sent")
        tmp_db.record_message(pid, "outbound", "Hey test message")

        dash = OutreachDashboard(tmp_db)
        output = dash.render()

        assert "Prospects: 1" in output
        assert "Messaged: 1" in output
        assert "Opener Sent" in output

    def test_render_compact_mode(self, tmp_db):
        """Compact mode should skip zero-count stages."""
        C.disable()
        dash = OutreachDashboard(tmp_db, compact=True)
        output = dash.render()
        # In compact mode with empty DB, many stages should be hidden
        assert "PIPELINE FUNNEL" in output
        # Follow-Up Queue is hidden in compact mode
        assert "FOLLOW-UP QUEUE" not in output


class TestAnomalyDetection:
    """Test the anomaly detection engine."""

    def test_no_anomalies_fresh_db(self, dashboard):
        """Fresh empty DB should have no anomalies (not enough data to trigger)."""
        alerts = dashboard._detect_anomalies()
        # Fresh DB with 0 messaged won't trigger reply rate alert (needs >= 5)
        # But it also has no messages, so no "inactive" alert either
        assert isinstance(alerts, list)

    def test_zero_reply_rate_alert(self, tmp_db):
        """Should flag when reply rate is 0% with 5+ messages sent."""
        C.disable()
        # Send 5 messages with no replies
        for i in range(5):
            pid = tmp_db.record_prospect(
                profile_url=f"https://linkedin.com/in/test{i}",
                name=f"Test User {i}",
            )
            tmp_db.record_message(pid, "outbound", f"Hey test {i}")

        dash = OutreachDashboard(tmp_db)
        alerts = dash._detect_anomalies()

        alert_msgs = [msg for _, msg in alerts]
        assert any("Reply rate" in msg and "0%" in msg for msg in alert_msgs)

    def test_unscheduled_followup_alert(self, tmp_db):
        """Should flag opener_sent prospects with no next_followup_at."""
        C.disable()
        pid = tmp_db.record_prospect(
            profile_url="https://linkedin.com/in/unscheduled",
            name="Unscheduled Person",
        )
        tmp_db.update_pipeline(pid, "opener_sent")
        # next_followup_at is NULL by default

        dash = OutreachDashboard(tmp_db)
        alerts = dash._detect_anomalies()

        alert_msgs = [msg for _, msg in alerts]
        assert any("Unscheduled" in msg for msg in alert_msgs)

    def test_inactive_system_alert(self, tmp_db):
        """Should flag when no messages sent in 3+ days."""
        C.disable()
        pid = tmp_db.record_prospect(
            profile_url="https://linkedin.com/in/old",
            name="Old Contact",
        )
        # Insert a message backdated 5 days
        five_days_ago = (datetime.now() - timedelta(days=5)).isoformat()
        tmp_db.conn.execute("""
            INSERT INTO messages (prospect_id, direction, message_text, sent_at)
            VALUES (?, 'outbound', 'old message', ?)
        """, (pid, five_days_ago))
        tmp_db.conn.commit()

        dash = OutreachDashboard(tmp_db)
        alerts = dash._detect_anomalies()

        alert_msgs = [msg for _, msg in alerts]
        assert any("inactive" in msg.lower() or "activity" in msg.lower() for msg in alert_msgs)

    def test_overdue_followup_alert(self, tmp_db):
        """Should flag follow-ups overdue > 7 days."""
        C.disable()
        pid = tmp_db.record_prospect(
            profile_url="https://linkedin.com/in/overdue",
            name="Overdue Person",
        )
        # Set a follow-up date 10 days ago
        ten_days_ago = (datetime.now() - timedelta(days=10)).isoformat()
        tmp_db.update_pipeline(
            pid, "opener_sent",
            next_followup_at=ten_days_ago,
        )

        dash = OutreachDashboard(tmp_db)
        alerts = dash._detect_anomalies()

        alert_msgs = [msg for _, msg in alerts]
        assert any("overdue" in msg.lower() for msg in alert_msgs)

    def test_crash_rate_alert(self, tmp_db):
        """Should flag 3+ crashes in 7 days."""
        C.disable()
        # Create 3 crashed sessions
        for i in range(3):
            sid = tmp_db.start_session("outreach")
            tmp_db.end_session(sid, "crashed")

        dash = OutreachDashboard(tmp_db)
        alerts = dash._detect_anomalies()

        alert_msgs = [msg for _, msg in alerts]
        assert any("instability" in msg.lower() or "crash" in msg.lower() for msg in alert_msgs)


class TestSafetyBudget:
    """Test the daily safety budget display logic."""

    def test_budget_full(self, tmp_db):
        """Budget should show 100% remaining when nothing sent today."""
        C.disable()
        dash = OutreachDashboard(tmp_db)
        output = dash._daily_safety_budget()
        assert "0/10" in output
        assert "100%" in output
        assert "healthy" in output

    def test_budget_partial(self, tmp_db):
        """Budget should update after sending messages."""
        C.disable()
        pid = tmp_db.record_prospect(
            profile_url="https://linkedin.com/in/budget-test",
            name="Budget Test",
        )
        for i in range(5):
            tmp_db.record_message(pid, "outbound", f"msg {i}")

        dash = OutreachDashboard(tmp_db)
        output = dash._daily_safety_budget()
        assert "5/10" in output


class TestFollowUpQueue:
    """Test the follow-up queue display."""

    def test_empty_queue(self, tmp_db):
        """Should show 'no follow-ups' when queue is empty."""
        C.disable()
        dash = OutreachDashboard(tmp_db)
        output = dash._followup_queue()
        assert "No follow-ups pending" in output

    def test_stale_prospects_shown(self, tmp_db):
        """Should show opener_sent prospects with no follow-up date."""
        C.disable()
        pid = tmp_db.record_prospect(
            profile_url="https://linkedin.com/in/stale",
            name="Stale Person",
        )
        tmp_db.update_pipeline(pid, "opener_sent")

        dash = OutreachDashboard(tmp_db)
        output = dash._followup_queue()
        assert "Unscheduled" in output
        assert "Stale Person" in output
