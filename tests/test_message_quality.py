#!/usr/bin/env python3
"""
tests/test_message_quality.py — Tests for Message Quality Scoring
=================================================================
Comprehensive tests for the pre-send quality scoring trust layer.
"""

import sys
import sqlite3
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from message_quality import MessageScorer, MessageScore, MIN_QUALITY_SCORE, MAX_RISK_SCORE


class TestMessageScorerBase(unittest.TestCase):
    """Base class with shared test fixtures."""

    def setUp(self):
        """Create an in-memory DB for testing."""
        self.db = MagicMock()
        # Default: no recent messages (empty similarity cache)
        self.db.conn = sqlite3.connect(":memory:")
        self.db.conn.row_factory = sqlite3.Row
        self.db.conn.execute("""
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY,
                prospect_id INTEGER,
                direction TEXT,
                message_text TEXT,
                sent_at TEXT,
                session_id TEXT,
                approved_by TEXT
            )
        """)
        self.db.conn.execute("""
            CREATE TABLE prospects (
                id INTEGER PRIMARY KEY,
                profile_url TEXT,
                name TEXT,
                college TEXT,
                signal_type TEXT,
                headline TEXT
            )
        """)
        self.scorer = MessageScorer(self.db)

    def tearDown(self):
        self.db.conn.close()

    def _insert_message(self, text: str, days_ago: int = 0):
        """Helper: insert an outbound message into the test DB."""
        sent_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        self.db.conn.execute(
            "INSERT INTO messages (prospect_id, direction, message_text, sent_at) VALUES (?, ?, ?, ?)",
            (1, "outbound", text, sent_at)
        )
        self.db.conn.commit()
        # Invalidate cache
        self.scorer.invalidate_cache()


# ═══════════════════════════════════════════════════════════════════
# QUALITY SCORING TESTS
# ═══════════════════════════════════════════════════════════════════

class TestQualityScoring(TestMessageScorerBase):
    """Tests for the quality score dimension."""

    def test_good_opener_scores_high(self):
        """A well-crafted opener should score above threshold."""
        msg = "hey priya, saw your TEDx work at VIT. how do you keep students engaged after the event ends?"
        score = self.scorer.score_message(msg, name="Priya", college="VIT", signal_type="tedx")
        self.assertGreaterEqual(score.quality_score, MIN_QUALITY_SCORE)

    def test_empty_message_scores_zero(self):
        """Empty message should get zero quality."""
        score = self.scorer.score_message("")
        self.assertEqual(score.quality_score, 0.0)

    def test_whitespace_only_scores_zero(self):
        """Whitespace-only message should get zero quality."""
        score = self.scorer.score_message("   \n\t  ")
        self.assertEqual(score.quality_score, 0.0)

    def test_very_short_message_scores_lower(self):
        """Very short messages should score lower."""
        score = self.scorer.score_message("hey")
        self.assertLess(score.quality_score, 0.5)

    def test_very_long_message_scores_lower(self):
        """Excessively long messages should score lower."""
        msg = "hey bro, " + "this is a really long message that goes on and on " * 20
        score = self.scorer.score_message(msg)
        self.assertLess(score.quality_score, 0.8)

    def test_question_mark_boosts_quality(self):
        """Messages with a question should score higher."""
        with_q = "hey priya, saw your work at VIT. what's the vibe there like?"
        without_q = "hey priya, saw your work at VIT. looks really interesting."
        score_q = self.scorer.score_message(with_q, name="Priya", college="VIT")
        score_no_q = self.scorer.score_message(without_q, name="Priya", college="VIT")
        self.assertGreater(score_q.quality_score, score_no_q.quality_score)

    def test_casual_lowercase_scores_higher(self):
        """Ganesh's casual lowercase style should score higher than formal."""
        casual = "hey priya, saw your TEDx work at VIT. how do you keep students engaged?"
        formal = "Dear Priya, I noticed your TEDx work at VIT. How do you keep students engaged?"
        score_casual = self.scorer.score_message(casual, name="Priya", college="VIT")
        score_formal = self.scorer.score_message(formal, name="Priya", college="VIT")
        self.assertGreater(score_casual.quality_score, score_formal.quality_score)

    def test_template_leak_kills_quality(self):
        """Unreplaced template variables should tank quality."""
        msg = "hey {name}, saw your work at {college}. what's the vibe?"
        score = self.scorer.score_message(msg)
        self.assertLess(score.quality_score, 0.8)

    def test_corporate_opening_scores_lower(self):
        """Corporate openings like 'Dear' should reduce quality."""
        msg = "Dear Sir, I would like to discuss an opportunity with you. Please respond."
        score = self.scorer.score_message(msg)
        self.assertLess(score.quality_score, 0.6)

    def test_natural_hey_opening_scores_well(self):
        """Natural 'hey' opening should score well."""
        msg = "hey raj, saw your event work at BITS. what kind of events get real participation?"
        score = self.scorer.score_message(msg, name="Raj", college="BITS")
        self.assertGreaterEqual(score.quality_score, 0.7)


