"""
linkedin_original_post.py  —  v3.0 VIRAL DATA FORMAT EDITION
==============================================================
Daily LinkedIn Post Pipeline for Ganesh Tappiti (@ganeshtappiti)

PROVEN VIRAL FORMULA (reference: post that got 1.5 LAKH impressions + 400 followers):
  ┌─────────────────────────────────────────────────────────────────┐
  │  "I scanned [N] [sources]. Here are the [X] [findings] 👇"     │
  │  📊 Item 1 — 88%                                               │
  │  📊 Item 2 — 81%                                               │
  │  📊 Item 3 — 74%                                               │
  │  ... (6-10 items with percentages)                              │
  │  One insight that connects the data to the reader's life.       │
  │  No promo. No links. One question. Max 3 hashtags.              │
  └─────────────────────────────────────────────────────────────────┘
  IMAGE: Pen-drawn horizontal bar chart on paper (black + red/blue ink)

WHY THIS WORKS:
  - Data = credibility + saves (people screenshot and share)
  - "I scanned X" hook = immediate authority + curiosity
  - Horizontal bar chart image = stops the scroll, feels human not AI
  - No promo = algorithmic boost (LinkedIn loves native content)
  - Data posts get 3-5x more saves than opinion posts → algo amplification

GANESH'S TOPICS (adapted, not VybeSchool):
  - Clstr.in campus network metrics/learnings
  - Buildtrix startup validation research
  - Indian campus ecosystem data
  - AI tools used by Indian student founders
  - LinkedIn/startup skill demand in India
  - Campus ambassador / student startup trends

Run: python linkedin_original_post.py
"""

import argparse

# Argument parsing
parser = argparse.ArgumentParser(
    description="LinkedIn Viral Data Post Pipeline Ganesh Tappiti"
)
parser.add_argument(
    "--plan",
    action="store_true",
    default=False,
    help="Generate a 7-day content calendar JSON; exits without posting. Does NOT replace daily post; runs in addition.",
)
ARGS = parser.parse_args()

import asyncio
import json
import os
import re
import random
import os
import re
import random
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT        = Path(__file__).parent.resolve()
MEMORY_DIR       = REPO_ROOT / "memory"
NORMALIZED_DIR   = MEMORY_DIR / "normalized_2026-04-26"
POST_IMAGES_DIR  = MEMORY_DIR / "post_images"
DATA_DIR         = REPO_ROOT / "data-tracking"
CHROME_PROFILE   = DATA_DIR / "chrome-profile"
GUIDES_DIR       = REPO_ROOT / ".qodo" / "guides"

POST_HISTORY_FILE = MEMORY_DIR / "linkedin_post_history.json"
NATIVE_LOG_FILE   = DATA_DIR / "post_native_log.json"
PLAYBOOK_FILE     = MEMORY_DIR / "linkedin_post_writing_playbook.json"
HUMANIZATION_FILE = MEMORY_DIR / "humanization_policy.json"
SYNTHESIS_FILE    = NORMALIZED_DIR / "PERSONAL_SYNTHESIS_GANESH.md"
TONE_REF_FILE     = NORMALIZED_DIR / "ganesh_real_tone_reference.md"
ALGO_FILE         = GUIDES_DIR / "360-BREW-QUICK-REFERENCE.md"

POST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def load_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_recent_topics(history: dict, n: int = 10) -> list:
    return [p.get("topic", "") for p in history.get("posts", [])[-n:]]

def get_recent_hook_types(history: dict, n: int = 3) -> list:
    return [p.get("hook_type", "") for p in history.get("posts", [])[-n:]]

def get_recent_pillars(history: dict, n: int = 3) -> list:
    return [p.get("content_pillar", "") for p in history.get("posts", [])[-n:]]

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower())[:40].strip("_")

# ── TODAY GUARD ────────────────────────────────────────────────────────────
# Prevents the pipeline from posting more than once per calendar day (IST).
# A "pending" lock is also written before the browser launches so that if
# the script crashes mid-post, the next run still sees a record and aborts.

TODAY_LOCK_KEY = "today_lock"  # top-level key written into post_native_log.json

def _today_str_ist() -> str:
    """Return today's date string in IST (UTC+5:30)."""
    from datetime import timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(IST).strftime("%Y-%m-%d")

def already_posted_today(log: dict) -> bool:
    """
    Returns True if a 'success' OR 'pending' run was already logged today (IST).
    - success  → post went live, definitely do NOT post again.
    - pending  → browser was launched but script crashed before confirming;
                 treat as posted to avoid double-posting.
    """
    today = _today_str_ist()
    for run in log.get("runs", []):
        run_date = run.get("timestamp", "")[:10]  # YYYY-MM-DD prefix
        if run_date == today and run.get("status") in ("success", "pending"):
            return True
    return False

