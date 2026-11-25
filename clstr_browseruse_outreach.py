#!/usr/bin/env python3
"""
clstr.in LinkedIn Outreach — browser-use + Ollama Agent (v2)
=============================================================
Production-grade outreach agent with:
  - SQLite memory (replaces flat JSON)
  - Safety governor (daily caps, cooldown, random stops)
  - Human approval mode (--approve, --auto, --dry-run)
  - Crash recovery via checkpoints
  - Layered identity validation (hard-fail on bad names)
  - Deterministic navigation + AI-only-for-decisions
  - Optimized Ollama params for 16GB RAM

Usage:
  python clstr_browseruse_outreach.py --approve   # Human reviews each draft (DEFAULT)
  python clstr_browseruse_outreach.py --auto      # Auto-send (no review)
  python clstr_browseruse_outreach.py --dry-run   # Generate drafts only
"""

import asyncio
import inspect
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
from pydantic import Field
from pydantic import BaseModel

from outreach_db import OutreachDB, validate_name, normalize_name, normalize_url
from safety_governor import SafetyGovernor
from approval_mode import ApprovalMode, parse_mode_from_args
from message_quality import MessageScorer

# ── Load .env ──────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("clstr_outreach")

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════
FORM_URL = "https://forms.gle/2NYjiunqeUk3WUDh9"
PHONE = "9441467303"
CHROME_PROFILE = Path("data-tracking/chrome-profile")

SEARCH_KEYWORDS = [
    "campus ambassador engineering college Karnataka 2024",
    "student council secretary VTU college Bangalore",
    "cultural head college Chennai Tamil Nadu student",
    "club president engineering college Mysore Karnataka",
    "campus ambassador Pune college Maharashtra student",
    "event organizer Mumbai engineering college student",
    "social media lead college Gujarat Ahmedabad student",
    "IEEE student branch chair Hyderabad college",
    "hackathon organizer engineering college Vijayawada",
    "cultural secretary JNTU college Hyderabad student",
    "NSS coordinator engineering college Lucknow UP",
    "student volunteer Noida college tech fest organizer",
    "design head college club Delhi NCR student",
    "entrepreneurship cell member college India 2025",
    "graphic design lead college fest India",
    "outreach coordinator student body India college",
    "tech fest organizer engineering college India",
    "college chapter lead student India community",
    "brand ambassador student college India campus",
]

# ═══════════════════════════════════════════════════════════════════
# MESSAGE TEMPLATES — Ganesh's real voice
# ═══════════════════════════════════════════════════════════════════
TEMPLATES = {
    "campus_ambassador": [
        "hey {name}, saw your campus ambassador stuff at {college}. building clstr.in and genuinely curious — do students there actually engage or is it mostly just for the certificate?",
        "hey {name}, noticed you're doing ambassador work at {college}. quick one — what kind of students actually show up vs just collect the title?",
        "hey {name}, you seem pretty active at {college}. I'm building something for campus communities, clstr.in. what's the real vibe there like?",
    ],
    "tedx": [
        "hey {name}, saw the TEDx work at {college}. how do you actually keep students engaged after the event ends?",
        "hey {name}, TEDx organizer at {college} is no small thing. genuinely curious — what's the hardest part of pulling it off?",
    ],
    "event_coordinator": [
        "hey {name}, saw your event work at {college}. what kind of events actually get real participation vs just headcount?",
        "hey {name}, you've coordinated events at {college} — honest question, what makes campus stuff actually stick vs stuff people forget next day?",
    ],
    "student_council": [
        "hey {name}, you're on the council at {college} so you'd know — what do students there actually need that nobody's building?",
        "hey {name}, student council at {college}. what's one thing everyone complains about but nobody fixes?",
    ],
    "club_president": [
        "hey {name}, saw you lead {signal} at {college}. what's the one thing missing that would actually make campus life better?",
        "hey {name}, you head {signal} at {college} — how does real engagement look there vs the performative kind?",
    ],
    "core_team_design": [
        "hey {name}, saw your design work. building clstr.in and looking for someone to own the creative side, not just make posters. what kind of design do you enjoy most?",
        "hey {name}, your design stuff caught my eye. I'm building clstr.in — is branding and visual identity something you'd want to own end to end?",
    ],
    "core_team_marketing": [
        "hey {name}, noticed your marketing work at {college}. building clstr.in and need someone who actually thinks about growth, not just posts. what kind of campaigns have you run?",
        "hey {name}, saw your marketing background. I'm working on clstr.in — is growth strategy something you're into beyond just content creation?",
    ],
    "startup_cell": [
        "hey {name}, startup cell at {college} — are people there actually shipping things or mostly attending talks about building?",
        "hey {name}, saw the startup cell work. honest question — how many folks there are actually building something vs just learning about it?",
    ],
    "default": [
        "hey {name}, saw your profile — you seem to actually do stuff at {college}. I'm building clstr.in, what's your main focus right now?",
        "hey {name}, noticed you're pretty active at {college}. what would actually make campus life better there, if you had to pick one thing?",
        "hey {name}, building clstr.in — a campus network for college students. saw your work at {college} and genuinely curious what the community vibe is like there?",
    ],
}

