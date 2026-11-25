#!/usr/bin/env python3
"""
clstr.in LinkedIn Outreach — Clean, Safe, One-at-a-Time
Rules:
  - 10 candidates MAX per round
  - ONE message at a time, sequential, never parallel
  - Human-speed typing (30-50ms per char)
  - Random delays 25-45s between messages (mimics real browsing)
  - Deduplication: never message the same person twice
  - Name extraction must work (not "there")
  - Signal detection must match ACTUAL profile content, not LinkedIn UI text
  - Messages in Ganesh's real tone (casual, bro, blunt, short)
  - Role-aware: Campus Ambassador / Core Team / Founding Team
  - Form URL shared only in reply stage, not first message
"""

import json
import os
import time
import random
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════
MAX_PER_ROUND = 10
FORM_URL = "https://forms.gle/2NYjiunqeUk3WUDh9"
PHONE = "9441467303"
ALREADY_MESSAGED_FILE = Path("data-tracking/messaged_profiles.json")
OUTREACH_LOG_FILE = Path("data-tracking/outreach_log.json")
CHROME_PROFILE = Path("data-tracking/chrome-profile")

SEARCH_KEYWORDS = [
    # Karnataka / Tamil Nadu
    "campus ambassador engineering college Karnataka 2024",
    "student council secretary VTU college Bangalore",
    "cultural head college Chennai Tamil Nadu student",
    "club president engineering college Mysore Karnataka",
    # Maharashtra / Gujarat
    "campus ambassador Pune college Maharashtra student",
    "event organizer Mumbai engineering college student",
    "social media lead college Gujarat Ahmedabad student",
    # Andhra Pradesh / Telangana — new queries
    "IEEE student branch chair Hyderabad college",
    "hackathon organizer engineering college Vijayawada",
    "cultural secretary JNTU college Hyderabad student",
    # Uttar Pradesh / North India
    "NSS coordinator engineering college Lucknow UP",
    "student volunteer Noida college tech fest organizer",
    "design head college club Delhi NCR student",
    # Generic niche roles not tried yet
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
    'campus_ambassador': [
        "hey {name}, saw your campus ambassador stuff at {college}. building clstr.in and genuinely curious — do students there actually engage or is it mostly just for the certificate?",
        "hey {name}, noticed you're doing ambassador work at {college}. quick one — what kind of students actually show up vs just collect the title?",
        "hey {name}, you seem pretty active at {college}. I'm building something for campus communities, clstr.in. what's the real vibe there like?",
    ],
    'tedx': [
        "hey {name}, saw the TEDx work at {college}. how do you actually keep students engaged after the event ends?",
        "hey {name}, TEDx organizer at {college} is no small thing. genuinely curious — what's the hardest part of pulling it off?",
    ],
    'event_coordinator': [
        "hey {name}, saw your event work at {college}. what kind of events actually get real participation vs just headcount?",
        "hey {name}, you've coordinated events at {college} — honest question, what makes campus stuff actually stick vs stuff people forget next day?",
    ],
    'student_council': [
        "hey {name}, you're on the council at {college} so you'd know — what do students there actually need that nobody's building?",
        "hey {name}, student council at {college}. what's one thing everyone complains about but nobody fixes?",
    ],
    'club_president': [
        "hey {name}, saw you lead {signal} at {college}. what's the one thing missing that would actually make campus life better?",
        "hey {name}, you head {signal} at {college} — how does real engagement look there vs the performative kind?",
    ],
    'core_team_design': [
        "hey {name}, saw your design work. building clstr.in and looking for someone to own the creative side, not just make posters. what kind of design do you enjoy most?",
        "hey {name}, your design stuff caught my eye. I'm building clstr.in — is branding and visual identity something you'd want to own end to end?",
    ],
    'core_team_marketing': [
        "hey {name}, noticed your marketing work at {college}. building clstr.in and need someone who actually thinks about growth, not just posts. what kind of campaigns have you run?",
        "hey {name}, saw your marketing background. I'm working on clstr.in — is growth strategy something you're into beyond just content creation?",
    ],
    'startup_cell': [
        "hey {name}, startup cell at {college} — are people there actually shipping things or mostly attending talks about building?",
        "hey {name}, saw the startup cell work. honest question — how many folks there are actually building something vs just learning about it?",
    ],
    'default': [
        "hey {name}, saw your profile — you seem to actually do stuff at {college}. I'm building clstr.in, what's your main focus right now?",
        "hey {name}, noticed you're pretty active at {college}. what would actually make campus life better there, if you had to pick one thing?",
        "hey {name}, building clstr.in — a campus network for college students. saw your work at {college} and genuinely curious what the community vibe is like there?",
    ],
}

