#!/usr/bin/env python3
"""
clstr.in LinkedIn Inbox Reply Agent — browser-use + Ollama (v2)
================================================================
Production-grade inbox agent with:
  - SQLite memory (conversation history, pipeline tracking)
  - Safety governor (daily caps, cooldown)
  - Crash recovery via checkpoints
  - Deterministic navigation + AI-only-for-decisions
  - Optimized Ollama params for 16GB RAM

Usage:
  python clstr_browseruse_inbox.py
"""

import asyncio
import json
import os
import random
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserProfile
from browser_use import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from outreach_db import OutreachDB, normalize_url
from safety_governor import SafetyGovernor

# ── Load .env ──────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("clstr_inbox")

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════
MAX_REPLIES = 10
FORM_URL = "https://forms.gle/2NYjiunqeUk3WUDh9"
PHONE = "9441467303"
CHROME_PROFILE = Path("data-tracking/chrome-profile")

# ═══════════════════════════════════════════════════════════════════
# CONTEXTUAL REPLY LOGIC — Ganesh's actual voice
# ═══════════════════════════════════════════════════════════════════
def contextual_reply(their_msg: str) -> str:
    """Reply in Ganesh's actual tone — short, raw, peer-to-peer."""
    m = their_msg.lower()

    # They want to know what clstr is
    if any(w in m for w in ["what is", "tell me", "what's clstr", "more about", "what does", "explain", "clstr kya"]):
        return random.choice([
            "clstr.in is basically a campus network — verified, private to each college. students connect with batchmates, alumni, real opportunities. we're onboarding campus leaders to shape how it rolls out. what does your college community look like rn?",
            "its a verified campus network bro — think of it like a private space for your college where students actually connect with each other and with opportunities. we're building the campus layer. what's the vibe at your college like?",
        ])

    # Positive / interested
    if any(w in m for w in ["interested", "want to join", "how do i apply", "sign me up", "i'm in", "i am in",
                             "count me in", "sounds good", "love to", "definitely", "sure", "yes", "okay", "ok", "great"]):
        return f"perfect, fill this quick form and we'll take it from there: {FORM_URL}\n\ntakes 2 mins. we'll reach out within 48hrs. ping me on whatsapp if you have questions — {PHONE}"

    # They're busy
    if any(w in m for w in ["busy", "exams", "later", "not now", "maybe later", "semester"]):
        return random.choice([
            "that makes sense bro, take your time. i'll check back in a couple weeks",
            "all good, good luck with the exams. i'll follow up later",
        ])

    # Asking about time commitment
    if any(w in m for w in ["how many hours", "commitment", "time required", "how much time"]):
        return "flexible — roughly 3-5 hrs a week. you'd run campus activations and community stuff at your college. want me to send you the form so you can check role details?"

    # Asking about pay / compensation
    if any(w in m for w in ["pay", "paid", "salary", "stipend", "money", "compensation"]):
        return random.choice([
            "honestly not right now — we're early stage. but the experience of actually building something from ground up and leading at your campus is real. once we hit revenue we move to proper incentives",
            "not in a position to pay rn bro, we're early. but this isn't a college project — we're building it seriously. if you stay long term it turns into something real",
        ])

    # Generic positive but unclear
    if any(w in m for w in ["interesting", "nice", "cool", "wow", "good idea"]):
        return random.choice([
            "hm, what specifically caught your interest?",
            "what's your current role at college? curious if there's a fit",
        ])

    # Default — keep it going naturally
    return random.choice([
        "which college are you at?",
        "what year are you in bro?",
        "what are you mainly focused on at college rn?",
    ])


def detect_reply_sentiment(their_msg: str) -> str:
    """Detect sentiment of their reply for pipeline tracking."""
    m = their_msg.lower()
    if any(w in m for w in ["interested", "want to join", "sign me up", "i'm in",
                             "sounds good", "love to", "definitely", "sure", "yes"]):
        return "positive"
    if any(w in m for w in ["no", "not interested", "stop", "don't", "unsubscribe"]):
        return "negative"
    if any(w in m for w in ["busy", "exams", "later", "not now"]):
        return "deferred"
    if any(w in m for w in ["what is", "tell me", "more about"]):
        return "curious"
    return "neutral"


def determine_pipeline_stage(sentiment: str) -> str:
    """Map sentiment to pipeline stage."""
    mapping = {
        "positive": "interested",
        "negative": "dead",
        "deferred": "busy",
        "curious": "replied",
        "neutral": "replied",
    }
    return mapping.get(sentiment, "replied")


# ═══════════════════════════════════════════════════════════════════
# CUSTOM CONTROLLER TOOLS
# ═══════════════════════════════════════════════════════════════════
controller = Controller()

# Global state — initialized in main()
_state = {
    "db": None,
    "governor": None,
    "session_id": None,
}


class ReplyGenInput(BaseModel):
    their_last_message: str
    conversation_name: str = ""
    profile_url: str = ""


class ReplyGenResult(BaseModel):
    reply: str
    sentiment: str
    pipeline_stage: str


