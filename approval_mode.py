#!/usr/bin/env python3
"""
approval_mode.py — Human-in-the-Loop Approval for clstr.in Outreach
====================================================================
CLI-based approval system. Before any message is sent, the human reviews
the draft and decides: Send, Edit, Skip, or Quit.

Modes:
  --approve  : Show each draft, wait for human approval (DEFAULT)
  --auto     : Send automatically (no approval, current behavior)
  --dry-run  : Generate all drafts, save to DB, send nothing
"""

import sys
import logging
from typing import Optional

from outreach_db import OutreachDB
from message_quality import MessageScorer, MessageScore

log = logging.getLogger("approval_mode")


class ApprovalMode:
    """
    Human-in-the-loop message approval system.

    Presents draft messages to the operator for review before sending.
    Supports three modes: approve (interactive), auto (skip review), dry-run (no send).
    """

    MODE_APPROVE = "approve"   # Interactive human review
    MODE_AUTO = "auto"         # Auto-send (no review)
    MODE_DRYRUN = "dry-run"    # Generate only, never send

    def __init__(self, mode: str, db: OutreachDB):
        self.mode = mode
        self.db = db
        self.scorer = MessageScorer(db)
        self._quit_requested = False

        if mode == self.MODE_APPROVE:
            log.info("APPROVAL MODE: Human review required for each message")
        elif mode == self.MODE_AUTO:
            log.info("AUTO MODE: Messages will be sent without review")
        elif mode == self.MODE_DRYRUN:
            log.info("DRY-RUN MODE: Drafts generated, nothing will be sent")

    @property
    def quit_requested(self) -> bool:
        return self._quit_requested

    def review_message(
        self,
        prospect_id: int,
        name: str,
        college: str,
        signal_type: str,
        role_fit: str,
        draft_message: str,
        count: int,
        total: int,
    ) -> tuple[str, Optional[str]]:
        """
        Review a draft message. Returns (action, final_message).

        Actions:
          - "send"  : Approved, send the message (final_message = original or edited)
          - "skip"  : Skip this prospect
          - "quit"  : Stop the entire session

        In auto mode, always returns ("send", draft_message).
        In dry-run mode, saves to DB and returns ("skip", None).
        """
        # Create approval record in DB
        approval_id = self.db.create_approval(
            prospect_id=prospect_id,
            draft_message=draft_message,
            signal_type=signal_type,
            role_fit=role_fit,
        )

        # Score the message
        msg_score = self.scorer.score_message(
            draft=draft_message,
            name=name or "",
            college=college or "",
            signal_type=signal_type or "default",
        )

        if self.mode == self.MODE_AUTO:
            if not msg_score.is_safe_to_send:
                log.warning(
                    f"AUTO MODE: Message blocked by quality scoring for {name}. "
                    f"Reasons: {msg_score.reasons}"
                )
                self.db.skip_approval(approval_id)
                return "skip", None
            self.db.approve_message(approval_id)
            return "send", draft_message

        if self.mode == self.MODE_DRYRUN:
            log.info(
                f"DRY-RUN: Draft saved for {name} (approval #{approval_id}) "
                f"Score: {msg_score.summary()}"
            )
            self.db.skip_approval(approval_id)
            return "skip", None

        # ── Interactive approval mode ─────────────────────────────
        return self._interactive_review(
            approval_id, name, college, signal_type, role_fit,
            draft_message, count, total, msg_score
        )

    def _interactive_review(
        self,
        approval_id: int,
        name: str,
        college: str,
        signal_type: str,
        role_fit: str,
        draft_message: str,
        count: int,
        total: int,
        msg_score: MessageScore = None,
    ) -> tuple[str, Optional[str]]:
        """Show the draft to the human and wait for their decision."""
        border = "─" * 57
        print(f"\n┌{border}┐")
        print(f"│  OUTREACH DRAFT #{count}/{total}                               │"[:59] + "│")
        print(f"│{' ' * 57}│")
        print(f"│  To: {name:<51}│"[:59] + "│")
        print(f"│  College: {college or 'Unknown':<46}│"[:59] + "│")
        print(f"│  Signal: {signal_type or 'default':<47}│"[:59] + "│")
        print(f"│  Role Fit: {role_fit or 'Campus Ambassador':<45}│"[:59] + "│")
        print(f"│{' ' * 57}│")
        print(f"│  Message:                                               │"[:59] + "│")

        # Word-wrap the message for display
        words = draft_message.split()
        line = "│  "
        for word in words:
            if len(line) + len(word) + 1 > 56:
                print(f"{line:<58}│")
                line = "│  " + word
            else:
                line = line + " " + word if len(line) > 3 else line + word
        if line.strip("│ "):
            print(f"{line:<58}│")

        # Display quality scores
        if msg_score:
            print(f"│{' ' * 57}│")
            q_bar = self._score_bar(msg_score.quality_score)
            r_bar = self._score_bar(msg_score.risk_score, invert=True)
            s_bar = self._score_bar(msg_score.similarity_score, invert=True)
            p_bar = self._score_bar(msg_score.personalization_score)
            print(f"│  Quality: {q_bar} {msg_score.quality_score:.2f}  "
                  f"Risk: {r_bar} {msg_score.risk_score:.2f}       │"[:59] + "│")
            print(f"│  Similar: {s_bar} {msg_score.similarity_score:.2f}  "
                  f"Personal: {p_bar} {msg_score.personalization_score:.2f}  │"[:59] + "│")

            if not msg_score.is_safe_to_send:
                print(f"│{' ' * 57}│")
                print(f"│  ⚠ BLOCKED: {'; '.join(msg_score.reasons)[:42]:<44}│"[:59] + "│")

        print(f"│{' ' * 57}│")

        if msg_score and not msg_score.is_safe_to_send:
            print(f"│  [S]end anyway  [E]dit  [K]ip (recommended)  [Q]uit     │"[:59] + "│")
        else:
            print(f"│  [S]end  [E]dit  [K]ip  [Q]uit                          │"[:59] + "│")
        print(f"└{border}┘")

        while True:
            try:
                choice = input("\n  Your choice: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = "q"

            if choice in ("s", "send", ""):
                self.db.approve_message(approval_id)
                print("  ✓ Approved — sending...")
                return "send", draft_message

            elif choice in ("e", "edit"):
                print(f"\n  Current: {draft_message}")
                try:
                    edited = input("  New message: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("  (cancelled)")
                    continue
                if edited:
                    self.db.approve_message(approval_id, final_message=edited)
                    print("  ✓ Edited & approved — sending...")
                    return "send", edited
                else:
                    print("  (empty — keeping original)")
                    continue

            elif choice in ("k", "skip"):
                self.db.skip_approval(approval_id)
                print("  ⊘ Skipped")
                return "skip", None

            elif choice in ("q", "quit"):
                self.db.skip_approval(approval_id)
                self._quit_requested = True
                print("  ■ Quitting session...")
                return "quit", None

            else:
                print("  Invalid choice. Use [S]end, [E]dit, [K]ip, or [Q]uit")

    @staticmethod
    def _score_bar(value: float, width: int = 8, invert: bool = False) -> str:
        """
        Render a visual score bar. If invert=True, lower values are better (e.g., risk).

        Examples:
            0.85 → "████████░░"
            0.30 → "███░░░░░░░"
        """
        filled = int(value * width)
        empty = width - filled
        return f"{'█' * filled}{'░' * empty}"


def parse_mode_from_args(args: list[str] = None) -> str:
    """Parse the approval mode from command line arguments."""
    if args is None:
        args = sys.argv[1:]

    for arg in args:
        if arg in ("--approve", "-a"):
            return ApprovalMode.MODE_APPROVE
        elif arg in ("--auto",):
            return ApprovalMode.MODE_AUTO
        elif arg in ("--dry-run", "--dryrun", "-d"):
            return ApprovalMode.MODE_DRYRUN

    # Default: approve mode (safest)
    return ApprovalMode.MODE_APPROVE