ROLE_MAP = {
    'campus_ambassador': 'Campus Ambassador',
    'tedx': 'Campus Ambassador',
    'event_coordinator': 'Campus Ambassador',
    'student_council': 'Campus Ambassador',
    'club_president': 'Campus Ambassador',
    'core_team_design': 'Core Team (Designing & Marketing)',
    'core_team_marketing': 'Core Team (Designing & Marketing)',
    'startup_cell': 'Founding Team',
    'default': 'Campus Ambassador',
}


# ═══════════════════════════════════════════════════════════════════
# DEDUP TRACKER
# ═══════════════════════════════════════════════════════════════════
def load_messaged():
    if ALREADY_MESSAGED_FILE.exists():
        return set(json.loads(ALREADY_MESSAGED_FILE.read_text()))
    return set()

def save_messaged(urls):
    ALREADY_MESSAGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    ALREADY_MESSAGED_FILE.write_text(json.dumps(sorted(urls), indent=2))


# ═══════════════════════════════════════════════════════════════════
# PROFILE EXTRACTION
# ═══════════════════════════════════════════════════════════════════

def extract_college(page_text):
    """Get clean college name from profile text."""
    edu_markers = ['engineering college', 'institute of technology', 'college of engineering',
                   'university', 'institute of management', 'polytechnic', 'college of science']
    skip_prefixes = ['you both', 'also studied', 'goes to', 'went to']

    for line in page_text.split('\n'):
        s = line.strip()
        sl = s.lower()
        if any(sl.startswith(p) for p in skip_prefixes):
            continue
        for marker in edu_markers:
            if marker in sl and 5 < len(s) < 80:
                return s

    for line in page_text.split('\n'):
        s = line.strip()
        sl = s.lower()
        if any(sl.startswith(p) for p in skip_prefixes):
            continue
        if any(k in s for k in ('College', 'Institute', 'University')) and 5 < len(s) < 80:
            return s
    return None


def detect_signal(page_text):
    """Detect the strongest signal from the profile's EXPERIENCE/ACTIVITY section only.
    Avoids matching LinkedIn UI text like 'Software Engineer' in nav bars."""
    lower = page_text.lower()

    # Only match these in the actual profile content, not LinkedIn chrome
    if 'tedx' in lower:
        return 'tedx', 'TEDx'
    if any(t in lower for t in ['startup cell', 'entrepreneurship cell', 'e-cell']):
        return 'startup_cell', 'Startup Cell'
    if 'student council' in lower or 'student union' in lower:
        return 'student_council', 'Student Council'
    if 'campus ambassador' in lower or 'brand ambassador' in lower:
        return 'campus_ambassador', ''

    # Design signals — must be in their actual roles, not LinkedIn UI
    if any(t in lower for t in ['graphic design', 'ui/ux', 'figma', 'design head',
                                 'creative head', 'visual design', 'design lead']):
        return 'core_team_design', 'Design'

    # Marketing signals
    if any(t in lower for t in ['marketing lead', 'social media manager', 'content creator',
                                 'digital marketing', 'marketing head', 'outreach lead']):
        return 'core_team_marketing', 'Marketing'

    # Club leadership
    if any(t in lower for t in ['president', 'vice president', 'chairperson']) and any(
            t in lower for t in ['club', 'society', 'cell', 'association']):
        # Try to find club name
        for line in page_text.split('\n'):
            s = line.strip()
            if ('Club' in s or 'Society' in s) and len(s) < 60:
                return 'club_president', s
        return 'club_president', 'the club'

    if 'event coordinator' in lower or 'event organizer' in lower or 'event head' in lower:
        return 'event_coordinator', ''

    return 'default', ''


def generate_message(name, college, signal_type, specific_signal):
    """Generate a single personalized message in Ganesh's tone."""
    first_name = name.split()[0] if name else 'there'
    college_text = college or 'your campus'

    templates = TEMPLATES.get(signal_type, TEMPLATES['default'])
    msg = random.choice(templates).format(
        name=first_name, college=college_text, signal=specific_signal or college_text
    )
    if len(msg) > 320:
        msg = msg[:317] + '...'
    return msg