class RecordReplyInput(BaseModel):
    conversation_name: str
    their_message: str
    our_reply: str
    profile_url: str = ""


class HumanDelayInput(BaseModel):
    min_seconds: float = 8.0
    max_seconds: float = 15.0


class HumanDelayResult(BaseModel):
    waited_seconds: float


# ── Deterministic navigation tools ────────────────────────────────

@controller.action("Navigate directly to LinkedIn messaging inbox — deterministic")
async def navigate_to_inbox(browser) -> str:
    """Deterministic navigation — go directly to inbox."""
    page = await browser.get_current_page()
    await page.goto("https://www.linkedin.com/messaging/", wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    log.info("  Navigated to LinkedIn inbox")
    return "At LinkedIn messaging inbox"


# ── Intelligence tools ────────────────────────────────────────────

@controller.action("Generate a contextual reply in Ganesh's tone based on their message, with sentiment tracking")
async def gen_reply(params: ReplyGenInput) -> ReplyGenResult:
    reply = contextual_reply(params.their_last_message)
    sentiment = detect_reply_sentiment(params.their_last_message)
    stage = determine_pipeline_stage(sentiment)
    log.info(f"  Reply generated (sentiment={sentiment}): {reply[:80]}...")
    return ReplyGenResult(reply=reply, sentiment=sentiment, pipeline_stage=stage)


@controller.action("Record a reply that was successfully sent to SQLite database")
async def record_reply(params: RecordReplyInput) -> str:
    db = _state["db"]
    governor = _state["governor"]
    session_id = _state["session_id"]

    # Try to find the prospect by URL
    prospect_id = None
    if params.profile_url:
        url = normalize_url(params.profile_url)
        prospect = db.get_prospect_by_url(url)
        if prospect:
            prospect_id = prospect["id"]

    # If we have a prospect, record conversation
    if prospect_id:
        # Record their inbound message
        db.record_message(
            prospect_id=prospect_id,
            direction="inbound",
            message_text=params.their_message,
            session_id=session_id,
        )

        # Record our outbound reply
        db.record_message(
            prospect_id=prospect_id,
            direction="outbound",
            message_text=params.our_reply,
            session_id=session_id,
            approved_by="auto",
        )

        # Update pipeline based on sentiment
        sentiment = detect_reply_sentiment(params.their_message)
        stage = determine_pipeline_stage(sentiment)
        db.update_pipeline(
            prospect_id=prospect_id,
            stage=stage,
            sentiment=sentiment,
        )

        log.info(f"  Recorded reply for {params.conversation_name} (stage={stage})")
    else:
        log.info(f"  Recorded reply for {params.conversation_name} (no prospect match)")

    # Save checkpoint
    db.save_checkpoint(
        session_id=session_id,
        step="reply_sent",
        data=json.dumps({
            "conversation": params.conversation_name,
            "their_message": params.their_message[:100],
            "our_reply": params.our_reply[:100],
        }),
    )

    governor.record_send_success()

    status = governor.get_status()
    return f"Recorded. Replies sent: {status['session_sent']}/{status['session_limit']}"


@controller.action("Wait a random human-like delay between inbox actions")
async def human_delay(params: HumanDelayInput) -> HumanDelayResult:
    governor = _state["governor"]
    d = random.uniform(params.min_seconds, params.max_seconds)
    log.info(f"  Human delay: {d:.0f}s")
    await asyncio.sleep(d)
    return HumanDelayResult(waited_seconds=round(d, 1))


@controller.action("Get current inbox session status")
async def inbox_status() -> str:
    governor = _state["governor"]
    db = _state["db"]
    status = governor.get_status()
    stats = db.get_stats()
    return (
        f"Replies sent: {status['session_sent']}/{status['session_limit']}. "
        f"Daily total: {status['daily_limit'] - status['daily_remaining']}/{status['daily_limit']}. "
        f"Total replies in DB: {stats['total_replies']}. "
        f"Can send more: {status['can_send']}."
    )


# ═══════════════════════════════════════════════════════════════════
# TASK PROMPT
# ═══════════════════════════════════════════════════════════════════
INBOX_TASK = f"""
You are Ganesh Tappiti's LinkedIn inbox reply agent for clstr.in.
Your job is to check the LinkedIn inbox, read full conversation threads, and reply to
unread messages in Ganesh's authentic, casual tone.

## HARD RULES — NEVER BREAK
1. Reply to at most {MAX_REPLIES} conversations this session. After {MAX_REPLIES}, STOP.
2. Process ONE conversation at a time.
3. ALWAYS read the FULL conversation thread before replying — scroll to the top first.
4. NEVER reply if the last message in the thread was sent BY YOU (that's double-messaging).
5. NEVER reply to sponsored messages, LinkedIn system notifications, or InMail ads.
6. After each reply, call `human_delay` (8-15 seconds) before the next conversation.

## WORKFLOW
1. Call `navigate_to_inbox` to go directly to the messaging page.
2. Look for conversations with unread indicators (blue dot, bold text, or notification badge).
3. For each unread conversation (up to {MAX_REPLIES}):
   a. Click on the conversation.
   b. SCROLL TO THE TOP of the thread. Read EVERY message exchanged.
   c. Determine the context:
      - Who sent the last message? If it was YOU (Ganesh), SKIP — do not double-message.
      - Is this a real human reply? If it's LinkedIn system/sponsored, SKIP.
   d. Read their LAST message carefully.
   e. Call `gen_reply` with their last message text (and profile_url if visible).
   f. Type the reply CHARACTER BY CHARACTER (30-80ms per char) into the compose box.
   g. DO NOT paste. Type each character individually.
   h. Click Send.
   i. Call `record_reply` with the conversation name, their message, your reply, and profile_url if available.
   j. Call `human_delay` before moving to the next conversation.
4. When done, call `inbox_status` and report the summary.

## REPLY CONTEXT RULES
Based on what they said:
- "what is clstr" / "tell me more" → Explain in 2 lines, end with campus question
- Positive ("interested", "sure", "yes", "sounds good") → Share form: {FORM_URL} + WhatsApp: {PHONE}
- Busy ("exams", "later", "not now") → No pressure, "i'll follow up later"
- Pay/stipend question → Honest: early stage, no pay yet, real ownership + experience
- Time commitment question → "3-5 hrs a week, campus activations"
- Generic positive ("cool", "nice") → Ask one clarifying question
- Detailed skill answer → Pick ONE specific skill and connect it
- Unknown → Ask what college/year/focus they have

## MESSAGE TONE
- Max 2 sentences
- Casual — "bro", first name, direct
- Acknowledge what they specifically said
- Sound like a 21-year-old founder, not a recruiter
- No corporate language, no emoji overload

## ANTI-DETECTION
- Type replies character by character (30-80ms per char)
- Random delays between conversations
- If you encounter CAPTCHA or security check, STOP immediately

## ON COMPLETION
Report how many conversations you replied to and a brief summary.
"""


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
async def main():
    # Initialize SQLite database
    db = OutreachDB()

    # Recover any crashed sessions
    crashed = db.recover_crashed_sessions()
    if crashed:
        log.warning(f"Recovered {crashed} crashed session(s) from previous runs")

    # Initialize safety governor
    governor = SafetyGovernor(db)

    # Pre-session safety check
    can_start, reason = governor.can_start_session("inbox")
    # if not can_start:
    #     log.error(f"CANNOT START: {reason}")
    #     db.close()
    #     return

    # Start session
    session_id = db.start_session("inbox")

    # Set global state
    _state["db"] = db
    _state["governor"] = governor
    _state["session_id"] = session_id

    stats = db.get_stats()
    log.info(f"\n{'=' * 60}")
    log.info("clstr.in Inbox Reply v2 — browser-use + Ollama + SQLite")
    log.info(f"Session: {session_id}")
    log.info(f"Max replies: {MAX_REPLIES}")
    can_send, remaining = db.can_send_today(governor.MAX_DMS_PER_DAY)
    log.info(f"Messages remaining today: {remaining}")
    log.info(f"Total replies tracked: {stats['total_replies']}")
    log.info(f"{'=' * 60}\n")

    Path("data-tracking").mkdir(exist_ok=True)

    profile = BrowserProfile(
        user_data_dir=str(CHROME_PROFILE.resolve()),
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--start-maximized",
        ],
        disable_security=False,
        keep_alive=True,
        wait_between_actions=1.5,
        minimum_wait_page_load_time=3.0,
        wait_for_network_idle_page_load_time=3.0,
        highlight_elements=False,
    )

    # Load Gemini API key
    api_key = (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
    )
    if not api_key:
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                k = line.strip()
                if ("GOOGLE_API_KEY=" in k or "GEMINI_API_KEY=" in k) and "=" in k:
                    val = k.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        api_key = val
                        break
    if not api_key:
        log.error("No GOOGLE_API_KEY found. Add to .env: GOOGLE_API_KEY=your_key")
        db.close()
        return

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=0.3,
    )

    agent = Agent(
        task=INBOX_TASK,
        llm=llm,
        browser_profile=profile,
        controller=controller,
        max_failures=3,
        max_actions_per_step=3,
        use_vision=False,
        generate_gif=False,
    )

    try:
        result = await agent.run()

        db.end_session(session_id, "completed")

        final_stats = db.get_stats()
        log.info(f"\n{'=' * 60}")
        log.info(f"INBOX AGENT COMPLETE — Session: {session_id}")
        log.info(f"Replies sent: {governor._session_send_count}")
        log.info(f"Total sent today: {final_stats['today_sent']}")
        log.info(f"Pipeline: {final_stats['pipeline']}")
        log.info(f"Database: data-tracking/outreach.db")
        log.info(f"{'=' * 60}\n")

        return result

    except KeyboardInterrupt:
        log.info("Session stopped by user (Ctrl+C)")
        db.end_session(session_id, "stopped")
    except Exception as e:
        log.error(f"Session crashed: {e}")
        db.end_session(session_id, "crashed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