def write_pending_lock(log: dict, log_path: Path, ts: str) -> dict:
    """
    Write a 'pending' sentinel entry into the run log BEFORE the browser
    launches.  This ensures that even if the script crashes during posting,
    the next invocation will see today's date and refuse to post again.
    """
    log.setdefault("runs", []).append({
        "run_id": f"run_viral_{datetime.now().strftime('%Y%m%d_%H%M')}_pending",
        "timestamp": ts,
        "pipeline": "linkedin_viral_data_post_v3",
        "status": "pending",  # ← sentinel: browser is about to launch
        "topic": "[pending — set after post]",
    })
    save_json(log_path, log)
    return log

def resolve_pending_run(log: dict, log_path: Path, post_data: dict,
                        post_id: int, ts: str, status: str) -> dict:
    """
    Replace the most recent 'pending' sentinel with the real run record.
    """
    runs = log.get("runs", [])
    # Find the last pending entry and replace it
    for i in reversed(range(len(runs))):
        if runs[i].get("status") == "pending":
            runs[i] = {
                "run_id": f"run_viral_{datetime.now().strftime('%Y%m%d_%H%M')}",
                "timestamp": ts,
                "pipeline": "linkedin_viral_data_post_v3",
                "status": status,
                "topic": post_data.get("topic", ""),
                "research_source": post_data.get("research_source", ""),
                "predicted_reach": post_data.get("predicted_reach", ""),
                "word_count": post_data.get("word_count", 0),
                "post_id": post_id,
            }
            break
    log["runs"] = runs
    save_json(log_path, log)
    return log

def copy_image_to_clipboard(image_path: str) -> bool:
    ps_path = image_path.replace("\\", "\\\\")
    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        f"$img = [System.Drawing.Image]::FromFile('{ps_path}'); "
        "[System.Windows.Forms.Clipboard]::SetImage($img); "
        "Write-Output 'Image copied to clipboard.'"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True, text=True
    )
    print(f"  Clipboard: {result.stdout.strip()}")
    if result.stderr and "copied" not in result.stdout.lower():
        print(f"  Clipboard warning: {result.stderr.strip()[:200]}")
    return "copied" in result.stdout.lower()


# ═══════════════════════════════════════════════════════════════════════════
# VIRAL DATA POST PROMPT  —  The formula that gets 1.5 lakh impressions
# ═══════════════════════════════════════════════════════════════════════════