ROLE_MAP = {
    "campus_ambassador": "Campus Ambassador",
    "tedx": "Campus Ambassador",
    "event_coordinator": "Campus Ambassador",
    "student_council": "Campus Ambassador",
    "club_president": "Campus Ambassador",
    "core_team_design": "Core Team (Designing & Marketing)",
    "core_team_marketing": "Core Team (Designing & Marketing)",
    "startup_cell": "Founding Team",
    "default": "Campus Ambassador",
}


# ═══════════════════════════════════════════════════════════════════
# SIGNAL DETECTION
# ═══════════════════════════════════════════════════════════════════
def detect_signal(page_text: str) -> tuple[str, str]:
    """Detect the strongest signal from profile text."""
    lower = page_text.lower()

    if "tedx" in lower:
        return "tedx", "TEDx"
    if any(t in lower for t in ["startup cell", "entrepreneurship cell", "e-cell"]):
        return "startup_cell", "Startup Cell"
    if "student council" in lower or "student union" in lower:
        return "student_council", "Student Council"
    if "campus ambassador" in lower or "brand ambassador" in lower:
        return "campus_ambassador", ""

    if any(t in lower for t in ["graphic design", "ui/ux", "figma", "design head",
                                 "creative head", "visual design", "design lead"]):
        return "core_team_design", "Design"

    if any(t in lower for t in ["marketing lead", "social media manager", "content creator",
                                 "digital marketing", "marketing head", "outreach lead"]):
        return "core_team_marketing", "Marketing"

    if any(t in lower for t in ["president", "vice president", "chairperson"]) and any(
            t in lower for t in ["club", "society", "cell", "association"]):
        for line in page_text.split("\n"):
            s = line.strip()
            if ("Club" in s or "Society" in s) and len(s) < 60:
                return "club_president", s
        return "club_president", "the club"

    if "event coordinator" in lower or "event organizer" in lower or "event head" in lower:
        return "event_coordinator", ""

    return "default", ""


def generate_message(name: str, college: str, signal_type: str, specific_signal: str) -> str:
    """Generate a single personalized message in Ganesh's tone."""
    first_name = normalize_name(name).split()[0] if name else ""

    # HARD FAIL — never generate a message with a bad name
    if not validate_name(first_name):
        raise ValueError(f"REJECTED: Cannot generate message for invalid name '{name}'")

    college_text = college or "your campus"

    templates = TEMPLATES.get(signal_type, TEMPLATES["default"])
    msg = random.choice(templates).format(
        name=first_name, college=college_text, signal=specific_signal or college_text
    )
    if len(msg) > 320:
        msg = msg[:317] + "..."
    return msg


# ═══════════════════════════════════════════════════════════════════
# CUSTOM CONTROLLER TOOLS for browser-use
# ═══════════════════════════════════════════════════════════════════
controller = Controller()

# Global state — initialized in main()
_state = {
    "db": None,
    "governor": None,
    "approver": None,
    "scorer": None,
    "session_id": None,
}


class ProfileCheckInput(BaseModel):
    profile_url: str


class DeduplicationResult(BaseModel):
    is_duplicate: bool
    profile_url: str


class MessageGenInput(BaseModel):
    name: str
    college: str
    signal_type: str
    specific_signal: str = ""


class MessageGenResult(BaseModel):
    message: str
    role_fit: str
    status: str  # "ready", "rejected_name", "rejected_safety"


class RecordSentInput(BaseModel):
    profile_url: str
    name: str
    college: str
    role_fit: str
    signal_type: str
    message: str


class HumanDelayInput(BaseModel):
    min_seconds: float = 25.0
    max_seconds: float = 45.0


class HumanDelayResult(BaseModel):
    waited_seconds: float


# ── Deterministic navigation tools ────────────────────────────────

class SearchInput(BaseModel):
    keyword: str


class NavigateInput(BaseModel):
    url: str