# ═══════════════════════════════════════════════════════════════════
# INBOX REPLY LOGIC
# ═══════════════════════════════════════════════════════════════════
def contextual_reply(their_msg):
    """Reply in Ganesh's actual tone — short, raw, peer-to-peer."""
    m = their_msg.lower()

    # They want to know what clstr is
    if any(w in m for w in ['what is', 'tell me', "what's clstr", 'more about', 'what does', 'explain', 'clstr kya']):
        return random.choice([
            "clstr.in is basically a campus network — verified, private to each college. students connect with batchmates, alumni, real opportunities. we're onboarding campus leaders to shape how it rolls out. what does your college community look like rn?",
            "its a verified campus network bro — think of it like a private space for your college where students actually connect with each other and with opportunities. we're building the campus layer. what's the vibe at your college like?",
        ])

    # Positive / interested
    if any(w in m for w in ['interested', 'want to join', 'how do i apply', 'sign me up', "i'm in", 'i am in', 'count me in', 'sounds good', 'love to', 'definitely', 'sure', 'yes', 'okay', 'ok', 'great']):
        return f"perfect, fill this quick form and we'll take it from there: {FORM_URL}\n\ntakes 2 mins. we'll reach out within 48hrs. ping me on whatsapp if you have questions — {PHONE}"

    # They're busy
    if any(w in m for w in ['busy', 'exams', 'later', 'not now', 'maybe later', 'semester']):
        return random.choice([
            "that makes sense bro, take your time. i'll check back in a couple weeks",
            "all good, good luck with the exams. i'll follow up later",
        ])

    # Asking about time commitment
    if any(w in m for w in ['how many hours', 'commitment', 'time required', 'how much time']):
        return "flexible — roughly 3-5 hrs a week. you'd run campus activations and community stuff at your college. want me to send you the form so you can check role details?"

    # Asking about pay / compensation
    if any(w in m for w in ['pay', 'paid', 'salary', 'stipend', 'money', 'compensation']):
        return random.choice([
            "honestly not right now — we're early stage. but the experience of actually building something from ground up and leading at your campus is real. once we hit revenue we move to proper incentives",
            "not in a position to pay rn bro, we're early. but this isn't a college project — we're building it seriously. if you stay long term it turns into something real",
        ])

    # Generic positive but unclear
    if any(w in m for w in ['interesting', 'nice', 'cool', 'wow', 'good idea']):
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