def build_viral_prompt(
    synthesis: str,
    tone_ref: str,
    humanization: dict,
    algo_guide: str,
    recent_topics: list,
    recent_hook_types: list,
    recent_pillars: list,
) -> str:

    all_pillars = [
        "Build in Public",
        "AI-Enabled Building",
        "Campus Ecosystem",
        "Founder Psychology",
        "Design x Engineering",
    ]
    prefer_pillars  = [p for p in all_pillars if p not in recent_pillars] or all_pillars
    recent_str      = "\n".join(f"  - {t}" for t in recent_topics) or "  (none yet)"
    voice_policy    = humanization.get("system_template", "Write natural, credible, human LinkedIn posts.")

    return f"""You are the LinkedIn Viral Content Engine for Ganesh Tappiti (@ganeshtappiti).
Your ONE job: produce a post that gets 50,000+ impressions and 200+ real followers.

══════════════════════════════════════════════════════════════════
 PROVEN VIRAL FORMAT — "I SCANNED X" DATA POST
══════════════════════════════════════════════════════════════════

A post using this exact format got 1.5 LAKH (150,000) impressions and 400+ followers in a single day.
Here is the format you MUST follow:

LINE 1 (hook):    "I scanned [specific number] [specific source] in [timeframe]."
LINE 2 (payoff):  "Here are the [top X / real findings] [relevant to reader] 👇"
[blank line]
DATA LIST (6-10 items):
📊 [Specific finding or skill] — [percentage or number]
📊 [Specific finding or skill] — [percentage or number]
... (continue for 6-10 items, sorted highest to lowest %)
[blank line]
INSIGHT (2-4 lines):
One thing became obvious after scanning all this:
[The single most important pattern or truth the data reveals]
[One sentence on what this means for the reader]
[blank line]
REFLECTION (1-2 lines):
[A short honest observation connecting Ganesh's experience to this data]
[Example: "I'm seeing this in real time building clstr.in."]
[blank line]
ENGAGEMENT QUESTION (1 line — must be specific and create debate):
[e.g. "Are you upskilling for this market or waiting to see how it plays out?"]
[blank line]
HASHTAGS: #Tag1 #Tag2 #Tag3  (max 3, all relevant to data topic)

══════════════════════════════════════════════════════════════════
 WHY THIS FORMAT WORKS (360 Brew algorithm 2026)
══════════════════════════════════════════════════════════════════
- SAVES are the #1 signal: data posts get saved 5-10x more than opinion posts
- "I scanned X" hook = instant authority + curiosity = maximum "see more" clicks
- 📊 list = high dwell time (people read every line) = algorithm amplification
- No external links = 3-5x native reach boost from LinkedIn
- Specific numbers = credibility = shares from people who agree/disagree
- Engagement question at end = comments flood = further amplification

══════════════════════════════════════════════════════════════════
 GANESH'S PROFILE CONTEXT
══════════════════════════════════════════════════════════════════
{synthesis[:2000]}

══════════════════════════════════════════════════════════════════
 GANESH'S REAL VOICE
══════════════════════════════════════════════════════════════════
{tone_ref}

HUMANIZATION POLICY:
{voice_policy}

══════════════════════════════════════════════════════════════════
 DEDUP — DO NOT REPEAT
══════════════════════════════════════════════════════════════════
Already posted (skip these topics/angles):
{recent_str}

Recent pillars (avoid): {", ".join(recent_pillars) or "none"}
Prefer pillars today:   {", ".join(prefer_pillars)}

══════════════════════════════════════════════════════════════════
 TOPIC SELECTION — WHAT TO RESEARCH
══════════════════════════════════════════════════════════════════

Pick ONE topic from this ranked list (higher = more viral potential for Ganesh):

TIER 1 — Highest viral potential (data everyone wants to know):
→ AI engineering skills in demand — Indian job market / JDs (like the 1.5L post)
→ Startup skills Indian founders are hiring for right now
→ Tools Indian student founders actually use vs what colleges teach
→ Tech layoffs + AI hiring shift in India (companies cutting X, hiring Y)
→ Salaries for AI engineers in India 2026 (real numbers people compare themselves to)
→ Campus to startup transition — what actually helps vs what doesn't

TIER 2 — Strong viral potential:
→ What Y Combinator actually wants from Indian founders (real data from batches)
→ How Clstr.in grew — real metrics from building a campus OS
→ What Indian engineering students are learning vs what the market wants
→ AI tools replacing traditional skills — percentage data
→ MVP validation stats — what % of ideas survive first user test

TIER 3 — Good but more niche:
→ Design tools used by top Indian product teams
→ Stack used by top Indian SaaS startups
→ Time allocation of top student founders (data)

SELECTION CRITERIA:
✓ Pick the topic your TARGET AUDIENCE (Indian founders, students, builders 18-28) cares about MOST today
✓ Must be data you can present with realistic, credible percentages
✓ Must NOT be already in the recent topics list above
✓ Must fit Ganesh's voice — he's a 21yo founder building real products, not a career coach

══════════════════════════════════════════════════════════════════
 DATA GENERATION RULES
══════════════════════════════════════════════════════════════════

For the 📊 data list:
- Use realistic, research-grounded percentages (not made up)
- Base on: LinkedIn JD scanning, GitHub trend data, ProductHunt, Inc42, Wellfound, YC batches
- Sort from highest % to lowest %
- Each item should be specific (not vague)
- 6-10 items is the sweet spot — enough to feel comprehensive, not overwhelming
- The "source" in the hook must be specific: "215 Indian AI Engineering JDs" not "job descriptions"

══════════════════════════════════════════════════════════════════
 WRITING RULES (NON-NEGOTIABLE)
══════════════════════════════════════════════════════════════════
✓ Sound like Ganesh: 21yo founder, direct, specific, no corporate fluff
✓ NEVER mention VybeSchool, WhatsApp groups, or any external platforms
✓ NEVER include external links anywhere in the post body
✓ Max 3 hashtags at the very end only
✓ Total post: 120-200 words (data list posts can be slightly longer)
✓ Connect data to Ganesh's real experience when natural (clstr.in, Buildtrix, Scollab)
✓ End with a specific polarizing question (not "what do you think?")
✓ Zero AI-filler: "In today's world", "Excited to share", "Delighted to"

══════════════════════════════════════════════════════════════════
 IMAGE GENERATION — PEN-DRAWN HORIZONTAL BAR CHART
══════════════════════════════════════════════════════════════════

The image that made the 1.5L-impression post work was a HAND-DRAWN style horizontal bar chart.
You MUST generate an image prompt for this exact style.

Image style rules:
- Looks like someone drew it on a white/cream notebook paper with actual pens
- Horizontal bars (not vertical)  
- Each bar represents one data item from the 📊 list
- Categories on the LEFT, bars extend to the RIGHT, % label at the end of each bar
- Use TWO ink colors: black (for text, axes, labels) + RED or BLUE (for the bars)
- Paper texture visible — not a clean digital chart
- Title at the top in hand-lettered style
- No gradients, no shadows, no digital effects
- Messy-but-readable aesthetic — like a founder's whiteboard sketch
- Landscape/horizontal orientation (wider than tall)
- No logos, no VybeSchool, no WhatsApp, no QR codes

Image prompt template:
"A hand-drawn horizontal bar chart on white notebook paper, sketched with black and [red OR blue] ink pens.
The chart shows [DATA TITLE] with [NUMBER] horizontal bars.
Left side lists: [item1], [item2], [item3]... (all categories from the data).
Bars extend right showing relative percentages, with % numbers written at the end of each bar.
Title at top reads: '[CHART TITLE]' in bold hand-lettered style.
The pen strokes are slightly imperfect and natural-looking, like a researcher's field notes.
Paper has subtle texture. No digital effects. No shadows. No gradients.
Black ink for all text and axes. [Red OR Blue] ink for the horizontal percentage bars.
Clean white background. Landscape orientation."

══════════════════════════════════════════════════════════════════
 OUTPUT FORMAT — Return EXACTLY this JSON, nothing else
══════════════════════════════════════════════════════════════════
{{
  "topic": "one-sentence description of the research topic",
  "research_source": "what was scanned (e.g. '215 Indian startup JDs on LinkedIn in May 2026')",
  "data_items": [
    {{"label": "RAG / Retrieval Augmented Generation", "percentage": 88}},
    {{"label": "LangChain / LangGraph", "percentage": 81}}
  ],
  "content_pillar": "one of: Build in Public | AI-Enabled Building | Campus Ecosystem | Founder Psychology | Design x Engineering",
  "post_type": "research_data",
  "hook_type": "direct_authority",
  "post_text": "THE COMPLETE LINKEDIN POST — formatted with blank lines between sections, 📊 emojis on data lines, exactly following the I SCANNED format",
  "hashtags": ["#Tag1", "#Tag2", "#Tag3"],
  "engagement_question": "the final question line (just the question)",
  "chart_title": "title to write at top of the hand-drawn chart",
  "chart_ink_color": "red OR blue",
  "image_prompt": "the complete hand-drawn bar chart image generation prompt",
  "word_count": 0,
  "hook_first_line": "just the first line",
  "predicted_reach": "your honest prediction with reason"
}}
"""