# ═══════════════════════════════════════════════════════════════════
# RISK SCORING TESTS
# ═══════════════════════════════════════════════════════════════════

class TestRiskScoring(TestMessageScorerBase):
    """Tests for the risk score dimension."""

    def test_clean_message_low_risk(self):
        """A clean casual message should have low risk."""
        msg = "hey priya, saw your campus work. what's the community vibe there?"
        score = self.scorer.score_message(msg)
        self.assertLessEqual(score.risk_score, 0.3)

    def test_url_in_opener_high_risk(self):
        """URL in first outreach should increase risk."""
        msg = "hey priya, check out https://clstr.in and join us. what do you think?"
        score = self.scorer.score_message(msg, is_followup=False)
        self.assertGreater(score.risk_score, 0.1)

    def test_url_in_followup_lower_risk(self):
        """URL in follow-up is less risky than in opener."""
        msg = "hey priya, here's the form: https://forms.gle/abc. fill it when you can?"
        score_opener = self.scorer.score_message(msg, is_followup=False)
        score_followup = self.scorer.score_message(msg, is_followup=True)
        self.assertGreater(score_opener.risk_score, score_followup.risk_score)

    def test_phone_in_opener_risky(self):
        """Phone number in opener should increase risk."""
        msg = "hey priya, saw your work. call me at 9441467303"
        score = self.scorer.score_message(msg, is_followup=False)
        self.assertGreater(score.risk_score, 0.1)

    def test_banned_words_very_risky(self):
        """Banned words should significantly increase risk."""
        msg = "Dear Sir, I am writing to offer you a guaranteed free opportunity."
        score = self.scorer.score_message(msg)
        self.assertGreater(score.risk_score, 0.3)

    def test_excessive_length_increases_risk(self):
        """Very long messages increase risk."""
        msg = "hey bro, " + "x " * 300
        score = self.scorer.score_message(msg)
        self.assertGreater(score.risk_score, 0.0)

    def test_all_caps_increases_risk(self):
        """ALL CAPS segments increase risk."""
        msg = "hey priya, THIS IS AMAZING OPPORTUNITY for YOU. what do you think?"
        score = self.scorer.score_message(msg)
        self.assertGreater(score.risk_score, 0.0)

    def test_excessive_punctuation_increases_risk(self):
        """Too many exclamation marks increase risk."""
        msg = "hey priya!!! saw your work!!! so amazing!!! what's your focus???"
        score = self.scorer.score_message(msg)
        self.assertGreater(score.risk_score, 0.0)

    def test_empty_message_max_risk(self):
        """Empty message should be maximum risk."""
        score = self.scorer.score_message("")
        self.assertEqual(score.risk_score, 1.0)


# ═══════════════════════════════════════════════════════════════════
# SIMILARITY SCORING TESTS
# ═══════════════════════════════════════════════════════════════════

