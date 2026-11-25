#!/usr/bin/env python3
"""
safety_governor.py — Centralized Safety Enforcement for clstr.in Outreach
=========================================================================
All safety checks in one place. Both outreach and inbox agents import this
module to enforce consistent limits.

Checks are enforced via SQLite — cross-session, cross-restart, persistent.
"""

import random
import logging
from datetime import datetime, timedelta

from outreach_db import OutreachDB

log = logging.getLogger("safety_governor")


class SafetyGovernor:
    """
    Centralized safety layer for LinkedIn outreach automation.

    All limits are enforced via the SQLite database, meaning they persist
    across sessions, restarts, and crashes.
    """

    # ── Hard limits (Phase 1 — calibration period) ────────────────
    MAX_DMS_PER_DAY = 10           # Daily cap across all sessions (was 15)
    MAX_NEW_OPENERS_PER_DAY = 3    # Cold outreach only — highest risk
    MAX_FOLLOWUPS_PER_DAY = 5      # Follow-ups — medium risk
    MAX_INBOX_REPLIES_PER_DAY = 10 # Inbox replies — lowest risk, most natural
    MAX_PER_ROUND = 5              # Per-session cap (was 10)
    COOLDOWN_HOURS = 3             # Min hours between sessions — forces ≤2/day
    SESSION_TIME_LIMIT_MINS = 30   # Soft session time cap
    MIN_DELAY_BETWEEN_DMS = 25     # Seconds (randomized between min/max)
    MAX_DELAY_BETWEEN_DMS = 45     # Seconds

    # ── Random stop ───────────────────────────────────────────────
    # After each message, there's a chance the agent randomly stops.
    # This makes the behavior less predictable to LinkedIn's detection.
    RANDOM_STOP_PROBABILITY = 0.10  # 10% chance per message

    # ── Failure handling ──────────────────────────────────────────
    MAX_RETRIES_PER_PROFILE = 2
    MAX_CONSECUTIVE_FAILURES = 3   # Stop session after 3 failures in a row

    def __init__(self, db: OutreachDB):
        self.db = db
        self._consecutive_failures = 0
        self._session_send_count = 0
        self._session_started_at = datetime.now()

    # ─────────────────────────────────────────────────────────────
    # PRE-SESSION CHECKS
    # ─────────────────────────────────────────────────────────────
    def can_start_session(self, agent_type: str = "outreach") -> tuple[bool, str]:
        """
        Check if a new session can start. Returns (ok, reason).

        Checks:
        1. Daily send limit not reached
        2. Cooldown period has passed since last session
        """
        # Check daily limit
        can_send, remaining = self.db.can_send_today(self.MAX_DMS_PER_DAY)
        if not can_send:
            return False, (
                f"Daily limit reached ({self.MAX_DMS_PER_DAY} messages). "
                f"Try again tomorrow."
            )

        # Check cooldown
        ok, wait_mins = self.check_cooldown(agent_type)
        if not ok:
            return False, (
                f"Cooldown active. Wait {wait_mins:.0f} more minutes before "
                f"starting a new {agent_type} session."
            )

        log.info(
            f"Session pre-check PASSED: {remaining} messages remaining today, "
            f"cooldown clear."
        )
        return True, f"OK — {remaining} messages remaining today"

    def check_cooldown(self, agent_type: str) -> tuple[bool, float]:
        """
        Check if cooldown period has passed since last session.
        Returns (can_run, minutes_remaining).
        """
        last_end = self.db.get_last_session_end(agent_type)
        if last_end is None:
            return True, 0.0

        cooldown_end = last_end + timedelta(hours=self.COOLDOWN_HOURS)
        now = datetime.now()

        if now >= cooldown_end:
            return True, 0.0

        remaining = (cooldown_end - now).total_seconds() / 60
        return False, remaining

    # ─────────────────────────────────────────────────────────────
    # PER-MESSAGE CHECKS
    # ─────────────────────────────────────────────────────────────
    def can_send_message(self) -> tuple[bool, str]:
        """
        Check if we can send another message right now.

        Checks:
        1. Session round limit not reached
        2. Daily limit not reached
        3. Not in failure state
        """
        # Check session limit
        if self._session_send_count >= self.MAX_PER_ROUND:
            return False, (
                f"Session limit reached ({self.MAX_PER_ROUND}/{self.MAX_PER_ROUND}). "
                f"Session complete."
            )

        # Check daily limit
        can_send, remaining = self.db.can_send_today(self.MAX_DMS_PER_DAY)
        if not can_send:
            return False, (
                f"Daily limit reached ({self.MAX_DMS_PER_DAY} messages today)."
            )

        # Check consecutive failures
        if self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            return False, (
                f"Too many consecutive failures ({self._consecutive_failures}). "
                f"Stopping session for safety."
            )

        return True, f"OK — session {self._session_send_count}/{self.MAX_PER_ROUND}, daily {remaining} remaining"

    def record_send_success(self):
        """Record a successful message send."""
        self._session_send_count += 1
        self._consecutive_failures = 0
        log.info(
            f"Send #{self._session_send_count}/{self.MAX_PER_ROUND} recorded"
        )

    def record_failure(self) -> bool:
        """
        Record a failure. Returns True if should continue, False if should stop.
        """
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            log.error(
                f"STOPPING: {self._consecutive_failures} consecutive failures. "
                f"Session will end."
            )
            return False
        log.warning(
            f"Failure #{self._consecutive_failures}/{self.MAX_CONSECUTIVE_FAILURES}"
        )
        return True

    # ─────────────────────────────────────────────────────────────
    # RANDOM STOP (anti-pattern detection)
    # ─────────────────────────────────────────────────────────────
    def should_random_stop(self) -> bool:
        """
        After each message, roll the dice. 10% chance of stopping early.
        Makes the agent's behavior less predictable.
        Only activates after sending at least 3 messages (don't stop too early).
        """
        if self._session_send_count < 3:
            return False
        if random.random() < self.RANDOM_STOP_PROBABILITY:
            log.info(
                f"RANDOM STOP triggered after {self._session_send_count} messages. "
                f"This is intentional anti-detection behavior."
            )
            return True
        return False

    # ─────────────────────────────────────────────────────────────
    # HUMAN-SPEED DELAYS
    # ─────────────────────────────────────────────────────────────
    def get_human_delay(self) -> float:
        """
        Get a random delay between messages (25-45 seconds).
        Uses a slightly non-uniform distribution for realism.
        """
        # Weighted toward the middle of the range for more natural feel
        base = random.uniform(self.MIN_DELAY_BETWEEN_DMS, self.MAX_DELAY_BETWEEN_DMS)
        # Add occasional longer pauses (simulates checking phone, etc.)
        if random.random() < 0.15:
            base += random.uniform(10, 30)
            log.info(f"Extended pause: {base:.0f}s (simulating natural behavior)")
        return base

    def get_typing_delay_ms(self) -> int:
        """Get a random per-character typing delay in milliseconds (30-80ms)."""
        return random.randint(30, 80)

    # ─────────────────────────────────────────────────────────────
    # PHASE 1 — SEPARATED RISK CHECKS
    # ─────────────────────────────────────────────────────────────
    def can_send_new_opener(self) -> tuple[bool, str]:
        """
        Check if we can send a NEW cold outreach message today.
        Cold openers are highest risk — strictest limit.
        """
        sent = self.db.get_daily_opener_count()
        remaining = max(0, self.MAX_NEW_OPENERS_PER_DAY - sent)
        if remaining <= 0:
            return False, f"New opener limit reached ({self.MAX_NEW_OPENERS_PER_DAY}/day)"
        return True, f"{remaining} new openers remaining today"

    def can_send_followup(self) -> tuple[bool, str]:
        """
        Check if we can send a follow-up message today.
        Follow-ups are medium risk — moderate limit.
        """
        sent = self.db.get_daily_followup_count()
        remaining = max(0, self.MAX_FOLLOWUPS_PER_DAY - sent)
        if remaining <= 0:
            return False, f"Follow-up limit reached ({self.MAX_FOLLOWUPS_PER_DAY}/day)"
        return True, f"{remaining} follow-ups remaining today"

    def check_session_time(self) -> tuple[bool, float]:
        """
        Check if the session has exceeded the soft time limit.
        Returns (is_within_limit, minutes_elapsed).
        """
        elapsed = (datetime.now() - self._session_started_at).total_seconds() / 60
        if elapsed >= self.SESSION_TIME_LIMIT_MINS:
            log.warning(
                f"Session time limit reached: {elapsed:.0f}m / {self.SESSION_TIME_LIMIT_MINS}m. "
                f"Consider stopping to maintain natural behavior."
            )
            return False, elapsed
        return True, elapsed

    # ─────────────────────────────────────────────────────────────
    # STATUS REPORTING
    # ─────────────────────────────────────────────────────────────
    def get_status(self) -> dict:
        """Get current safety status."""
        can_send, remaining = self.db.can_send_today(self.MAX_DMS_PER_DAY)
        within_time, elapsed_mins = self.check_session_time()
        return {
            "session_sent": self._session_send_count,
            "session_limit": self.MAX_PER_ROUND,
            "daily_remaining": remaining,
            "daily_limit": self.MAX_DMS_PER_DAY,
            "consecutive_failures": self._consecutive_failures,
            "can_send": can_send and self._session_send_count < self.MAX_PER_ROUND,
            "session_minutes": round(elapsed_mins, 1),
            "session_time_ok": within_time,
        }

    def get_phase1_status(self) -> dict:
        """Get Phase 1 specific metrics with separated risk levels."""
        opener_ok, opener_msg = self.can_send_new_opener()
        followup_ok, followup_msg = self.can_send_followup()
        within_time, elapsed = self.check_session_time()
        can_send, daily_remaining = self.db.can_send_today(self.MAX_DMS_PER_DAY)

        return {
            "openers_sent_today": self.db.get_daily_opener_count(),
            "openers_limit": self.MAX_NEW_OPENERS_PER_DAY,
            "openers_ok": opener_ok,
            "followups_sent_today": self.db.get_daily_followup_count(),
            "followups_limit": self.MAX_FOLLOWUPS_PER_DAY,
            "followups_ok": followup_ok,
            "daily_total": self.MAX_DMS_PER_DAY - daily_remaining,
            "daily_limit": self.MAX_DMS_PER_DAY,
            "session_minutes": round(elapsed, 1),
            "session_time_limit": self.SESSION_TIME_LIMIT_MINS,
            "session_time_ok": within_time,
        }

    def print_status(self):
        """Print a formatted status summary."""
        s = self.get_status()
        log.info(
            f"Safety Status: "
            f"Session {s['session_sent']}/{s['session_limit']} | "
            f"Daily {s['daily_limit'] - s['daily_remaining']}/{s['daily_limit']} | "
            f"Failures {s['consecutive_failures']}/{self.MAX_CONSECUTIVE_FAILURES} | "
            f"Time {s['session_minutes']}m/{self.SESSION_TIME_LIMIT_MINS}m | "
            f"Can send: {s['can_send']}"
        )