# ═══════════════════════════════════════════════════════════════════════════
# GENERATE POST VIA GEMINI
# ═══════════════════════════════════════════════════════════════════════════

async def generate_post(prompt: str, api_key: str) -> dict:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-05-20",
        google_api_key=api_key,
        temperature=0.85,
    )

    print("  Calling Gemini to research data + draft viral post...")
    response = await llm.ainvoke([
        SystemMessage(content=(
            "You are a LinkedIn viral content strategist and data journalist. "
            "You create data-driven posts that get massive reach on LinkedIn. "
            "You use real, credible research data. "
            "You ALWAYS return valid JSON with no extra text, no markdown fences."
        )),
        HumanMessage(content=prompt),
    ])

    raw = response.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse Gemini JSON:\n{raw[:500]}")

    data["word_count"] = len(data.get("post_text", "").split())
    return data


# ═══════════════════════════════════════════════════════════════════════════
# GENERATE PEN-DRAWN BAR CHART IMAGE
# ═══════════════════════════════════════════════════════════════════════════

async def generate_image(image_prompt: str, save_path: Path, api_key: str) -> bool:
    import httpx, base64

    print(f"  Generating pen-drawn horizontal bar chart...")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash-preview-image-generation:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": image_prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        print(f"  Image gen failed: HTTP {resp.status_code}")
        return False

    data = resp.json()
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                save_path.write_bytes(img_bytes)
                size_kb = len(img_bytes) // 1024
                print(f"  ✓ Chart saved: {save_path.name} ({size_kb} KB)")
                return True

    print("  No image data in Gemini response.")
    return False