# ═══════════════════════════════════════════════════════════════════
# BROWSER AUTOMATION — SAFE, SEQUENTIAL
# ═══════════════════════════════════════════════════════════════════
class OutreachBot:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
        self.wait = None

    def start(self):
        log.info("Starting Chrome...")
        opts = webdriver.ChromeOptions()
        profile_dir = str(CHROME_PROFILE.resolve())
        CHROME_PROFILE.mkdir(parents=True, exist_ok=True)
        opts.add_argument(f"user-data-dir={profile_dir}")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--start-maximized")
        # Anti-detection
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=opts)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.wait = WebDriverWait(self.driver, 15)
        log.info("✓ Browser ready")

    def login(self):
        self.driver.get("https://www.linkedin.com/feed/")
        time.sleep(4)
        if 'login' in self.driver.current_url or 'authwall' in self.driver.current_url:
            log.info("Logging in...")
            self.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(self.email)
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(6)
            log.info("✓ Logged in")
        else:
            log.info("✓ Already logged in")

    def human_delay(self, min_s=25, max_s=45):
        """Random delay between actions to look human."""
        d = random.uniform(min_s, max_s)
        log.info(f"  ⏳ Waiting {d:.0f}s (human delay)...")
        time.sleep(d)

    def human_type(self, element, text):
        """Type text character by character at human speed."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.03, 0.08))  # 30-80ms per char

    # ─── INBOX ───
    def check_inbox(self):
        log.info("\n── Checking inbox ──")
        try:
            # Verify window is still alive before navigating
            _ = self.driver.current_url
        except Exception:
            log.warning("  Browser window gone — skipping inbox")
            return
        try:
            self.driver.get("https://www.linkedin.com/messaging/")
            time.sleep(4)
            convos = self.driver.find_elements(By.CSS_SELECTOR, ".msg-conversation-listitem")
            unread = []
            for c in convos:
                try:
                    c.find_element(By.CSS_SELECTOR, ".notification-badge, .msg-conversation-listitem__unread-count")
                    unread.append(c)
                except Exception:
                    pass

            log.info(f"  Unread: {len(unread)}")
            replied = 0
            for convo in unread[:10]:
                try:
                    # Re-check window still alive before each convo
                    _ = self.driver.current_url
                    convo.click()
                    time.sleep(3)
                    msgs = self.driver.find_elements(By.CSS_SELECTOR, ".msg-s-event__content")
                    if not msgs:
                        continue
                    last = msgs[-1].text.strip()
                    if len(last) < 5:
                        continue
                    reply = contextual_reply(last)
                    if reply:
                        box = self.driver.find_element(By.CSS_SELECTOR, ".msg-form__contenteditable")
                        box.click()
                        time.sleep(1)
                        self.human_type(box, reply)
                        time.sleep(2)
                        try:
                            btn = self.driver.find_element(By.CSS_SELECTOR, "button.msg-form__send-button")
                            self.driver.execute_script("arguments[0].click();", btn)
                        except Exception:
                            from selenium.webdriver.common.keys import Keys
                            box.send_keys(Keys.RETURN)
                        log.info(f"  ✓ Replied: {reply[:60]}...")
                        replied += 1
                        time.sleep(random.uniform(8, 15))
                except Exception as e:
                    log.warning(f"  Convo error: {e}")
                    continue
            log.info(f"  ✓ Inbox done — replied to {replied}")
        except Exception as e:
            log.warning(f"  Inbox check failed (non-critical): {e}")

    # ─── SEARCH ───
    def search_profiles(self, messaged_set, limit=15):
        """Search LinkedIn and extract name+URL pairs from search result cards.
        Names are always visible in search results even when profiles are restricted.
        """
        results = []  # list of {url, name}
        seen_urls = set()

        for kw in SEARCH_KEYWORDS:
            if len(results) >= limit:
                break
            url = f"https://www.linkedin.com/search/results/people/?keywords={kw.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
            log.info(f"  Searching: {kw}")
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))

            # Each result card has a name span + profile link — grab both together
            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".entity-result__item, li.reusable-search__result-container"
            )
            for card in cards:
                try:
                    # Get the profile link
                    link_el = card.find_element(By.CSS_SELECTOR, "a[href*='/in/']")  
                    href = (link_el.get_attribute('href') or '').split('?')[0].rstrip('/')
                    if not href.startswith('https://www.linkedin.com/in/'):
                        continue
                    if 'ganeshtappiti' in href or href in messaged_set or href in seen_urls:
                        continue

                    # Get the name from the card's title/heading span
                    name = None
                    for name_sel in [
                        ".entity-result__title-text a span[aria-hidden='true']",
                        ".entity-result__title-text span[aria-hidden='true']",
                        ".app-aware-link span[aria-hidden='true']",
                        ".entity-result__title-line span",
                    ]:
                        try:
                            name_el = card.find_element(By.CSS_SELECTOR, name_sel)
                            candidate = name_el.text.strip()
                            if (2 <= len(candidate) <= 50
                                    and candidate.lower() not in ('linkedin member', 'linkedin', '')
                                    and not candidate.startswith('http')):
                                name = candidate
                                break
                        except Exception:
                            pass

                    # Fallback: grab any visible text from the card title area
                    if not name:
                        try:
                            title_el = card.find_element(By.CSS_SELECTOR, ".entity-result__title-text")
                            raw = title_el.text.strip().split('\n')[0]
                            if 2 <= len(raw) <= 50 and 'LinkedIn Member' not in raw:
                                name = raw
                        except Exception:
                            pass

                    if not name:
                        continue

                    results.append({'url': href, 'name': name})
                    seen_urls.add(href)
                    if len(results) >= limit:
                        break
                except Exception:
                    continue

            time.sleep(random.uniform(2, 4))

        return results[:limit]

    # ─── EXTRACT ───
    def extract_profile(self, url, known_name):
        """Navigate to profile, extract college and signal from page body.
        Name is already known from search results."""
        self.driver.get(url)
        time.sleep(random.uniform(3, 5))

        body = self.driver.find_element(By.TAG_NAME, "body").text
        college = extract_college(body)
        if not college:
            log.warning("  ⚠ Could not extract college — skipping")
            return None

        signal_type, specific_signal = detect_signal(body)
        role_fit = ROLE_MAP.get(signal_type, 'Campus Ambassador')

        return {
            'name': known_name,
            'url': url,
            'college': college,
            'signal_type': signal_type,
            'specific_signal': specific_signal,
            'role_fit': role_fit,
        }

    # ─── SEND DM ───
    def send_dm(self, profile_url, message):
        handle = profile_url.rstrip('/').split('/in/')[-1].split('/')[0]
        msg_url = f"https://www.linkedin.com/messaging/thread/new/?to={handle}"
        log.info(f"  → Opening messaging for {handle}")
        self.driver.get(msg_url)
        time.sleep(random.uniform(4, 6))

        if 'messaging' not in self.driver.current_url:
            log.warning("  ⚠ Redirected away from messaging — skipping")
            return False

        # Find compose box
        box = None
        for sel in [".msg-form__contenteditable", "div[role='textbox']", "div[contenteditable='true']"]:
            try:
                el = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                if el.is_displayed():
                    box = el
                    break
            except Exception:
                pass

        if not box:
            log.warning("  ⚠ Compose box not found — skipping")
            return False

        # Type message at human speed
        self.driver.execute_script("arguments[0].scrollIntoView(true);", box)
        time.sleep(1)
        ActionChains(self.driver).move_to_element(box).click().perform()
        time.sleep(1)
        self.human_type(box, message)
        time.sleep(random.uniform(1.5, 3))

        # Find Send button
        send = None
        try:
            send = self.driver.find_element(By.CSS_SELECTOR, "button.msg-form__send-button")
        except Exception:
            for btn in self.driver.find_elements(By.TAG_NAME, "button"):
                if btn.text.strip() == 'Send':
                    send = btn
                    break

        if not send:
            log.warning("  ⚠ Send button not found")
            return False

        self.driver.execute_script("arguments[0].scrollIntoView(true);", send)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", send)
        time.sleep(2)
        log.info(f"  ✓ SENT: {message}")
        return True

    def close(self):
        if self.driver:
            input("\nPress ENTER to close browser...")
            self.driver.quit()


# ═══════════════════════════════════════════════════════════════════
# MAIN CAMPAIGN
# ═══════════════════════════════════════════════════════════════════
def run_campaign():
    log.info(f"\n{'='*60}")
    log.info(f"clstr.in Outreach — Round of {MAX_PER_ROUND}")
    log.info(f"{'='*60}\n")

    Path('data-tracking').mkdir(exist_ok=True)
    messaged = load_messaged()
    log.info(f"Previously messaged: {len(messaged)} profiles")

    bot = OutreachBot(
        email=os.getenv("LINKEDIN_EMAIL", ""),
        password=os.getenv("LINKEDIN_PASSWORD", ""),
    )

    results = []
    sent_count = 0

    try:
        bot.start()
        bot.login()

        # Step 1: Check inbox first
        bot.check_inbox()

        # Step 2: Search
        log.info("\n── Searching for candidates ──")
        profile_candidates = bot.search_profiles(messaged, limit=MAX_PER_ROUND + 5)
        if not profile_candidates:
            log.error("No new profiles found")
            return
        log.info(f"✓ Found {len(profile_candidates)} new profiles\n")

        # Step 3: ONE AT A TIME
        for i, candidate in enumerate(profile_candidates, 1):
            if sent_count >= MAX_PER_ROUND:
                log.info(f"\n✓ Round complete — {MAX_PER_ROUND} messages sent")
                break

            url = candidate['url']
            known_name = candidate['name']

            log.info(f"\n── [{i}/{len(profile_candidates)}] ──")
            log.info(f"  Name: {known_name}")
            log.info(f"  URL:  {url}")

            # Extract college + signal (name already known)
            data = bot.extract_profile(url, known_name)
            if not data:
                continue

            log.info(f"  Name:    {data['name']}")
            log.info(f"  College: {data['college']}")
            log.info(f"  Signal:  {data['signal_type']}")
            log.info(f"  Role:    {data['role_fit']}")

            # Generate message
            msg = generate_message(
                data['name'], data['college'],
                data['signal_type'], data['specific_signal']
            )
            log.info(f"  Draft:   {msg[:80]}...")

            # Send
            ok = bot.send_dm(url, msg)
            if ok:
                sent_count += 1
                messaged.add(url)
                save_messaged(messaged)
                results.append({
                    'profile_url': url,
                    'name': data['name'],
                    'college': data['college'],
                    'role_fit': data['role_fit'],
                    'signal': data['signal_type'],
                    'message': msg,
                    'sent_at': datetime.now().isoformat(),
                })
                log.info(f"  ✓ ({sent_count}/{MAX_PER_ROUND} sent)")

                # HUMAN DELAY between messages
                if sent_count < MAX_PER_ROUND:
                    bot.human_delay(25, 45)
            else:
                log.warning("  ✗ Send failed — moving on")
                time.sleep(random.uniform(5, 10))

        # Save results
        with open(OUTREACH_LOG_FILE, 'w') as f:
            json.dump({
                'campaign_date': datetime.now().isoformat(),
                'messages_sent': sent_count,
                'results': results,
            }, f, indent=2)

        log.info(f"\n{'='*60}")
        log.info(f"DONE — {sent_count} messages sent | Log: {OUTREACH_LOG_FILE}")
        log.info(f"{'='*60}\n")

    finally:
        bot.close()


if __name__ == "__main__":
    run_campaign()