class TestSimilarityScoring(TestMessageScorerBase):
    """Tests for the similarity score dimension."""

    def test_no_history_zero_similarity(self):
        """With no message history, similarity should be 0."""
        msg = "hey priya, saw your campus work. what's the community vibe?"
        score = self.scorer.score_message(msg)
        self.assertEqual(score.similarity_score, 0.0)

    def test_exact_duplicate_high_similarity(self):
        """Exact same message should have very high similarity."""
        existing = "hey priya, saw your campus work. what's the vibe there?"
        self._insert_message(existing, days_ago=1)

        score = self.scorer.score_message(existing)
        self.assertGreater(score.similarity_score, 0.9)

    def test_completely_different_low_similarity(self):
        """Totally different messages should have low similarity."""
        self._insert_message("hey priya, saw your TEDx work at VIT. how was it?", days_ago=1)

        msg = "yo raj, noticed the startup cell at BITS. are people there actually shipping?"
        score = self.scorer.score_message(msg)
        self.assertLess(score.similarity_score, 0.5)

    def test_similar_template_catches_high_similarity(self):
        """Messages from the same template should show high similarity."""
        self._insert_message(
            "hey priya, saw your campus ambassador stuff at VIT. do students there actually engage?",
            days_ago=1
        )

        msg = "hey raj, saw your campus ambassador stuff at BITS. do students there actually engage?"
        score = self.scorer.score_message(msg)
        self.assertGreater(score.similarity_score, 0.5)

    def test_old_messages_still_compared(self):
        """Messages within lookback window should be compared."""
        self._insert_message("hey priya, saw your work at VIT. what's the vibe?", days_ago=15)
        msg = "hey priya, saw your work at VIT. what's the vibe?"
        score = self.scorer.score_message(msg)
        self.assertGreater(score.similarity_score, 0.9)


# ═══════════════════════════════════════════════════════════════════
# PERSONALIZATION SCORING TESTS
# ═══════════════════════════════════════════════════════════════════

class TestPersonalizationScoring(TestMessageScorerBase):
    """Tests for the personalization score dimension."""

    def test_fully_personalized_high_score(self):
        """Message with name + college + signal should score high."""
        msg = "hey priya, saw your TEDx work at VIT. how do you keep students engaged?"
        score = self.scorer.score_message(
            msg, name="Priya", college="VIT", signal_type="tedx"
        )
        self.assertGreaterEqual(score.personalization_score, 0.6)

    def test_no_personalization_low_score(self):
        """Generic message with no personal details should score low."""
        msg = "hey, saw your profile. what are you working on?"
        score = self.scorer.score_message(msg, name="", college="", signal_type="default")
        self.assertLess(score.personalization_score, 0.5)

    def test_name_present_boosts_score(self):
        """Having the name in the message should boost personalization."""
        with_name = "hey priya, saw your work. what's your focus?"
        without_name = "hey, saw your work. what's your focus?"
        score_name = self.scorer.score_message(with_name, name="Priya")
        score_no_name = self.scorer.score_message(without_name, name="Priya")
        self.assertGreater(score_name.personalization_score, score_no_name.personalization_score)

    def test_college_reference_boosts_score(self):
        """Mentioning their college should boost personalization."""
        with_college = "hey priya, saw your work at VIT. what's the vibe?"
        without_college = "hey priya, saw your work. what's the vibe?"
        score_c = self.scorer.score_message(with_college, name="Priya", college="VIT")
        score_nc = self.scorer.score_message(without_college, name="Priya", college="VIT")
        self.assertGreater(score_c.personalization_score, score_nc.personalization_score)

    def test_generic_opener_penalized(self):
        """Generic LinkedIn openers should be penalized."""
        msg = "i came across your profile and thought we should connect. what do you think?"
        score = self.scorer.score_message(msg, name="Priya", college="VIT")
        self.assertLess(score.personalization_score, 0.7)

    def test_specific_signal_boosts_score(self):
        """Referencing a specific signal (club name, etc.) boosts score."""
        msg = "hey priya, saw you lead the Robotics Club at VIT. what's the one thing missing?"
        score = self.scorer.score_message(
            msg, name="Priya", college="VIT",
            signal_type="club_president", specific_signal="Robotics Club"
        )
        self.assertGreaterEqual(score.personalization_score, 0.7)