# ═══════════════════════════════════════════════════════════════════════════
# POST TO LINKEDIN VIA PURE PLAYWRIGHT  (no browser-use, no LLM)
# ═══════════════════════════════════════════════════════════════════════════

async def post_to_linkedin(post_text: str, _api_key: str = "") -> bool:
    """
    Post to LinkedIn using pure Playwright + saved Chrome profile.
    - Copies the Chrome profile to a temp dir to avoid lock conflicts.
    - Uses system Chrome (channel='chrome') so saved cookies/sessions work.
    - Pastes image from clipboard via Ctrl+V.
    - Types text character by character (human-speed).
    - No browser-use, no Ollama, no LLM involved.
    """
    import shutil, tempfile
    from playwright.async_api import async_playwright

    tmp_profile = tempfile.mkdtemp(prefix="li-post-")
    print(f"  Copying Chrome profile to temp: {tmp_profile}")
    shutil.copytree(str(CHROME_PROFILE.resolve()), tmp_profile, dirs_exist_ok=True)
    print("  Profile copied.")

    success = False
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=tmp_profile,
                headless=False,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--start-maximized",
                    "--disable-infobars",
                ],
                ignore_https_errors=True,
                no_viewport=True,
            )

            page = context.pages[0] if context.pages else await context.new_page()

            # ── [1] Navigate to feed ────────────────────────────────────
            print("  Navigating to LinkedIn feed...")
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            if "login" in page.url or "authwall" in page.url:
                print("  ERROR: LinkedIn session expired. Re-login required.")
                await context.close()
                return False
            print(f"  Feed loaded: {page.url}")

            # Scroll to top to expose the 'Start a post' composer box
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(2)

            # ── [2] Click 'Start a post' ────────────────────────────────
            print("  Clicking 'Start a post'...")
            start_selectors = [
                "button.share-box-feed-entry__trigger",
                "button[class*='share-box-feed-entry__trigger']",
                ".share-box-feed-entry__trigger",
                "button:has-text('Start a post')",
                "div.share-box-feed-entry__top-bar button",
                "div[class*='share-box-feed-entry'] button:first-child",
                "[placeholder='Start a post']",
            ]
            clicked = False
            for sel in start_selectors:
                try:
                    el = await page.wait_for_selector(sel, timeout=4000)
                    if el:
                        await el.click()
                        clicked = True
                        print(f"  Start a post clicked.")
                        break
                except Exception:
                    continue

            if not clicked:
                # JS fallback — find by text content
                clicked = await page.evaluate("""
                    () => {
                        const els = document.querySelectorAll('button, div[role=button], input[placeholder]');
                        for (const el of els) {
                            const t = (el.textContent || el.getAttribute('placeholder') || '').trim();
                            if (t.toLowerCase().includes('start a post') ||
                                t.toLowerCase().includes('what do you want to talk about')) {
                                el.click(); return true;
                            }
                        }
                        return false;
                    }
                """)
                if clicked:
                    print("  Start a post clicked via JS fallback.")

            if not clicked:
                print("  Could not find 'Start a post' button — check page manually.")
            await asyncio.sleep(2)

            # ── [3] Paste image from clipboard ──────────────────────────
            print("  Pasting image from clipboard (Ctrl+V)...")
            await page.keyboard.press("Control+v")
            await asyncio.sleep(4)  # Wait for image upload to begin

            # ── [4] Find text area and type post ────────────────────────
            print("  Locating post text area...")
            text_area_selectors = [
                "div.ql-editor[contenteditable='true']",
                "div[contenteditable='true'][data-placeholder]",
                "div.share-creation-state__text-editor div[contenteditable='true']",
                "div[role='textbox']",
                "div.editor-content div[contenteditable='true']",
            ]
            text_area = None
            for sel in text_area_selectors:
                try:
                    text_area = await page.wait_for_selector(sel, timeout=5000)
                    if text_area:
                        print(f"  Found text area (selector: {sel})")
                        break
                except Exception:
                    continue

            if not text_area:
                print("  ERROR: Could not find post text area.")
                await context.close()
                return False

            await text_area.click()
            await asyncio.sleep(0.5)

            # Type character by character (human-speed: 40-80ms per char)
            print(f"  Typing {len(post_text)} characters...")
            import random as _random
            for char in post_text:
                if char == "\n":
                    await page.keyboard.press("Enter")
                else:
                    await page.keyboard.type(char)
                await asyncio.sleep(_random.uniform(0.04, 0.08))

            await asyncio.sleep(2)
            print("  Text typed.")

            # ── [5] Click Post ───────────────────────────────────────────
            print("  Clicking Post button...")
            post_btn_selectors = [
                "button.share-actions__primary-action",
                "button[class*='share-actions__primary-action']",
                "button.artdeco-button--primary:has-text('Post')",
                "button:has-text('Post')",
                "button[aria-label='Post']",
            ]
            posted = False
            for sel in post_btn_selectors:
                try:
                    btn = await page.wait_for_selector(sel, timeout=5000)
                    if btn:
                        is_disabled = await btn.get_attribute("disabled")
                        if is_disabled:
                            print(f"  Post button found but disabled — waiting 3s...")
                            await asyncio.sleep(3)
                        await btn.click()
                        posted = True
                        print(f"  Post button clicked (selector: {sel})")
                        break
                except Exception:
                    continue

            if not posted:
                print("  ERROR: Could not find or click the Post button.")
                await context.close()
                return False

            # ── [6] Confirm ─────────────────────────────────────────────
            await asyncio.sleep(6)
            print("  Waiting for post to appear in feed...")

            # Check if modal closed (means post went through)
            modal_gone = True
            try:
                modal = await page.query_selector("div.share-creation-state")
                if modal:
                    modal_visible = await modal.is_visible()
                    modal_gone = not modal_visible
            except Exception:
                modal_gone = True

            if modal_gone:
                print("  Post modal closed — post submitted successfully.")
                success = True
            else:
                print("  WARNING: Modal still visible. Post may not have gone through.")
                success = False

            await asyncio.sleep(3)
            await context.close()

    except Exception as e:
        print(f"  ERROR in post_to_linkedin: {e}")
        import traceback; traceback.print_exc()
        success = False
    finally:
        shutil.rmtree(tmp_profile, ignore_errors=True)
        print("  Temp profile cleaned up.")

    return success



