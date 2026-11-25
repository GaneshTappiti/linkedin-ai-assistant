#!/usr/bin/env python3
"""
message_quality.py — Pre-Send Message Quality Scoring for clstr.in Outreach OS
================================================================================
The automated trust layer. Every draft message is scored BEFORE it enters the
approval queue or gets sent. Four deterministic scores, all computed locally
with zero external dependencies.

Scores:
  - quality_score       (0.0-1.0)  Overall message quality
  - risk_score          (0.0-1.0)  Detection/spam risk (lower = safer)
  - similarity_score    (0.0-1.0)  How similar to recent messages (lower = more unique)
  - personalization_score (0.0-1.0) How personalized the message is

Usage:
    from message_quality import MessageScorer

    scorer = MessageScorer(db)
    score = scorer.score_message(
        draft="hey Priya, saw your TEDx work at VIT...",
        name="Priya",
        college="VIT",
        signal_type="tedx"
    )
    if score.is_safe_to_send:
        # proceed to approval queue
    else:
        # auto-block with reasons
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from outreach_db import OutreachDB

log = logging.getLogger("message_quality")


# ═══════════════════════════════════════════════════════════════════
# SCORE DATACLASS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MessageScore:
    """Container for all message quality scores."""
    quality_score: float = 0.0
    risk_score: float = 0.0
    similarity_score: float = 0.0
    personalization_score: float = 0.0
    is_safe_to_send: bool = False
    reasons: list = field(default_factory=list)

    def summary(self) -> str:
        """Human-readable one-line summary."""
        safe = "✓ SAFE" if self.is_safe_to_send else "✗ BLOCKED"
        return (
            f"{safe} | "
            f"quality={self.quality_score:.2f} "
            f"risk={self.risk_score:.2f} "
            f"similar={self.similarity_score:.2f} "
            f"personal={self.personalization_score:.2f}"
        )


# ═══════════════════════════════════════════════════════════════════
# THRESHOLDS
# ═══════════════════════════════════════════════════════════════════

# Minimum quality score to allow sending
MIN_QUALITY_SCORE = 0.6

# Maximum risk score to allow sending
MAX_RISK_SCORE = 0.7

# Maximum similarity to recent messages before warning
MAX_SIMILARITY_SCORE = 0.85

# How many recent messages to compare against for similarity
SIMILARITY_LOOKBACK_DAYS = 30
SIMILARITY_MAX_MESSAGES = 50


# ═══════════════════════════════════════════════════════════════════
# BANNED / RISKY PATTERNS
# ═══════════════════════════════════════════════════════════════════

# Words that should NEVER appear in a first outreach message
BANNED_WORDS_OPENER = {
    "unsubscribe", "opt-out", "bulk", "mass", "automated",
    "dear sir", "dear madam", "to whom", "dear hiring",
    "we are pleased", "i am writing to", "on behalf of",
    "kindly", "humbly", "respected", "esteemed",
    "100%", "guarantee", "free", "discount", "limited time",
    "click here", "act now", "hurry", "urgent",
}

# Words that increase risk score but don't auto-block
RISKY_WORDS = {
    "opportunity", "exciting", "amazing", "incredible",
    "partnership", "collaboration", "synergy",
    "apply now", "join us", "we're hiring",
    "check out", "visit",
}

# Patterns that indicate template-ness (reduce quality)
TEMPLATE_PATTERNS = [
    r"\{[a-z_]+\}",           # Unreplaced template variables
    r"<[A-Z_]+>",             # Unreplaced placeholders
    r"\[INSERT .+?\]",        # Manual placeholders
    r"FIRST_NAME|COLLEGE",    # Common template tokens
]

# URL pattern
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

# Phone number pattern (Indian format)
PHONE_PATTERN = re.compile(r"\b\d{10}\b|\b\d{5}\s?\d{5}\b|\+91\s?\d{10}")


# ═══════════════════════════════════════════════════════════════════
# SCORER
# ═══════════════════════════════════════════════════════════════════

class MessageScorer:
    """
    Deterministic message quality scorer. No ML, no external APIs.
    All scoring is rules-based, computed with Python stdlib only.
    """

    def __init__(self, db: OutreachDB):
        self.db = db
        self._recent_messages_cache = None
        self._cache_timestamp = None

    def score_message(
        self,
        draft: str,
        name: str = "",
        college: str = "",
        signal_type: str = "",
        specific_signal: str = "",
        is_followup: bool = False,
    ) -> MessageScore:
        """
        Score a draft message across all four dimensions.
        Returns a MessageScore with is_safe_to_send determination.
        """
        score = MessageScore()

        # Compute individual scores
        score.quality_score = self._score_quality(draft, is_followup)
        score.risk_score = self._score_risk(draft, is_followup)
        score.similarity_score = self._score_similarity(draft)
        score.personalization_score = self._score_personalization(
            draft, name, college, signal_type, specific_signal
        )

        # Determine safety
        score.is_safe_to_send = True

        if score.quality_score < MIN_QUALITY_SCORE:
            score.is_safe_to_send = False
            score.reasons.append(
                f"Quality too low: {score.quality_score:.2f} < {MIN_QUALITY_SCORE}"
            )

        if score.risk_score > MAX_RISK_SCORE:
            score.is_safe_to_send = False
            score.reasons.append(
                f"Risk too high: {score.risk_score:.2f} > {MAX_RISK_SCORE}"
            )

        if score.similarity_score > MAX_SIMILARITY_SCORE:
            score.is_safe_to_send = False
            score.reasons.append(
                f"Too similar to recent messages: {score.similarity_score:.2f}"
            )

        # Add positive reasons
        if score.is_safe_to_send:
            if score.personalization_score >= 0.7:
                score.reasons.append("Good personalization")
            if score.risk_score <= 0.2:
                score.reasons.append("Low risk")
            if score.similarity_score <= 0.3:
                score.reasons.append("Highly unique")
            if not score.reasons:
                score.reasons.append("Passes all checks")

        log.info(f"Score: {score.summary()}")
        return score

    # ─────────────────────────────────────────────────────────────
    # QUALITY SCORING
    # ─────────────────────────────────────────────────────────────
    def _score_quality(self, draft: str, is_followup: bool = False) -> float:
        """
        Score overall message quality (0.0 - 1.0).

        Checks:
          - Length (sweet spot: 50-250 chars for openers)
          - Sentence count (1-3 sentences ideal)
          - Contains a question (engagement signal)
          - Lowercase style (matches Ganesh's voice)
          - No unreplaced template variables
          - Starts naturally (hey, hi — not Dear)
        """
        if not draft or not draft.strip():
            return 0.0

        points = 0.0
        max_points = 6.0

        # 1. Length check (20% weight)
        length = len(draft)
        if is_followup:
            # Follow-ups should be shorter
            if 30 <= length <= 200:
                points += 1.0
            elif 20 <= length <= 250:
                points += 0.6
            elif length > 0:
                points += 0.2
        else:
            # Openers have slightly more room
            if 50 <= length <= 250:
                points += 1.0
            elif length > 0:
                points -= 1.0

        # 2. Sentence count (15% weight)
        sentences = [s.strip() for s in re.split(r'[.!?]+', draft) if s.strip()]
        if 1 <= len(sentences) <= 3:
            points += 1.0
        elif len(sentences) == 4:
            points += 0.5
        else:
            points += 0.2

        # 3. Contains a question (20% weight — engagement signal)
        if "?" in draft:
            points += 1.0
        else:
            points += 0.2  # No question = less engaging

        # 4. Lowercase style match (15% weight)
        # Ganesh's style: mostly lowercase, casual
        upper_ratio = sum(1 for c in draft if c.isupper()) / max(len(draft), 1)
        if upper_ratio < 0.05:
            points += 1.0  # Very casual — perfect
        elif upper_ratio < 0.15:
            points += 0.7  # Some caps — acceptable
        else:
            points += 0.3  # Too formal/corporate

        # 5. No unreplaced templates (15% weight)
        has_template = any(
            re.search(pat, draft) for pat in TEMPLATE_PATTERNS
        )
        if not has_template:
            points += 1.0
        else:
            points -= 2.0  # Template leak = huge penalty

        # 6. Natural opening (15% weight)
        lower_draft = draft.lower().strip()
        if lower_draft.startswith(("hey ", "hi ", "yo ")):
            points += 1.0  # Natural casual opening
        elif lower_draft.startswith(("hello ", "hey,", "hi,")):
            points += 0.6  # Acceptable but slightly formal
        elif lower_draft.startswith(("dear ", "respected ", "greetings")):
            points -= 1.0  # Corporate — huge penalty
        else:
            points += 0.4  # Neutral

        return round(min(points / max_points, 1.0), 3)

    # ─────────────────────────────────────────────────────────────
    # RISK SCORING
    # ─────────────────────────────────────────────────────────────
    def _score_risk(self, draft: str, is_followup: bool = False) -> float:
        """
        Score detection/spam risk (0.0 - 1.0). Lower = safer.

        Checks:
          - Banned words present
          - Risky words present
          - URL in first message (should never be)
          - Phone number in first message
          - Excessive length (spam signal)
          - ALL CAPS segments
          - Excessive punctuation (!!!, ???)
        """
        if not draft or not draft.strip():
            return 1.0  # Empty message = maximum risk

        risk_points = 0.0
        max_risk = 7.0
        lower = draft.lower()

        # 1. Banned words (heavy penalty)
        banned_found = [w for w in BANNED_WORDS_OPENER if w in lower]
        if banned_found:
            risk_points += len(banned_found) * 2.0
            log.warning(f"  Banned words found: {banned_found}")

        # 2. Risky words (moderate penalty)
        risky_found = [w for w in RISKY_WORDS if w in lower]
        if risky_found:
            risk_points += min(len(risky_found) * 0.3, 1.0)

        # 3. URL in first message (high risk for openers)
        if URL_PATTERN.search(draft):
            if not is_followup:
                risk_points += 1.5  # URL in opener = very risky
            else:
                risk_points += 0.3  # URL in followup = slightly risky

        # 4. Phone number in first message
        if PHONE_PATTERN.search(draft):
            if not is_followup:
                risk_points += 1.0  # Phone in opener = risky
            else:
                risk_points += 0.2  # Phone in followup = ok if they asked

        # 5. Excessive length
        if len(draft) > 500:
            risk_points += 1.0
        elif len(draft) > 320:
            risk_points += 0.5

        # 6. ALL CAPS segments (3+ consecutive uppercase words)
        caps_words = re.findall(r'\b[A-Z]{3,}\b', draft)
        if len(caps_words) >= 2:
            risk_points += 0.5

        # 7. Excessive punctuation
        if draft.count("!") >= 3 or draft.count("?") >= 3:
            risk_points += 0.5

        return round(min(risk_points / max_risk, 1.0), 3)

    # ─────────────────────────────────────────────────────────────
    # SIMILARITY SCORING
    # ─────────────────────────────────────────────────────────────
    def _score_similarity(self, draft: str) -> float:
        """
        Score how similar this draft is to recent outbound messages (0.0 - 1.0).
        Uses Jaccard similarity on word sets (bigrams for better accuracy).
        Lower = more unique.
        """
        recent = self._get_recent_messages()
        if not recent:
            return 0.0  # No history = perfectly unique

        draft_bigrams = self._get_bigrams(draft)
        if not draft_bigrams:
            return 0.0

        max_sim = 0.0
        for msg_text in recent:
            msg_bigrams = self._get_bigrams(msg_text)
            if not msg_bigrams:
                continue
            sim = self._jaccard(draft_bigrams, msg_bigrams)
            max_sim = max(max_sim, sim)

        return round(max_sim, 3)

    def _get_bigrams(self, text: str) -> set:
        """Extract word bigrams from text for similarity comparison."""
        words = re.findall(r'[a-z]+', text.lower())
        if len(words) < 2:
            return set(words)
        return {f"{words[i]}_{words[i+1]}" for i in range(len(words) - 1)}

    def _jaccard(self, set_a: set, set_b: set) -> float:
        """Jaccard similarity coefficient between two sets."""
        if not set_a and not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0

    def _get_recent_messages(self) -> list[str]:
        """
        Get recent outbound messages from SQLite for similarity comparison.
        Cached for 5 minutes to avoid hammering the DB.
        """
        now = datetime.now()

        # Cache check
        if (self._recent_messages_cache is not None
                and self._cache_timestamp
                and (now - self._cache_timestamp).seconds < 300):
            return self._recent_messages_cache

        # Query recent outbound messages
        cutoff = (now - timedelta(days=SIMILARITY_LOOKBACK_DAYS)).isoformat()
        rows = self.db.conn.execute("""
            SELECT message_text FROM messages
            WHERE direction = 'outbound' AND sent_at > ?
            ORDER BY sent_at DESC
            LIMIT ?
        """, (cutoff, SIMILARITY_MAX_MESSAGES)).fetchall()

        self._recent_messages_cache = [row["message_text"] for row in rows]
        self._cache_timestamp = now
        return self._recent_messages_cache

    def invalidate_cache(self):
        """Clear the similarity cache (call after sending a new message)."""
        self._recent_messages_cache = None
        self._cache_timestamp = None

    # ─────────────────────────────────────────────────────────────
    # PERSONALIZATION SCORING
    # ─────────────────────────────────────────────────────────────
    def _score_personalization(
        self,
        draft: str,
        name: str,
        college: str,
        signal_type: str,
        specific_signal: str,
    ) -> float:
        """
        Score how personalized the message is (0.0 - 1.0).

        Checks:
          - First name used in message
          - College/campus referenced
          - Signal type referenced (TEDx, startup cell, etc.)
          - Specific signal referenced (club name, event, etc.)
          - Not just a generic template
        """
        if not draft or not draft.strip():
            return 0.0

        points = 0.0
        max_points = 5.0
        lower = draft.lower()

        # 1. First name present (25% weight)
        if name:
            first_name = name.strip().split()[0].lower() if name.strip() else ""
            if first_name and first_name in lower:
                points += 1.0
            else:
                points += 0.0

        # 2. College referenced (25% weight)
        if college:
            college_lower = college.lower()
            # Check for college name or reasonable abbreviation
            if college_lower in lower:
                points += 1.0
            elif len(college_lower) > 5 and college_lower[:4] in lower:
                points += 0.5  # Partial match (abbreviation)
            else:
                # Check for "your campus" / "your college" fallback
                if "your campus" in lower or "your college" in lower:
                    points += 0.3
        else:
            # No college provided — check for generic campus reference
            if "your campus" in lower or "your college" in lower:
                points += 0.3

        # 3. Signal type referenced (20% weight)
        signal_keywords = {
            "tedx": ["tedx", "ted"],
            "campus_ambassador": ["ambassador"],
            "event_coordinator": ["event", "coordinator", "organizer"],
            "student_council": ["council", "student union"],
            "club_president": ["club", "society", "president"],
            "core_team_design": ["design", "creative", "figma", "branding"],
            "core_team_marketing": ["marketing", "growth", "content"],
            "startup_cell": ["startup", "entrepreneurship", "e-cell"],
        }
        keywords = signal_keywords.get(signal_type, [])
        if any(kw in lower for kw in keywords):
            points += 1.0
        elif signal_type != "default":
            points += 0.2  # Has a signal type but didn't reference it

        # 4. Specific signal referenced (15% weight)
        if specific_signal:
            if specific_signal.lower() in lower:
                points += 1.0
            else:
                points += 0.2

        # 5. Non-generic feel (15% weight)
        # Check that the message doesn't feel like a mass template
        generic_openers = [
            "i came across your profile",
            "i noticed your profile",
            "i saw your profile and thought",
            "i'm reaching out because",
            "i hope this message finds you",
        ]
        is_generic = any(g in lower for g in generic_openers)
        if not is_generic:
            points += 1.0
        else:
            points += 0.2

        return round(min(points / max_points, 1.0), 3)

    # ─────────────────────────────────────────────────────────────
    # BATCH SCORING (for dashboard / analytics)
    # ─────────────────────────────────────────────────────────────
    def score_recent_messages(self, days: int = 7) -> dict:
        """
        Score all outbound messages from the last N days.
        Returns aggregate stats for the dashboard.
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = self.db.conn.execute("""
            SELECT m.message_text, p.name, p.college, p.signal_type
            FROM messages m
            JOIN prospects p ON p.id = m.prospect_id
            WHERE m.direction = 'outbound' AND m.sent_at > ?
            ORDER BY m.sent_at DESC
        """, (cutoff,)).fetchall()

        if not rows:
            return {
                "count": 0,
                "avg_quality": 0.0,
                "avg_risk": 0.0,
                "avg_similarity": 0.0,
                "avg_personalization": 0.0,
                "blocked_count": 0,
            }

        scores = []
        blocked = 0
        for row in rows:
            r = dict(row)
            s = self.score_message(
                draft=r["message_text"],
                name=r.get("name") or "",
                college=r.get("college") or "",
                signal_type=r.get("signal_type") or "default",
            )
            scores.append(s)
            if not s.is_safe_to_send:
                blocked += 1

        return {
            "count": len(scores),
            "avg_quality": round(sum(s.quality_score for s in scores) / len(scores), 3),
            "avg_risk": round(sum(s.risk_score for s in scores) / len(scores), 3),
            "avg_similarity": round(sum(s.similarity_score for s in scores) / len(scores), 3),
            "avg_personalization": round(sum(s.personalization_score for s in scores) / len(scores), 3),
            "blocked_count": blocked,
        }
