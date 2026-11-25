#!/usr/bin/env python3
"""Dry-run test: verifies all imports, configs, and agent init work."""

import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"

def main():
    passed = 0
    failed = 0

    # -- Test 1: All imports --
    print("=== Test 1: Import Check ===")
    try:
        from browser_use import Agent, Browser, BrowserProfile, Controller
        from langchain_ollama import ChatOllama
        from pydantic import BaseModel
        from dotenv import load_dotenv
        print("  [OK] All imports work")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        failed += 1
        return 1  # Can't continue without imports

    # -- Test 2: .env loading --
    print("\n=== Test 2: .env Loading ===")
    try:
        load_dotenv()
        email = os.getenv("LINKEDIN_EMAIL")
        model = os.getenv("OLLAMA_MODEL")
        assert email, "LINKEDIN_EMAIL not set"
        assert model, "OLLAMA_MODEL not set"
        print(f"  [OK] LINKEDIN_EMAIL = {email}")
        print(f"  [OK] OLLAMA_MODEL   = {model}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] .env failed: {e}")
        failed += 1

    # -- Test 3: Outreach script module import --
    print("\n=== Test 3: Outreach Module ===")
    try:
        import clstr_browseruse_outreach as outreach
        assert outreach.MAX_PER_ROUND == 10
        assert len(outreach.TEMPLATES) >= 9
        messaged_count = len(outreach._round_state["messaged"])
        print(f"  [OK] MAX_PER_ROUND   = {outreach.MAX_PER_ROUND}")
        print(f"  [OK] TEMPLATES keys  = {list(outreach.TEMPLATES.keys())}")
        print(f"  [OK] Messaged count  = {messaged_count}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Outreach module failed: {e}")
        failed += 1

    # -- Test 4: Inbox script module import --
    print("\n=== Test 4: Inbox Module ===")
    try:
        import clstr_browseruse_inbox as inbox
        assert inbox.MAX_REPLIES == 10
        print(f"  [OK] MAX_REPLIES     = {inbox.MAX_REPLIES}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Inbox module failed: {e}")
        failed += 1

    # -- Test 5: Message generation --
    print("\n=== Test 5: Message Generation ===")
    try:
        msg = outreach.generate_message("Rahul", "VIT Vellore", "campus_ambassador", "")
        assert "rahul" in msg.lower()
        assert len(msg) <= 320
        print(f"  [OK] Sample msg: {msg}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Message gen failed: {e}")
        failed += 1

    # -- Test 6: Signal detection --
    print("\n=== Test 6: Signal Detection ===")
    try:
        sig, detail = outreach.detect_signal("Campus Ambassador at JNTU Hyderabad, organized TEDx event")
        assert sig == "tedx"
        print(f"  [OK] TEDx detected: signal={sig}, detail={detail}")

        sig2, _ = outreach.detect_signal("President of Coding Club at IIT Delhi")
        assert sig2 == "club_president"
        print(f"  [OK] Club president detected: signal={sig2}")

        sig3, _ = outreach.detect_signal("Random student profile with no keywords")
        assert sig3 == "default"
        print(f"  [OK] Default fallback: signal={sig3}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Signal detection failed: {e}")
        failed += 1

    # -- Test 7: Contextual reply --
    print("\n=== Test 7: Contextual Reply ===")
    try:
        reply1 = inbox.contextual_reply("What is clstr exactly?")
        assert "campus" in reply1.lower() or "clstr" in reply1.lower()
        print(f"  [OK] 'what is clstr' reply OK")

        reply2 = inbox.contextual_reply("Yes I'm interested!")
        assert outreach.FORM_URL in reply2
        print(f"  [OK] Positive reply includes form URL")

        reply3 = inbox.contextual_reply("I have exams right now")
        assert "later" in reply3.lower() or "follow up" in reply3.lower()
        print(f"  [OK] Busy reply OK")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Contextual reply failed: {e}")
        failed += 1

    # -- Test 8: LLM init (no actual call) --
    print("\n=== Test 8: LLM Init ===")
    try:
        llm = ChatOllama(model="qwen2.5:7b", temperature=0.3, num_ctx=8192)
        assert llm.model == "qwen2.5:7b"
        print(f"  [OK] LLM model: {llm.model}")
        print(f"  [OK] LLM ready (no call made)")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] LLM init failed: {e}")
        failed += 1

    # -- Test 9: BrowserProfile config --
    print("\n=== Test 9: BrowserProfile Config ===")
    try:
        profile = BrowserProfile(
            user_data_dir=str(Path("data-tracking/chrome-profile").resolve()),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            highlight_elements=False,
        )
        assert profile.user_data_dir is not None
        assert profile.headless is False
        print(f"  [OK] Profile dir: {profile.user_data_dir}")
        print(f"  [OK] Headless: {profile.headless}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] BrowserProfile config failed: {e}")
        failed += 1

    # -- Test 10: Dedup file integrity --
    print("\n=== Test 10: Dedup File Integrity ===")
    try:
        import json
        messaged = outreach.load_messaged()
        assert isinstance(messaged, set)
        print(f"  [OK] Loaded {len(messaged)} messaged profiles")
        data = json.loads(Path("data-tracking/messaged_profiles.json").read_text())
        assert isinstance(data, list)
        print(f"  [OK] messaged_profiles.json is valid JSON list")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] Dedup file check failed: {e}")
        failed += 1

    # -- Summary --
    print(f"\n{'=' * 50}")
    total = passed + failed
    if failed == 0:
        print(f"ALL {passed}/{total} TESTS PASSED -- dry-run OK")
    else:
        print(f"RESULT: {passed} passed, {failed} failed out of {total}")
    print(f"{'=' * 50}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