# ═══════════════════════════════════════════════════════════════════════════
# LOG UPDATES
# ═══════════════════════════════════════════════════════════════════════════

def update_history(history: dict, post_data: dict, image_path: str, ts: str) -> dict:
    posts = history.get("posts", [])
    new_id = max((p.get("id", 0) for p in posts), default=0) + 1
    posts.append({
        "id": new_id,
        "published_at": ts,
        "source_platform": "linkedin_native",
        "source_type": "viral_data_post",
        "topic": post_data.get("topic", ""),
        "research_source": post_data.get("research_source", ""),
        "content_pillar": post_data.get("content_pillar", ""),
        "post_type": post_data.get("post_type", "research_data"),
        "hook_type": post_data.get("hook_type", ""),
        "linkedin_hook": post_data.get("hook_first_line", ""),
        "linkedin_hashtags": post_data.get("hashtags", []),
        "word_count": post_data.get("word_count", 0),
        "image_attached": bool(image_path),
        "image_path": image_path,
        "image_style": "pen_drawn_horizontal_bar_chart",
        "image_prompt_used": post_data.get("image_prompt", ""),
        "predicted_reach": post_data.get("predicted_reach", ""),
        "status": "published",
    })
    history["posts"] = posts
    history["total_posts"] = len(posts)
    history["last_updated"] = ts
    return history

def update_log(log: dict, post_data: dict, post_id: int, ts: str, status: str) -> dict:
    if not log:
        log = {"version": "1.0.0", "created_at": ts, "runs": []}
    log.setdefault("runs", []).append({
        "run_id": f"run_viral_{datetime.now().strftime('%Y%m%d_%H%M')}",
        "timestamp": ts,
        "pipeline": "linkedin_viral_data_post_v3",
        "status": status,
        "topic": post_data.get("topic", ""),
        "research_source": post_data.get("research_source", ""),
        "predicted_reach": post_data.get("predicted_reach", ""),
        "word_count": post_data.get("word_count", 0),
        "post_id": post_id,
    })
    return log


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