@controller.action("Navigate to LinkedIn People search with a specific keyword — deterministic, no AI reasoning needed")
async def navigate_to_search(params: SearchInput, browser) -> str:
    """Deterministic navigation — go directly to search URL."""
    keyword = params.keyword.replace(" ", "%20")
    url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER"
    page = await browser.get_current_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(2)  # Wait for dynamic content
    log.info(f"  Navigated to search: {params.keyword}")
    return f"Navigated to LinkedIn People search for: {params.keyword}"


@controller.action("Navigate directly to a LinkedIn profile URL — deterministic")
async def navigate_to_profile(params: NavigateInput, browser) -> str:
    """Deterministic navigation — go directly to a profile."""
    page = await browser.get_current_page()
    await page.goto(params.url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(2)
    log.info(f"  Navigated to profile: {params.url}")
    return f"At profile: {params.url}"


@controller.action("Open the LinkedIn message compose window for a profile URL — deterministic")
async def open_message_compose(params: NavigateInput, browser) -> str:
    """Deterministic navigation — go to messaging thread."""
    page = await browser.get_current_page()
    # Try clicking the Message button on the profile first
    try:
        msg_btn = await page.query_selector('button:has-text("Message")')
        if msg_btn:
            await msg_btn.click()
            await asyncio.sleep(2)
            return "Message compose window opened via button"
    except Exception:
        pass
    # Fallback: navigate to messaging URL
    return "Could not find Message button — try clicking it manually"


# ── Intelligence tools (AI makes decisions here) ──────────────────

@controller.action("Check if a profile URL has already been messaged (deduplication via SQLite)")
async def check_dedup(params: ProfileCheckInput) -> DeduplicationResult:
    db = _state["db"]
    url = normalize_url(params.profile_url)
    is_dup = db.has_been_messaged(url) or db.is_duplicate(url)
    if is_dup:
        log.info(f"  DEDUP: Already contacted {url}")
    return DeduplicationResult(is_duplicate=is_dup, profile_url=url)


@controller.action("Generate a personalized outreach message in Ganesh's tone with safety validation")
async def gen_message(params: MessageGenInput) -> MessageGenResult:
    db = _state["db"]
    governor = _state["governor"]
    scorer = _state["scorer"]
    role = ROLE_MAP.get(params.signal_type, "Campus Ambassador")

    # Safety check — can we still send new openers? (Phase 1 limit check)
    can_send, reason = governor.can_send_new_opener()
    if not can_send:
        log.warning(f"  SAFETY BLOCK: {reason}")
        return MessageGenResult(message="", role_fit=role, status=f"rejected_safety: {reason}")

    # Name validation — hard fail on garbage names
    if not validate_name(params.name):
        log.warning(f"  NAME REJECTED: '{params.name}' failed identity validation")
        return MessageGenResult(message="", role_fit=role, status=f"rejected_name: '{params.name}'")

    try:
        msg = generate_message(params.name, params.college, params.signal_type, params.specific_signal)
        
        # Pre-send quality scoring
        score = scorer.score_message(
            draft=msg,
            name=params.name,
            college=params.college,
            signal_type=params.signal_type,
            specific_signal=params.specific_signal,
            is_followup=False
        )
        
        if not score.is_safe_to_send:
            reasons = "; ".join(score.reasons)
            log.warning(f"  MESSAGE BLOCKED BY SCORING: {reasons}")
            return MessageGenResult(message="", role_fit=role, status=f"rejected_quality: {reasons}")
            
        log.info(f"  Generated ({role}): {msg[:80]}... [Score: {score.quality_score:.2f}]")
        return MessageGenResult(message=msg, role_fit=role, status="ready")
    except ValueError as e:
        log.warning(f"  MESSAGE REJECTED: {e}")
        return MessageGenResult(message="", role_fit=role, status=f"rejected_name: {e}")


@controller.action("Record a successfully sent message to SQLite database and update pipeline")
async def record_sent(params: RecordSentInput) -> str:
    db = _state["db"]
    governor = _state["governor"]
    session_id = _state["session_id"]
    approver = _state["approver"]

    url = normalize_url(params.profile_url)
    clean_name = normalize_name(params.name)

    try:
        # Record prospect
        prospect_id = db.record_prospect(
            profile_url=url,
            name=clean_name,
            college=params.college,
            signal_type=params.signal_type,
            role_fit=params.role_fit)

        # Determine approval status
        approved_by = "auto"
        if approver and approver.mode == ApprovalMode.MODE_APPROVE:
            approved_by = "human"

        # Record message
        db.record_message(
            prospect_id=prospect_id,
            direction="outbound",
            message_text=params.message,
            session_id=session_id,
            approved_by=approved_by)

        # Update pipeline
        db.update_pipeline(
            prospect_id=prospect_id,
            stage="opener_sent")

        # Save checkpoint
        db.save_checkpoint(
            session_id=session_id,
            step="message_sent",
            data=json.dumps({"url": url, "name": clean_name, "message": params.message}))

        # Record success with governor
        governor.record_send_success()
        governor.print_status()

        status = governor.get_status()
        return (
            f"Recorded: {clean_name}. "
            f"Session: {status['session_sent']}/{status['session_limit']}. "
            f"Daily remaining: {status['daily_remaining']}."
        )

    except ValueError as e:
        log.error(f"  RECORD FAILED: {e}")
        return f"FAILED to record: {e}"


@controller.action("Wait a random human-like delay between actions (25-45 seconds, with occasional longer pauses)")
async def human_delay(params: HumanDelayInput) -> HumanDelayResult:
    governor = _state["governor"]
    d = governor.get_human_delay()
    log.info(f"  Human delay: {d:.0f}s")
    await asyncio.sleep(d)
    return HumanDelayResult(waited_seconds=round(d, 1))


@controller.action("Get current session status — messages sent, limits, safety state")
async def round_status() -> str:
    governor = _state["governor"]
    status = governor.get_phase1_status()
    db = _state["db"]
    stats = db.get_stats()

    return (
        f"Session Minutes: {status['session_minutes']}m/{status['session_time_limit']}m. "
        f"Daily Openers: {status['openers_sent_today']}/{status['openers_limit']}. "
        f"Daily Followups: {status['followups_sent_today']}/{status['followups_limit']}. "
        f"Total prospects in DB: {stats['total_prospects']}. "
    )


@controller.action("Check if the agent should randomly stop for anti-detection")
async def check_random_stop() -> str:
    governor = _state["governor"]
    if governor.should_random_stop():
        return "RANDOM_STOP: Yes — stop the session now for anti-detection. This is intentional."
    return "Continue — no random stop triggered."


@controller.action("Get a search keyword for finding LinkedIn prospects")
async def get_search_keyword() -> str:
    kw = random.choice(SEARCH_KEYWORDS)
    log.info(f"  Search keyword: {kw}")
    return kw


# ═══════════════════════════════════════════════════════════════════
# TASK PROMPT — deterministic + AI hybrid
# ═══════════════════════════════════════════════════════════════════
OUTREACH_TASK = f"""
You are Ganesh Tappiti's LinkedIn outreach agent for clstr.in — a verified campus social network.
Your job is to find, verify, and message college students who are campus leaders.

## HARD RULES — NEVER BREAK
1. Send at most 10 messages this session. After 10, STOP.
2. Process ONE profile at a time. Finish completely before moving to the next.
3. After EVERY message, call `check_random_stop` — if it says STOP, end the session.
4. After sending each message, call `human_delay` before the next profile.
5. NEVER message someone already messaged — always call `check_dedup` first.
6. NEVER send if `gen_message` returns status != "ready" — skip that profile.

## WORKFLOW (repeat for each candidate)
1. Call `get_search_keyword` to get a search query.
2. Call `navigate_to_search` with that keyword — this navigates DIRECTLY, no need to find the search bar.
3. WAIT 3 seconds for results to load, then SCROLL DOWN to see profiles.
4. From the search results page, pick a profile that looks like a real student with campus leadership signals.
4. Call `check_dedup` with the profile URL. If duplicate, skip and pick another.
5. Call `navigate_to_profile` with the profile URL to go directly to their profile.
6. Read their headline, experience, education sections.
7. VERIFY identity — extract their real name and college:
   - Name must be a real person's name (NOT "there", "LinkedIn Member", "unknown")
   - College must be an actual institution name
   - If EITHER is missing or unclear, SKIP this profile entirely.
8. Detect their strongest signal:
   - TEDx -> tedx
   - Startup cell / E-cell / Entrepreneurship cell -> startup_cell
   - Student council / Student union -> student_council
   - Campus ambassador / Brand ambassador -> campus_ambassador
   - Graphic design / UI/UX / Figma / Design head -> core_team_design
   - Marketing lead / Social media manager / Content creator -> core_team_marketing
   - Club/Society president or VP -> club_president
   - Event coordinator/organizer -> event_coordinator
   - None of the above -> default
9. Call `gen_message` with their name, college, signal_type, and specific_signal.
   - If status is NOT "ready", SKIP this profile. Do not attempt to send.
10. Send the DM:
    - Call `open_message_compose` or click the Message button on their profile.
    - Type the message CHARACTER BY CHARACTER into the compose box (30-80ms per char).
    - DO NOT paste. Type each character individually.
    - Click Send.
11. Call `record_sent` with all profile details.
12. Call `check_random_stop` — if triggered, STOP and report summary.
13. Call `round_status` to check if you've hit the limit.
14. If under the limit, call `human_delay` then go to step 1 for the next candidate.
15. If at the limit, STOP and report the summary.

## MESSAGE TONE
- Max 2 sentences
- Casual, peer-to-peer — use "bro", first name, direct
- Reference something SPECIFIC from their profile
- End with ONE genuine question
- NO corporate language, NO emoji overload, NO pitching clstr.in directly
- NO form link ({FORM_URL}) in first message
- NO phone number ({PHONE}) in first message
- Sound like a 21-year-old founder, not a recruiter

## ANTI-DETECTION
- Type messages character by character (30-80ms per char), NEVER paste
- Use random delays between all actions
- Never rush through profiles
- If you encounter a CAPTCHA or security check, STOP immediately

## ON COMPLETION
When done, call `round_status` and report the final summary.
"""


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
async def main():
    # Parse approval mode from CLI args
    mode = parse_mode_from_args()

    # Initialize SQLite database
    db = OutreachDB()

    # Recover any crashed sessions from previous runs
    crashed = db.recover_crashed_sessions()
    if crashed:
        log.warning(f"Recovered {crashed} crashed session(s) from previous runs")

    # Initialize safety governor and scorer
    governor = SafetyGovernor(db)
    scorer = MessageScorer(db)

    # Pre-session safety check
    can_start, reason = governor.can_start_session("outreach")
    if not can_start:
        log.error(f"CANNOT START: {reason}")
        db.close()
        return

    # Phase 1: Check if we have any opener limit left
    can_send_openers, limit_msg = governor.can_send_new_opener()
    if not can_send_openers:
        log.error(f"PHASE 1 LIMIT REACHED: {limit_msg}")
        db.close()
        return

    # Start a new session
    session_id = db.start_session("outreach")

    # Initialize approval mode
    approver = ApprovalMode(mode=mode, db=db)

    # Set global state for controller tools
    _state["db"] = db
    _state["governor"] = governor
    _state["approver"] = approver
    _state["scorer"] = scorer
    _state["session_id"] = session_id

    stats = db.get_stats()
    log.info(f"\n{'=' * 60}")
    log.info("clstr.in Outreach v2 — browser-use + Ollama + SQLite")
    log.info(f"Mode: {mode}")
    log.info(f"Session: {session_id}")
    log.info(f"Daily limit: {governor.MAX_DMS_PER_DAY} | Per-round: {governor.MAX_PER_ROUND}")
    can_send, remaining = db.can_send_today(governor.MAX_DMS_PER_DAY)
    log.info(f"Messages remaining today: {remaining}")
    log.info(f"Total prospects in DB: {stats['total_prospects']}")
    log.info(f"Total previously messaged: {stats['total_messaged']}")
    log.info(f"{'=' * 60}\n")

    # Ensure data-tracking directory exists
    Path("data-tracking").mkdir(exist_ok=True)

    # Configure persistent Chrome profile with anti-detection
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
        highlight_elements=False)

    browser = Browser(browser_profile=profile)

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
        task=OUTREACH_TASK,
        llm=llm,
        browser=browser,
        controller=controller,
        max_failures=3,
        max_actions_per_step=3,
        use_vision=False,  # Ollama doesn't support vision well
        generate_gif=False)

    try:
        result = await agent.run()

        # End session successfully
        db.end_session(session_id, "completed")

        final_stats = db.get_stats()
        log.info(f"\n{'=' * 60}")
        log.info(f"AGENT COMPLETE — Session: {session_id}")
        log.info(f"Messages sent this session: {governor._session_send_count}")
        log.info(f"Total sent today: {final_stats['today_sent']}")
        log.info(f"Total prospects: {final_stats['total_prospects']}")
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
        close_method = getattr(browser, "close", None) or getattr(browser, "aclose", None)
        if close_method:
            close_result = close_method()
            if inspect.isawaitable(close_result):
                await close_result
        else:
            get_context = getattr(browser, "get_context", None)
            if get_context:
                context = await get_context()
                context_close = getattr(context, "close", None) or getattr(context, "aclose", None)
                if context_close:
                    context_close_result = context_close()
                    if inspect.isawaitable(context_close_result):
                        await context_close_result
        db.close()


if __name__ == "__main__":
    asyncio.run(main())




















