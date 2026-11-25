#!/usr/bin/env python3
"""
daily_ops.py — Unified Operator CLI for clstr.in Outreach
=========================================================
Codifies the 2-session/day workflow into a single human-operator tool.
This is NOT a new agent; it orchestrates existing modules.

Usage:
  python daily_ops.py morning    # Full morning workflow (Inbox -> Outreach)
  python daily_ops.py evening    # Full evening workflow (Follow-ups)
  python daily_ops.py status     # Quick status check
  python daily_ops.py preflight  # Pre-session safety checklist
"""

import sys
import argparse
import subprocess
import logging
from datetime import datetime
import sqlite3
import requests

from outreach_db import OutreachDB
from safety_governor import SafetyGovernor
from message_quality import MessageScorer

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("daily_ops")

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title.upper()} ".center(60, "="))
    print("=" * 60 + "\n")

def print_step(step_num: int, title: str):
    print(f"\n[Step {step_num}] {title}")
    print("-" * 40)

# ═══════════════════════════════════════════════════════════════════
# PREFLIGHT CHECKS
# ═══════════════════════════════════════════════════════════════════
def check_ollama() -> bool:
    """Check if Ollama is running and responsive."""
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=2)
        if res.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def check_db() -> tuple[bool, str]:
    """Check if SQLite DB is accessible."""
    try:
        db = OutreachDB()
        stats = db.get_stats()
        db.close()
        return True, f"OK ({stats['total_prospects']} prospects)"
    except Exception as e:
        return False, str(e)

def run_preflight() -> bool:
    """Run all pre-session safety checks."""
    print_header("preflight safety checks")
    
    all_passed = True
    
    # 1. Check Ollama
    print("Checking Ollama... ", end="")
    if check_ollama():
        print("[OK] Running")
    else:
        print("[FAIL] NOT RESPONDING (Ensure Ollama is running)")
        all_passed = False
        
    # 2. Check Database
    print("Checking Database... ", end="")
    db_ok, db_msg = check_db()
    if db_ok:
        print(f"[OK] {db_msg}")
    else:
        print(f"[FAIL] FAILED: {db_msg}")
        all_passed = False
        
    # 3. Check Safety Governor Limits
    print("Checking Safety Budget... ", end="")
    try:
        db = OutreachDB()
        gov = SafetyGovernor(db)
        
        can_start, reason = gov.can_start_session("outreach")
        if can_start:
            print("[OK] OK to start session")
        else:
            print(f"[BLOCKED] {reason}")
            # Don't fail the whole preflight, just block the session start later
            
        # Check specific Phase 1 limits
        p1 = gov.get_phase1_status()
        print(f"  - Openers: {p1['openers_sent_today']}/{p1['openers_limit']} sent today")
        print(f"  - Follow-ups: {p1['followups_sent_today']}/{p1['followups_limit']} sent today")
        
        db.close()
    except Exception as e:
        print(f"[FAIL] ERROR: {e}")
        all_passed = False

    print("\nPreflight Status: ", end="")
    if all_passed:
        print("[OK] ALL SYSTEMS GO")
    else:
        print("[FAIL] ISSUES DETECTED")
        
    return all_passed

# ═══════════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════════
def run_status():
    """Quick status check without the full dashboard."""
    print_header("system status")
    
    db = OutreachDB()
    gov = SafetyGovernor(db)
    scorer = MessageScorer(db)
    
    p1 = gov.get_phase1_status()
    stats = db.get_stats()
    q_stats = scorer.score_recent_messages(days=7)
    
    print("== BUDGET ==")
    print(f"Daily Limit:  {p1['daily_total']}/{p1['daily_limit']} used")
    print(f"Openers:      {p1['openers_sent_today']}/{p1['openers_limit']} used")
    print(f"Follow-ups:   {p1['followups_sent_today']}/{p1['followups_limit']} used")
    
    print("\n== PIPELINE ==")
    print(f"Total Prospects: {stats['total_prospects']}")
    for stage, count in stats["pipeline"].items():
        if count > 0:
            print(f"  - {stage}: {count}")
            
    print("\n== QUALITY (Last 7 days) ==")
    print(f"Messages Scored: {q_stats['count']}")
    print(f"Avg Quality:     {q_stats['avg_quality']:.2f}")
    print(f"Avg Risk:        {q_stats['avg_risk']:.2f}")
    print(f"Auto-blocked:    {q_stats['blocked_count']}")
    
    db.close()

# ═══════════════════════════════════════════════════════════════════
# WORKFLOWS
# ═══════════════════════════════════════════════════════════════════
def run_morning():
    """Morning workflow: Status -> Queue -> Preflight -> Recommendation"""
    print_header("morning workflow")
    
    print_step(1, "Daily Dashboard Snapshot")
    subprocess.run(["python", "outreach_dashboard.py", "--once"])
    
    print_step(2, "Follow-up Queue Preview")
    subprocess.run(["python", "followup_scheduler.py", "queue"])
    
    print_step(3, "System Preflight")
    passed = run_preflight()
    
    print_step(4, "Recommendation")
    if not passed:
        print("⚠️  Resolve preflight issues before starting.")
    else:
        print("👉 RECOMMENDED ACTION: Run Inbox Session -> Run Outreach Session")
        print("   Command 1: python clstr_browseruse_inbox.py")
        print("   Command 2: python clstr_browseruse_outreach.py --approve")

def run_evening():
    """Evening workflow: Status -> Preflight -> Recommendation"""
    print_header("evening workflow")
    
    print_step(1, "Daily Dashboard Snapshot")
    subprocess.run(["python", "outreach_dashboard.py", "--once"])
    
    print_step(2, "Pending Follow-ups")
    subprocess.run(["python", "followup_scheduler.py", "queue"])
    
    print_step(3, "System Preflight")
    passed = run_preflight()
    
    print_step(4, "Recommendation")
    if not passed:
        print("⚠️  Resolve preflight issues before starting.")
    else:
        print("👉 RECOMMENDED ACTION: Process Follow-ups")
        print("   Command: python followup_scheduler.py review")

# ═══════════════════════════════════════════════════════════════════
# CLI ENTRY
# ═══════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="Unified Operator CLI for clstr.in Outreach")
    parser.add_argument("command", choices=["morning", "evening", "status", "preflight"],
                        help="The operation to perform")
    
    args = parser.parse_args()
    
    if args.command == "morning":
        run_morning()
    elif args.command == "evening":
        run_evening()
    elif args.command == "status":
        run_status()
    elif args.command == "preflight":
        run_preflight()

if __name__ == "__main__":
    main()