async def main():
    # Load memory first (needed by --plan and the full pipeline)
    print("[1/6] Loading memory + profile context...")
    synthesis    = load_text(SYNTHESIS_FILE)
    tone_ref     = load_text(TONE_REF_FILE)
    humanization = load_json(HUMANIZATION_FILE)
    algo_guide   = load_text(ALGO_FILE)
    history      = load_json(POST_HISTORY_FILE)
    native_log   = load_json(NATIVE_LOG_FILE)
    print(f"  ✓ Profile synthesis:   {len(synthesis):,} chars")
    print(f"  ✓ Post history:        {history.get('total_posts', 0)} posts logged")

    # ── --plan FLAG ──────────────────────────────────────────────────────────
    # Generate 7-day content calendar; exit without posting.
    if ARGS.plan:
        print("[--plan] Generating 7-day content calendar...")
        try:
            from scripts.content_planner import generate_content_calendar
            calendar = generate_content_calendar(
                synthesis=synthesis,
                tone_ref=tone_ref,
                humanization=humanization,
                algo_guide=algo_guide,
                recent_topics=get_recent_topics(history, 10),
                recent_pillars=get_recent_pillars(history, 3),
            )
            calendar_path = MEMORY_DIR / "linkedin_content_calendar.json"
            save_json(calendar_path, calendar)
            print(f"  ✓ Calendar written to {calendar_path}")
            print("[--plan] Exiting — no post will be published today.")
            sys.exit(0)
        except Exception as e:
            print(f"  ✗ Failed to generate calendar: {e}")
            import traceback; traceback.print_exc()
            sys.exit(1)
    # ─────────────────────────────────────────────────────────────────────────

    # API key
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║  LinkedIn Viral Data Post Pipeline  —  Ganesh Tappiti          ║")
    print("║  Formula: 'I scanned X' + 📊 data + pen-drawn chart           ║")
    print("║  Target:  50,000+ impressions  |  100+ new followers           ║")
    print("╚═════════════════════════════════════════════════════════════════╝")
    print()

    # API key
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                k = line.strip()
                if ("GOOGLE_API_KEY=" in k or "GEMINI_API_KEY=" in k) and "=" in k:
                    val = k.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        api_key = val
                        break
    if not api_key:
        print("ERROR: No GOOGLE_API_KEY found. Add to .env:  GOOGLE_API_KEY=your_key_here")
        sys.exit(1)
    print("✓ API key loaded\n")

    # ── --plan FLAG ──────────────────────────────────────────────────────────
    # Generate 7-day content calendar; exit without posting.
    # Must NOT bypass the TODAY GUARD — if a post already went live today,
    # --plan should still be allowed (it only writes calendar JSON).
    if ARGS.plan:
        print("[--plan] Generating 7-day content calendar...")
        try:
            from scripts.content_planner import generate_content_calendar
            calendar = generate_content_calendar(
                synthesis=synthesis,
                tone_ref=tone_ref,
                humanization=humanization,
                algo_guide=algo_guide,
                recent_topics=get_recent_topics(history, 10),
                recent_pillars=get_recent_pillars(history, 3),
            )
            calendar_path = MEMORY_DIR / "linkedin_content_calendar.json"
            save_json(calendar_path, calendar)
            print(f"  ✓ Calendar written to {calendar_path}")
            print("[--plan] Exiting — no post will be published today.")
            sys.exit(0)
        except Exception as e:
            print(f"  ✗ Failed to generate calendar: {e}")
            import traceback; traceback.print_exc()
            sys.exit(1)
    # ─────────────────────────────────────────────────────────────────────────

    # [1] Load memory
    print("[1/6] Loading memory + profile context...")
    synthesis    = load_text(SYNTHESIS_FILE)
    tone_ref     = load_text(TONE_REF_FILE)
    humanization = load_json(HUMANIZATION_FILE)
    algo_guide   = load_text(ALGO_FILE)
    history      = load_json(POST_HISTORY_FILE)
    native_log   = load_json(NATIVE_LOG_FILE)
    print(f"  ✓ Profile synthesis:   {len(synthesis):,} chars")
    print(f"  ✓ Post history:        {history.get('total_posts', 0)} posts logged")

    # ── TODAY GUARD ──────────────────────────────────────────────────────────
    # Block execution if we already posted (or started posting) today.
    today_ist = _today_str_ist()
    print(f"\n[TODAY GUARD] Checking for existing posts on {today_ist} (IST)...")
    if already_posted_today(native_log):
        print()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║  🛑  DUPLICATE BLOCKED — Already posted today (IST)          ║")
        print("║                                                               ║")
        print("║  The pipeline detected a 'success' or 'pending' run today.   ║")
        print("║  LinkedIn rule: max 1 post per day from this pipeline.        ║")
        print("║  Run again tomorrow after 8:00 AM IST.                        ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        sys.exit(0)  # Clean exit — not an error, just a guard
    print(f"  ✓ No post found today — safe to proceed.")
    # ─────────────────────────────────────────────────────────────────────────

    # [2] Dedup
    print("\n[2/6] Checking post history for deduplication...")
    recent_topics  = get_recent_topics(history, 10)
    recent_hooks   = get_recent_hook_types(history, 3)
    recent_pillars = get_recent_pillars(history, 3)
    print(f"  Avoiding {len(recent_topics)} recent topics")
    print(f"  Rotating off pillars: {recent_pillars}")

    # [3] Generate viral data post
    print("\n[3/6] Researching + drafting viral data post via Gemini...")
    prompt = build_viral_prompt(
        synthesis=synthesis,
        tone_ref=tone_ref,
        humanization=humanization,
        algo_guide=algo_guide,
        recent_topics=recent_topics,
        recent_hook_types=recent_hooks,
        recent_pillars=recent_pillars,
    )
    post_data = await generate_post(prompt, api_key)

    # Display
    print(f"\n  ┌─ RESEARCH DATA ────────────────────────────────────────")
    print(f"  │  Topic:   {post_data.get('topic', '')}")
    print(f"  │  Source:  {post_data.get('research_source', '')}")
    print(f"  │  Pillar:  {post_data.get('content_pillar', '')}")
    print(f"  │  Predicted reach: {post_data.get('predicted_reach', '')}")
    items = post_data.get("data_items", [])
    if items:
        print(f"  │  Data items ({len(items)}):")
        for item in items:
            bar = "█" * int(item.get("percentage", 0) // 5)
            print(f"  │    {item.get('percentage', 0):>3}% {bar} {item.get('label', '')}")
    print(f"  └────────────────────────────────────────────────────────")
    print()
    print("  ── DRAFT POST ──────────────────────────────────────────────")
    print()
    print(post_data.get("post_text", ""))
    print()
    print("  ────────────────────────────────────────────────────────────")

    # [4] Generate pen-drawn bar chart image
    print("\n[4/6] Generating pen-drawn horizontal bar chart image...")
    today_str  = datetime.now().strftime("%Y-%m-%d")
    topic_slug = slugify(post_data.get("topic", "post"))
    img_path   = POST_IMAGES_DIR / f"{today_str}_{topic_slug}.png"
    image_ok   = await generate_image(post_data.get("image_prompt", ""), img_path, api_key)

    # [5] Copy to clipboard
    if image_ok:
        print("\n[5/6] Copying chart image to clipboard...")
        clipboard_ok = copy_image_to_clipboard(str(img_path))
        if not clipboard_ok:
            print("  ⚠ Clipboard may have failed — attempting post anyway")
        await asyncio.sleep(2)
    else:
        print("\n[5/6] Skipping clipboard (image failed)")

    # [6] Post
    print("\n[6/6] Posting to LinkedIn via browser agent...")
    ts = datetime.now(timezone.utc).isoformat()

    # ── PRE-POST PENDING LOCK ────────────────────────────────────────────────
    # Write a 'pending' sentinel to the run log BEFORE the browser launches.
    # If the script crashes mid-post, the next run will see this sentinel and
    # refuse to post again — preventing a double-post from a crash loop.
    print("  Writing pre-post pending lock to run log...")
    native_log = write_pending_lock(native_log, NATIVE_LOG_FILE, ts)
    print("  ✓ Pending lock written — safe to launch browser.")
    # ─────────────────────────────────────────────────────────────────────────

    post_ok = await post_to_linkedin(post_data.get("post_text", ""), api_key)
    status  = "success" if post_ok else "failed"

    # Logs — resolve the pending sentinel into the real run record
    print("\n[+] Saving logs...")
    history = update_history(history, post_data, str(img_path) if image_ok else "", ts)
    save_json(POST_HISTORY_FILE, history)
    native_log = resolve_pending_run(native_log, NATIVE_LOG_FILE, post_data,
                                     history["total_posts"], ts, status)
    print(f"  ✓ Logs updated — {history['total_posts']} total posts")

    # Summary
    print()
    print("╔═════════════════════════════════════════════════════════════════╗")
    if post_ok:
        print("║  ✅  POSTED SUCCESSFULLY                                        ║")
    else:
        print("║  ❌  FAILED — check browser agent output above                  ║")
    print("╠═════════════════════════════════════════════════════════════════╣")
    print(f"║  Topic:   {post_data.get('topic','')[:61]:<61} ║")
    print(f"║  Source:  {post_data.get('research_source','')[:61]:<61} ║")
    print(f"║  Hook:    {post_data.get('hook_first_line','')[:61]:<61} ║")
    print(f"║  Words:   {str(post_data.get('word_count',0)):<61} ║")
    print(f"║  Chart:   {(img_path.name if image_ok else 'none (text-only post)'):<61} ║")
    print(f"║  Reach:   {post_data.get('predicted_reach','')[:61]:<61} ║")
    print("╚═════════════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    asyncio.run(main())