# ═══════════════════════════════════════════════════════════════════
# SAFETY GATE TESTS
# ═══════════════════════════════════════════════════════════════════

class TestSafetyGate(TestMessageScorerBase):
    """Tests for the is_safe_to_send determination."""

    def test_good_message_is_safe(self):
        """Well-crafted message should pass all gates."""
        msg = "hey priya, saw your TEDx work at VIT. how do you keep students engaged after?"
        score = self.scorer.score_message(
            msg, name="Priya", college="VIT", signal_type="tedx"
        )
        self.assertTrue(score.is_safe_to_send)

    def test_empty_message_not_safe(self):
        """Empty message should be blocked."""
        score = self.scorer.score_message("")
        self.assertFalse(score.is_safe_to_send)

    def test_spammy_message_not_safe(self):
        """Spammy corporate message should be blocked."""
        msg = "Dear Sir, I am writing to offer you a guaranteed free opportunity. Click here now!"
        score = self.scorer.score_message(msg)
        # Should fail on either quality (too corporate) or risk (banned words)
        self.assertFalse(score.is_safe_to_send)

    def test_reasons_populated_on_block(self):
        """Blocked messages should have reasons explaining why."""
        score = self.scorer.score_message("")
        self.assertFalse(score.is_safe_to_send)
        self.assertTrue(len(score.reasons) > 0)

    def test_reasons_populated_on_pass(self):
        """Passing messages should have positive reasons."""
        msg = "hey priya, saw your TEDx work at VIT. how do you keep students engaged?"
        score = self.scorer.score_message(
            msg, name="Priya", college="VIT", signal_type="tedx"
        )
        if score.is_safe_to_send:
            self.assertTrue(len(score.reasons) > 0)

    def test_summary_contains_status(self):
        """Summary string should contain SAFE or BLOCKED."""
        msg = "hey priya, saw your work. what's your focus?"
        score = self.scorer.score_message(msg, name="Priya")
        summary = score.summary()
        self.assertTrue("SAFE" in summary or "BLOCKED" in summary)

    def test_high_similarity_blocks(self):
        """Very high similarity to recent messages should block."""
        existing = "hey priya, saw your campus ambassador stuff at VIT. do students there actually engage?"
        self._insert_message(existing, days_ago=1)

        # Exact same message
        score = self.scorer.score_message(
            existing, name="Priya", college="VIT", signal_type="campus_ambassador"
        )
        # Should be blocked due to high similarity
        if score.similarity_score > 0.85:
            self.assertFalse(score.is_safe_to_send)


# ═══════════════════════════════════════════════════════════════════
# BATCH SCORING TESTS
# ═══════════════════════════════════════════════════════════════════

class TestBatchScoring(TestMessageScorerBase):
    """Tests for the batch scoring / dashboard support."""

    def test_empty_db_returns_zeros(self):
        """Empty DB should return zero averages."""
        stats = self.scorer.score_recent_messages(days=7)
        self.assertEqual(stats["count"], 0)
        self.assertEqual(stats["avg_quality"], 0.0)

    def test_batch_with_messages(self):
        """Batch scoring should process multiple messages."""
        # Insert prospect first
        self.db.conn.execute(
            "INSERT INTO prospects (id, profile_url, name, college, signal_type) VALUES (1, 'url1', 'Priya', 'VIT', 'tedx')"
        )
        self._insert_message("hey priya, saw your TEDx work. how was it?", days_ago=1)
        self._insert_message("hey raj, noticed the startup cell. are people shipping?", days_ago=2)

        stats = self.scorer.score_recent_messages(days=7)
        self.assertEqual(stats["count"], 2)
        self.assertGreater(stats["avg_quality"], 0.0)


if __name__ == "__main__":
    unittest.main()
