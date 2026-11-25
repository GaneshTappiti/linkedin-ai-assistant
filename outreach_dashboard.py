#!/usr/bin/env python3
"""
outreach_dashboard.py — CLI Operational Dashboard for clstr.in Outreach OS
==========================================================================
Terminal-based dashboard providing full operational visibility into the
outreach pipeline. Zero external dependencies — uses Python stdlib only.

Usage:
    python outreach_dashboard.py            # Auto-refresh every 30s
    python outreach_dashboard.py --once     # Single snapshot
    python outreach_dashboard.py --compact  # Fewer sections
    python outreach_dashboard.py --export   # Plain text (no ANSI colors)
"""

import os
import sys
import time
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

# ── Ensure project root is on path ──────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from outreach_db import OutreachDB
from safety_governor import SafetyGovernor
from message_quality import MessageScorer

# ═══════════════════════════════════════════════════════════════════
# ANSI ESCAPE CODES — for terminal styling
# ═══════════════════════════════════════════════════════════════════
class C:
    """ANSI color codes. Disabled when --export is used."""
    RESET       = "\033[0m"
    BOLD        = "\033[1m"
    DIM         = "\033[2m"
    UNDERLINE   = "\033[4m"

    # Foreground
    RED         = "\033[91m"
    GREEN       = "\033[92m"
    YELLOW      = "\033[93m"
    BLUE        = "\033[94m"
    MAGENTA     = "\033[95m"
    CYAN        = "\033[96m"
    WHITE       = "\033[97m"
    GRAY        = "\033[90m"

    # Background
    BG_RED      = "\033[41m"
    BG_GREEN    = "\033[42m"
    BG_YELLOW   = "\033[43m"
    BG_BLUE     = "\033[44m"

    @classmethod
    def disable(cls):
        """Strip all ANSI codes for --export mode."""
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith("_"):
                setattr(cls, attr, "")


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD ENGINE
# ═══════════════════════════════════════════════════════════════════
class OutreachDashboard:
    """Terminal-based operational dashboard for the outreach pipeline."""

    # Pipeline stage display order and labels
    PIPELINE_STAGES = [
        ("new",          "New Prospects"),
        ("opener_sent",  "Opener Sent"),
        ("followup_1",   "Follow-Up #1"),
        ("followup_2",   "Follow-Up #2"),
        ("followup_3",   "Follow-Up #3"),
        ("awaiting_reply","Awaiting Reply"),
        ("replied",      "Replied"),
        ("interested",   "Interested"),
        ("form_sent",    "Form Sent"),
        ("converted",    "Converted ✓"),
        ("deferred",     "Deferred"),
        ("re_engage",    "Re-Engage"),
        ("dead",         "Dead ✗"),
    ]

    # Width of the dashboard
    WIDTH = 64

    def __init__(self, db: OutreachDB, compact: bool = False):
        self.db = db
        self.gov = SafetyGovernor(db)
        self.scorer = MessageScorer(db)
        self.compact = compact

    # ─────────────────────────────────────────────────────────────
    # MAIN RENDER
    # ─────────────────────────────────────────────────────────────
    def render(self) -> str:
        """Render the full dashboard as a string."""
        lines = []
        now = datetime.now()

        lines.append(self._header(now))
        lines.append(self._pipeline_funnel())
        lines.append(self._daily_safety_budget())
        lines.append(self._cooldown_status())

        if not self.compact:
            lines.append(self._active_sessions())
            lines.append(self._followup_queue())
            lines.append(self._recent_activity())
            lines.append(self._message_quality_summary())
            lines.append(self._reply_metrics())

        lines.append(self._risk_alerts())
        lines.append(self._footer(now))

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────
    def _header(self, now: datetime) -> str:
        w = self.WIDTH
        ts = now.strftime("%Y-%m-%d %H:%M:%S %Z").strip()
        stats = self.db.get_stats()

        title = "OUTREACH OS — OPERATIONAL DASHBOARD"
        prospect_line = (
            f"Prospects: {C.BOLD}{stats['total_prospects']}{C.RESET}  "
            f"Messaged: {C.BOLD}{stats['total_messaged']}{C.RESET}  "
            f"Replies: {C.BOLD}{stats['total_replies']}{C.RESET}"
        )

        return (
            f"\n{C.CYAN}{'═' * w}{C.RESET}\n"
            f"{C.BOLD}{C.CYAN}  {title}{C.RESET}\n"
            f"{C.DIM}  {ts}{C.RESET}\n"
            f"  {prospect_line}\n"
            f"{C.CYAN}{'═' * w}{C.RESET}"
        )

    # ─────────────────────────────────────────────────────────────
    # PIPELINE FUNNEL
    # ─────────────────────────────────────────────────────────────
    def _pipeline_funnel(self) -> str:
        stats = self.db.get_stats()
        pipeline = stats.get("pipeline", {})
        total = stats["total_prospects"] or 1  # avoid div by zero

        lines = [f"\n{C.BOLD}  ┌─ PIPELINE FUNNEL {'─' * (self.WIDTH - 22)}┐{C.RESET}"]

        # Find max count for bar scaling
        max_count = max(pipeline.values()) if pipeline else 1
        bar_max_width = 30

        for stage_key, stage_label in self.PIPELINE_STAGES:
            count = pipeline.get(stage_key, 0)
            if count == 0 and self.compact:
                continue

            # Color coding by stage type
            if stage_key in ("converted",):
                color = C.GREEN
            elif stage_key in ("dead",):
                color = C.RED
            elif stage_key in ("deferred", "re_engage"):
                color = C.YELLOW
            elif stage_key in ("interested", "replied"):
                color = C.MAGENTA
            elif stage_key in ("followup_1", "followup_2", "followup_3"):
                color = C.BLUE
            else:
                color = C.CYAN

            # Draw bar
            if max_count > 0:
                bar_len = max(0, int((count / max_count) * bar_max_width))
            else:
                bar_len = 0

            bar = f"{color}{'█' * bar_len}{'░' * (bar_max_width - bar_len)}{C.RESET}"
            pct = (count / total) * 100
            lines.append(f"  │  {stage_label:<16} {bar} {count:>3} ({pct:>4.1f}%)")

        lines.append(f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # DAILY SAFETY BUDGET
    # ─────────────────────────────────────────────────────────────
    def _daily_safety_budget(self) -> str:
        can_send, remaining = self.db.can_send_today(SafetyGovernor.MAX_DMS_PER_DAY)
        sent_today = SafetyGovernor.MAX_DMS_PER_DAY - remaining
        limit = SafetyGovernor.MAX_DMS_PER_DAY
        pct_used = (sent_today / limit) * 100 if limit > 0 else 0
        pct_remaining = 100 - pct_used

        # Color based on budget usage
        if pct_used >= 80:
            bar_color = C.RED
            status_text = f"{C.RED}⚠ NEARLY EXHAUSTED{C.RESET}"
        elif pct_used >= 50:
            bar_color = C.YELLOW
            status_text = f"{C.YELLOW}▸ moderate usage{C.RESET}"
        else:
            bar_color = C.GREEN
            status_text = f"{C.GREEN}✓ healthy{C.RESET}"

        bar_width = 30
        filled = int((sent_today / limit) * bar_width) if limit > 0 else 0
        empty = bar_width - filled
        bar = f"{bar_color}{'█' * filled}{C.RESET}{'░' * empty}"

        lines = [
            f"\n{C.BOLD}  ┌─ DAILY SAFETY BUDGET {'─' * (self.WIDTH - 26)}┐{C.RESET}",
            f"  │  Today: {C.BOLD}{sent_today}/{limit}{C.RESET}  [{bar}]  {pct_remaining:.0f}% remaining",
            f"  │  Status: {status_text}",
            f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}",
        ]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # COOLDOWN STATUS
    # ─────────────────────────────────────────────────────────────
    def _cooldown_status(self) -> str:
        outreach_ok, outreach_mins = self.gov.check_cooldown("outreach")
        inbox_ok, inbox_mins = self.gov.check_cooldown("inbox")

        def _status(ok: bool, mins: float, label: str) -> str:
            if ok:
                return f"  │  {label:<12} {C.GREEN}CLEAR ✓{C.RESET}"
            else:
                m = int(mins)
                return f"  │  {label:<12} {C.YELLOW}⏳ {m}m remaining{C.RESET}"

        lines = [
            f"\n{C.BOLD}  ┌─ COOLDOWN STATUS {'─' * (self.WIDTH - 22)}┐{C.RESET}",
            _status(outreach_ok, outreach_mins, "Outreach:"),
            _status(inbox_ok, inbox_mins, "Inbox:"),
            f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}",
        ]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # ACTIVE SESSIONS
    # ─────────────────────────────────────────────────────────────
    def _active_sessions(self) -> str:
        rows = self.db.conn.execute("""
            SELECT id, agent_type, status, started_at, ended_at, messages_sent
            FROM sessions
            ORDER BY started_at DESC LIMIT 5
        """).fetchall()

        lines = [f"\n{C.BOLD}  ┌─ SESSIONS (last 5) {'─' * (self.WIDTH - 24)}┐{C.RESET}"]

        if not rows:
            lines.append(f"  │  {C.DIM}No sessions recorded yet{C.RESET}")
        else:
            for r in rows:
                r = dict(r)
                sid = r["id"][:8]
                agent = r["agent_type"]
                status = r["status"]
                sent = r["messages_sent"] or 0

                # Status color
                if status == "running":
                    sc = f"{C.GREEN}●{C.RESET} running"
                elif status == "completed":
                    sc = f"{C.BLUE}✓{C.RESET} done"
                elif status == "crashed":
                    sc = f"{C.RED}✗{C.RESET} CRASHED"
                else:
                    sc = f"{C.YELLOW}■{C.RESET} stopped"

                # Format timestamp
                try:
                    started = datetime.fromisoformat(r["started_at"]).strftime("%m/%d %H:%M")
                except (ValueError, TypeError):
                    started = "?"

                lines.append(f"  │  {sid}  {agent:<10} {sc:<22} {sent:>2} msgs  {started}")

        lines.append(f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # FOLLOW-UP QUEUE
    # ─────────────────────────────────────────────────────────────
    def _followup_queue(self) -> str:
        followups = self.db.get_pending_followups()
        now = datetime.now()

        # Also get prospects that SHOULD have followups but don't (opener_sent + null followup_at)
        stale = self.db.conn.execute("""
            SELECT p.name, pl.stage, pl.next_followup_at, pl.updated_at
            FROM pipeline pl
            JOIN prospects p ON p.id = pl.prospect_id
            WHERE pl.stage = 'opener_sent' AND pl.next_followup_at IS NULL
            ORDER BY pl.updated_at ASC
        """).fetchall()

        lines = [f"\n{C.BOLD}  ┌─ FOLLOW-UP QUEUE {'─' * (self.WIDTH - 22)}┐{C.RESET}"]

        if not followups and not stale:
            lines.append(f"  │  {C.DIM}No follow-ups pending{C.RESET}")
        else:
            if followups:
                lines.append(f"  │  {C.GREEN}Due now:{C.RESET}")
                for f in followups[:5]:
                    f = dict(f)
                    name = f.get("name", "?")[:20]
                    stage = f.get("stage", "?")
                    score = f.get("lead_score") or "—"
                    lines.append(f"  │    {C.BOLD}{name:<22}{C.RESET} {stage:<14} score: {score}")
                if len(followups) > 5:
                    lines.append(f"  │    {C.DIM}... and {len(followups) - 5} more{C.RESET}")

            if stale:
                lines.append(f"  │  {C.YELLOW}⚠ Unscheduled (opener_sent, no follow-up date):{C.RESET}")
                for s in stale[:5]:
                    s = dict(s)
                    name = (s.get("name") or "?")[:20]
                    try:
                        updated = datetime.fromisoformat(s["updated_at"])
                        days_ago = (now - updated).days
                        age_str = f"{days_ago}d ago"
                    except (ValueError, TypeError):
                        age_str = "?"
                    lines.append(f"  │    {name:<22} sent {age_str}")
                if len(stale) > 5:
                    lines.append(f"  │    {C.DIM}... and {len(stale) - 5} more{C.RESET}")

        lines.append(f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # RECENT ACTIVITY
    # ─────────────────────────────────────────────────────────────
    def _recent_activity(self) -> str:
        rows = self.db.conn.execute("""
            SELECT p.name, m.direction, m.sent_at,
                   SUBSTR(m.message_text, 1, 50) as preview
            FROM messages m
            JOIN prospects p ON p.id = m.prospect_id
            ORDER BY m.sent_at DESC LIMIT 8
        """).fetchall()

        lines = [f"\n{C.BOLD}  ┌─ RECENT ACTIVITY {'─' * (self.WIDTH - 22)}┐{C.RESET}"]

        if not rows:
            lines.append(f"  │  {C.DIM}No messages recorded yet{C.RESET}")
        else:
            for r in rows:
                r = dict(r)
                name = (r.get("name") or "?")[:16]
                direction = r["direction"]
                preview = (r.get("preview") or "")[:35]

                # Direction icon
                if direction == "outbound":
                    icon = f"{C.BLUE}→{C.RESET}"
                else:
                    icon = f"{C.GREEN}←{C.RESET}"

                # Format timestamp
                try:
                    ts = datetime.fromisoformat(r["sent_at"]).strftime("%m/%d %H:%M")
                except (ValueError, TypeError):
                    ts = "?"

                lines.append(f"  │  {icon} {name:<18} {ts}  {C.DIM}{preview}…{C.RESET}")

        lines.append(f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # MESSAGE QUALITY
    # ─────────────────────────────────────────────────────────────
    def _message_quality_summary(self) -> str:
        q_stats = self.scorer.score_recent_messages(days=7)
        
        # Color coding for quality
        q = q_stats["avg_quality"]
        if q >= 0.8:
            q_color = C.GREEN
        elif q >= 0.6:
            q_color = C.YELLOW
        else:
            q_color = C.RED
            
        # Color coding for risk (inverted)
        r = q_stats["avg_risk"]
        if r <= 0.2:
            r_color = C.GREEN
        elif r <= 0.5:
            r_color = C.YELLOW
        else:
            r_color = C.RED

        lines = [
            f"\n{C.BOLD}  ┌─ MESSAGE QUALITY (last 7 days) {'─' * (self.WIDTH - 36)}┐{C.RESET}",
            f"  │  Avg Quality:      {q_color}{q:.2f}{C.RESET}  (>0.6 is good)",
            f"  │  Avg Risk:         {r_color}{r:.2f}{C.RESET}  (<0.5 is good)",
            f"  │  Avg Similarity:   {q_stats['avg_similarity']:.2f}",
            f"  │  Avg Personal:     {q_stats['avg_personalization']:.2f}",
            f"  │  Auto-blocked:     {q_stats['blocked_count']}",
            f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}",
        ]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # REPLY METRICS
    # ─────────────────────────────────────────────────────────────
    def _reply_metrics(self) -> str:
        stats = self.db.get_stats()
        messaged = stats["total_messaged"]
        replies = stats["total_replies"]
        reply_rate = (replies / messaged * 100) if messaged > 0 else 0

        # Conversion funnel
        pipeline = stats.get("pipeline", {})
        interested = pipeline.get("interested", 0)
        form_sent = pipeline.get("form_sent", 0)
        converted = pipeline.get("converted", 0)

        # Color code reply rate
        if reply_rate >= 20:
            rate_color = C.GREEN
        elif reply_rate >= 10:
            rate_color = C.YELLOW
        else:
            rate_color = C.RED

        lines = [
            f"\n{C.BOLD}  ┌─ REPLY METRICS {'─' * (self.WIDTH - 20)}┐{C.RESET}",
            f"  │  Reply Rate:   {rate_color}{C.BOLD}{reply_rate:.1f}%{C.RESET}  ({replies}/{messaged})",
            f"  │  Interested:   {C.BOLD}{interested}{C.RESET}",
            f"  │  Form Sent:    {C.BOLD}{form_sent}{C.RESET}",
            f"  │  Converted:    {C.GREEN}{C.BOLD}{converted}{C.RESET}",
            f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}",
        ]
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────
    # RISK ALERTS — ANOMALY DETECTION
    # ─────────────────────────────────────────────────────────────
    def _risk_alerts(self) -> str:
        alerts = self._detect_anomalies()

        lines = [f"\n{C.BOLD}  ┌─ RISK ALERTS {'─' * (self.WIDTH - 18)}┐{C.RESET}"]

        if not alerts:
            lines.append(f"  │  {C.GREEN}✓ No anomalies detected{C.RESET}")
        else:
            for severity, message in alerts:
                if severity == "critical":
                    icon = f"{C.RED}{C.BOLD}⚠{C.RESET}"
                    color = C.RED
                elif severity == "warning":
                    icon = f"{C.YELLOW}⚠{C.RESET}"
                    color = C.YELLOW
                else:
                    icon = f"{C.BLUE}ℹ{C.RESET}"
                    color = C.CYAN

                lines.append(f"  │  {icon} {color}{message}{C.RESET}")

        lines.append(f"{C.BOLD}  └{'─' * (self.WIDTH - 3)}┘{C.RESET}")
        return "\n".join(lines)

    def _detect_anomalies(self) -> list[tuple[str, str]]:
        """Run anomaly detection rules against current data. Returns [(severity, message)]."""
        alerts = []
        stats = self.db.get_stats()
        now = datetime.now()

        # ── 1. Reply rate critically low ──
        messaged = stats["total_messaged"]
        replies = stats["total_replies"]
        if messaged >= 5 and replies == 0:
            alerts.append(("critical", f"Reply rate: 0% ({replies}/{messaged} — zero replies)"))
        elif messaged >= 10:
            rate = (replies / messaged) * 100
            if rate < 10:
                alerts.append(("warning", f"Reply rate low: {rate:.0f}% ({replies}/{messaged})"))

        # ── 2. Overdue follow-ups ──
        overdue = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM pipeline
            WHERE next_followup_at IS NOT NULL
              AND next_followup_at < ?
              AND stage NOT IN ('converted', 'dead')
        """, ((now - timedelta(days=7)).isoformat(),)).fetchone()["c"]
        if overdue > 0:
            alerts.append(("critical", f"Follow-ups overdue > 7 days: {overdue} prospects"))

        # ── 3. Unscheduled follow-ups ──
        unscheduled = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM pipeline
            WHERE stage = 'opener_sent' AND next_followup_at IS NULL
        """).fetchone()["c"]
        if unscheduled > 0:
            alerts.append(("warning", f"Unscheduled follow-ups: {unscheduled} opener_sent with no date"))

        # ── 4. Pipeline stagnation ──
        recent_changes = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM pipeline
            WHERE updated_at > ?
              AND stage NOT IN ('new', 'dead')
        """, ((now - timedelta(days=7)).isoformat(),)).fetchone()["c"]
        pipeline_active = sum(
            v for k, v in stats.get("pipeline", {}).items()
            if k not in ("new", "dead")
        )
        if pipeline_active > 0 and recent_changes == 0:
            alerts.append(("warning", "Pipeline stalled — 0 stage progressions in 7 days"))

        # ── 5. Session crash rate ──
        recent_crashes = self.db.conn.execute("""
            SELECT COUNT(*) as c FROM sessions
            WHERE status = 'crashed' AND started_at > ?
        """, ((now - timedelta(days=7)).isoformat(),)).fetchone()["c"]
        if recent_crashes >= 3:
            alerts.append(("critical", f"System instability: {recent_crashes} crashed sessions in 7 days"))
        elif recent_crashes >= 1:
            alerts.append(("info", f"Crashed sessions in last 7 days: {recent_crashes}"))

        # ── 6. Daily budget burn rate ──
        sent_today = stats["today_sent"]
        if sent_today >= 10 and now.hour < 14:
            alerts.append(("warning", f"Budget burning fast: {sent_today} sent before 2 PM"))

        # ── 7. No activity in 3+ days ──
        last_msg = self.db.conn.execute("""
            SELECT MAX(sent_at) as last FROM messages
        """).fetchone()["last"]
        if last_msg:
            try:
                last_dt = datetime.fromisoformat(last_msg)
                days_silent = (now - last_dt).days
                if days_silent >= 7:
                    alerts.append(("critical", f"System inactive for {days_silent} days"))
                elif days_silent >= 3:
                    alerts.append(("warning", f"No outreach activity for {days_silent} days"))
            except (ValueError, TypeError):
                pass

        return alerts

    # ─────────────────────────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────────────────────────
    def _footer(self, now: datetime) -> str:
        return (
            f"\n{C.CYAN}{'═' * self.WIDTH}{C.RESET}\n"
            f"{C.DIM}  Ctrl+C to exit  |  Data: data-tracking/outreach.db{C.RESET}\n"
        )


# ═══════════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
def main():
    # Force UTF-8 output on Windows (cp1252 can't render box-drawing chars)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )

    parser = argparse.ArgumentParser(
        description="Outreach OS — CLI Operational Dashboard"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Single snapshot, then exit"
    )
    parser.add_argument(
        "--compact", action="store_true",
        help="Compact mode — fewer sections"
    )
    parser.add_argument(
        "--export", action="store_true",
        help="Plain text output (no ANSI colors)"
    )
    parser.add_argument(
        "--interval", type=int, default=30,
        help="Refresh interval in seconds (default: 30)"
    )
    args = parser.parse_args()

    if args.export:
        C.disable()

    db = OutreachDB()
    dashboard = OutreachDashboard(db, compact=args.compact)

    if args.once or args.export:
        print(dashboard.render())
        db.close()
        return

    # ── Live refresh loop ──
    try:
        while True:
            # Clear screen (Windows + Unix)
            os.system("cls" if os.name == "nt" else "clear")
            print(dashboard.render())
            print(f"{C.DIM}  Refreshing in {args.interval}s...{C.RESET}", end="", flush=True)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n\n{C.CYAN}  Dashboard closed.{C.RESET}\n")
    finally:
        db.close()


if __name__ == "__main__":
    main()
