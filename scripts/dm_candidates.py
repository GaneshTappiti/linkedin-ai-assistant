import time
import json
import os
import re
from collections import deque
from datetime import datetime
from urllib.parse import urlparse, urlunparse, quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchWindowException

# 10 Candidates to process (Excluding Candidate 1 which we already drafted for)
CANDIDATES = [
    {"url": "https://www.linkedin.com/in/yaswanthkumarkota/", "name": "Yaswanth", "college": "MVGR"},
    {"url": "https://www.linkedin.com/in/venu-patnaik/", "name": "Venu", "college": "MVGR"},
    {"url": "https://www.linkedin.com/in/tahir-hussain-516447306/", "name": "Tahir", "college": "your college"},
    {"url": "https://www.linkedin.com/in/sai-088083344/", "name": "Sai", "college": "your college"},
    {"url": "https://www.linkedin.com/in/abhishek-gangwar-179800363/", "name": "Abhishek", "college": "your college"},
    {"url": "https://www.linkedin.com/in/lochanmathukumilli/", "name": "Lochan", "college": "your college"},
    {"url": "https://www.linkedin.com/in/girish-hukkeri-b4621a345/", "name": "Girish", "college": "your college"},
    {"url": "https://www.linkedin.com/in/nikhil-kumar-4736253b0/", "name": "Nikhil", "college": "your college"},
    {"url": "https://www.linkedin.com/in/mananjainx/", "name": "Manan", "college": "your college"},
    {"url": "https://www.linkedin.com/in/shubham-singh-a6ab7334a/", "name": "Shubham", "college": "your college"}
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRACKING_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "data-tracking"))
TRACKING_FILE = os.path.join(TRACKING_DIR, "sent_candidates.json")
CHROME_PROFILE_DIR = os.path.join(TRACKING_DIR, "chrome-profile")
AUTOMATION_CONFIG_FILE = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "docs", "automation", "clstr_hiring_automation_config.json")
)
MAX_PROFILES_TO_SCAN = 150
S0_STAGE = "s0_search_and_score"
S1_STAGE = "s1_casual_opener"

def is_truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}

def load_automation_config():
    with open(AUTOMATION_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_message(name, college, config):
    template = config["message_templates"]["casual_opener"]
    return template.format(first_name=name, college_name=college)

def setup_driver():
    debugger_address = os.getenv("LINKEDIN_CHROME_DEBUGGER", "").strip()
    attach_only = is_truthy(os.getenv("LINKEDIN_ATTACH_ONLY", ""))
    disable_fallback = is_truthy(os.getenv("LINKEDIN_DISABLE_FALLBACK", "1"))
    if debugger_address:
        attach_options = webdriver.ChromeOptions()
        attach_options.debugger_address = debugger_address
        try:
            print(f"Attaching to existing Chrome debugger session at {debugger_address}...")
            attached_driver = webdriver.Chrome(options=attach_options)
            setattr(attached_driver, "_attached_to_existing", True)
            return attached_driver
        except WebDriverException as attach_error:
            if attach_only:
                raise RuntimeError(
                    f"Failed to attach to existing Chrome debugger session at {debugger_address}."
                ) from attach_error
            print("Could not attach to existing debugger session. Falling back to managed Chrome session.")
    elif attach_only:
        raise RuntimeError(
            "LINKEDIN_ATTACH_ONLY is enabled but LINKEDIN_CHROME_DEBUGGER is not set."
        )

    os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)
    options = webdriver.ChromeOptions()
    # Persist authenticated session in a dedicated Selenium profile directory.
    options.add_argument(f"user-data-dir={CHROME_PROFILE_DIR}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-resources")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    try:
        managed_driver = webdriver.Chrome(options=options)
        setattr(managed_driver, "_attached_to_existing", False)
        return managed_driver
    except WebDriverException as e:
        # Clean up stale Chromium singleton lock files from interrupted sessions.
        for lock_file in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
            lock_path = os.path.join(CHROME_PROFILE_DIR, lock_file)
            if os.path.exists(lock_path):
                try:
                    os.remove(lock_path)
                except OSError:
                    pass

        try:
            managed_driver_retry = webdriver.Chrome(options=options)
            setattr(managed_driver_retry, "_attached_to_existing", False)
            return managed_driver_retry
        except WebDriverException:
            if disable_fallback:
                raise RuntimeError(
                    f"Failed to launch Chrome with persistent profile at: {CHROME_PROFILE_DIR}. "
                    "Fallback profile launch is disabled to prevent opening extra windows."
                ) from e
            fallback_profile_dir = os.path.join(TRACKING_DIR, "chrome-profile-fallback")
            os.makedirs(fallback_profile_dir, exist_ok=True)
            fallback_options = webdriver.ChromeOptions()
            fallback_options.add_argument(f"user-data-dir={fallback_profile_dir}")
            fallback_options.add_argument("--profile-directory=Default")
            fallback_options.add_argument("--disable-dev-shm-usage")
            fallback_options.add_argument("--start-maximized")
            fallback_options.add_argument("--no-sandbox")
            fallback_options.add_argument("--disable-gpu")
            fallback_options.add_argument("--disable-web-resources")
            fallback_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            fallback_options.add_experimental_option("useAutomationExtension", False)
            print(
                "Persistent Chrome profile unavailable, switching to fallback profile. "
                "You may need to log in again."
            )
            try:
                fallback_driver = webdriver.Chrome(options=fallback_options)
                setattr(fallback_driver, "_attached_to_existing", False)
                return fallback_driver
            except WebDriverException as fallback_error:
                raise RuntimeError(
                    f"Failed to launch Chrome with persistent profile at: {CHROME_PROFILE_DIR} "
                    f"and fallback profile at: {fallback_profile_dir}. "
                    "Close conflicting Chrome sessions and run again."
                ) from fallback_error

def normalize_linkedin_url(url):
    parsed = urlparse(url.strip())
    clean_path = parsed.path.rstrip("/")
    normalized = urlunparse((
        (parsed.scheme or "https").lower(),
        parsed.netloc.lower(),
        clean_path,
        "",
        "",
        ""
    ))
    return normalized

def slug_to_display_name(profile_url):
    path = urlparse(profile_url).path.rstrip("/")
    slug = path.split("/")[-1]
    slug = re.sub(r"[-_]+", " ", slug)
    slug = re.sub(r"\d+", "", slug).strip()
    return slug.title() if slug else "there"

def build_search_keywords(config):
    candidate_sources = config.get("candidate_sources", {})
    keywords = []

    keywords.extend(candidate_sources.get("preferred_search_keywords", []))
    role_specific_search = candidate_sources.get("role_specific_search", {})
    for role_data in role_specific_search.values():
        keywords.extend(role_data.get("keywords", []))

    # Preserve order while removing duplicates/empties.
    seen = set()
    deduped = []
    for keyword in keywords:
        clean = (keyword or "").strip()
        if not clean or clean.lower() in seen:
            continue
        seen.add(clean.lower())
        deduped.append(clean)
    return deduped

def recover_window_if_closed(driver):
    try:
        handles = driver.window_handles
    except WebDriverException:
        return False

    if handles:
        try:
            driver.switch_to.window(handles[0])
            return True
        except WebDriverException:
            return False

    try:
        driver.switch_to.new_window("tab")
        return True
    except WebDriverException:
        return False

def safe_navigate(driver, url, attempts=2):
    for _ in range(attempts):
        try:
            driver.get(url)
            return True
        except NoSuchWindowException:
            if not recover_window_if_closed(driver):
                return False
        except WebDriverException as exc:
            if "target window already closed" in str(exc).lower():
                if not recover_window_if_closed(driver):
                    return False
                continue
            raise
    return False

def search_candidate_profiles(driver, keyword, excluded_urls, max_results=25):
    query = quote_plus(f"{keyword} India")
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={query}&origin=GLOBAL_SEARCH_HEADER"
    if not safe_navigate(driver, search_url):
        print(" Search skipped: unable to recover a browser window.")
        return []

    try:
        WebDriverWait(driver, 10).until(EC.url_contains("/search/results/people"))
    except Exception:
        return []

    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    anchors = driver.find_elements(By.XPATH, "//a[contains(@href,'/in/')]")
    results = []
    seen_local = set()

    for anchor in anchors:
        href = (anchor.get_attribute("href") or "").strip()
        if not href:
            continue
        normalized_url = normalize_linkedin_url(href)
        if "/in/" not in normalized_url:
            continue
        if normalized_url in excluded_urls or normalized_url in seen_local:
            continue

        anchor_text = (anchor.text or "").strip()
        if not anchor_text:
            anchor_text = (anchor.get_attribute("aria-label") or "").strip()
        name = anchor_text.split("\n")[0].strip() if anchor_text else slug_to_display_name(normalized_url)

        results.append({
            "url": normalized_url,
            "name": name,
            "college": "your college",
        })
        seen_local.add(normalized_url)

        if len(results) >= max_results:
            break

    return results

def find_first_clickable(driver, xpaths, timeout_seconds=6):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for xpath in xpaths:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    return element
        time.sleep(0.2)
    return None

def find_first_visible(driver, xpaths, timeout_seconds=6):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for xpath in xpaths:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if element.is_displayed():
                    return element
        time.sleep(0.2)
    return None

def wait_for_message_editor(driver, timeout_seconds=8):
    editor_xpaths = [
        "//div[contains(@class,'msg-form__contenteditable') and @contenteditable='true']",
        "//div[@role='textbox' and @contenteditable='true']",
        "//div[@contenteditable='true' and contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//textarea[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//textarea[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//textarea[contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
    ]
    return find_first_visible(driver, editor_xpaths, timeout_seconds=timeout_seconds)

def score_band_label(score, config):
    bands = config.get("scoring", {}).get("bands", [])
    for band in bands:
        range_text = (band.get("range") or "").strip()
        if "-" not in range_text:
            continue
        try:
            low_text, high_text = range_text.split("-", 1)
            low = int(low_text.strip())
            high = int(high_text.strip())
        except ValueError:
            continue
        if low <= score <= high:
            return band.get("label", "unknown")
    return "unknown"

def candidate_state_for_score(score, config):
    label = score_band_label(score, config)
    if label == "high_priority":
        return "scored"
    if label == "nurture":
        return "nurture"
    if label == "defer":
        return "rejected"
    return "scored"

def validate_stage_message(message_text, stage_id, config):
    guardrails = (
        config.get("conversation_workflow", {})
        .get("stage_message_guardrails", {})
        .get(stage_id, {})
    )
    message_lower = message_text.lower()

    for forbidden in guardrails.get("must_not_include", []):
        token = (forbidden or "").strip().lower()
        if token and token in message_lower:
            return False, f"Blocked by stage guardrail: contains forbidden token '{forbidden}'."

    required = guardrails.get("must_include", [])
    for must_include in required:
        token = (must_include or "").strip().lower()
        if token and token not in message_lower:
            return False, f"Blocked by stage guardrail: missing required token '{must_include}'."

    must_include_any = guardrails.get("must_include_any", [])
    if must_include_any:
        normalized_tokens = [
            (token or "").strip().lower()
            for token in must_include_any
            if (token or "").strip()
        ]
        if normalized_tokens and not any(token in message_lower for token in normalized_tokens):
            return False, (
                "Blocked by stage guardrail: expected at least one of "
                f"{must_include_any}."
            )

    return True, ""

def is_allowed_stage_transition(from_stage, to_stage, config):
    transitions = config.get("conversation_workflow", {}).get("allowed_stage_transitions", {})
    if not transitions:
        return True
    return to_stage in transitions.get(from_stage, [])

def infer_current_year_from_profile(profile_text):
    text = profile_text.lower()
    explicit_year_patterns = [
        r"\b([1-4])(?:st|nd|rd|th)?\s*year\b",
        r"\byear\s*([1-4])\b",
        r"\b([1-4])\s*/\s*4\b",
    ]
    for pattern in explicit_year_patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    if "final year" in text:
        return 4

    grad_match = re.search(
        r"\b(?:class of|batch of|graduating in|graduation(?:\s+year)?[:\s-]*)\s*(20\d{2})\b",
        text,
    )
    if grad_match:
        grad_year = int(grad_match.group(1))
        current_year = datetime.now().year
        years_until_graduation = grad_year - current_year
        inferred = 4 - years_until_graduation
        if 1 <= inferred <= 4:
            return inferred

    return None

def infer_student_status(profile_text):
    text = profile_text.lower()
    if re.search(r"\b(alumni|graduated|graduate\s+\d{4}|former student|ex[- ]student)\b", text):
        return False
    if re.search(r"\b(student|undergrad|undergraduate|btech|b\.tech|college|university)\b", text):
        return True
    return None

def evaluate_profile_eligibility(profile_context, config):
    guardrails = config.get("eligibility_guardrails", {})
    reasons = []

    inferred_year = profile_context.get("inferred_current_year")
    is_current_student = profile_context.get("is_current_student")
    allowed_years = set(guardrails.get("allowed_years", []))
    final_year_allowed = guardrails.get("final_year_allowed", False)

    if guardrails.get("current_college_students_only", False) and is_current_student is False:
        reasons.append("not_current_student")

    if inferred_year is not None:
        if allowed_years and inferred_year not in allowed_years:
            reasons.append("year_not_in_allowed_range")
        if not final_year_allowed and inferred_year == 4:
            reasons.append("final_year_student")

    return len(reasons) == 0, reasons

def load_sent_candidates():
    if not os.path.exists(TRACKING_FILE):
        return []
    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return []

def save_tracking(tracking_data):
    os.makedirs(TRACKING_DIR, exist_ok=True)
    existing = load_sent_candidates()

    tracked_url = normalize_linkedin_url(tracking_data["url"])
    existing = [
        item for item in existing
        if normalize_linkedin_url(item.get("url", "")) != tracked_url
    ]

    existing.append(tracking_data)
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4)

def score_candidate(profile_text, config):
    text = profile_text.lower()
    dimensions = config.get("scoring", {}).get("dimensions", [])
    raw_max = len(dimensions) * 5 if dimensions else 25

    campus_hits = len(re.findall(r"\b(ambassador|student council|club|coordinator|community|event|president|chapter|cell|representative)\b", text))
    execution_hits = len(re.findall(r"\b(led|organized|launched|managed|executed|campaign|built|hosted|spearheaded|founded|coordinated|drove|conducted)\b", text))
    communication_hits = len(re.findall(r"\b(founder|lead|manager|organizer|speaker|host|content creator|public speaking|debate)\b", text))
    network_hits = len(re.findall(r"\b(connections|followers|community|network|reach|engagement|members|audience|linkedin)\b", text))
    college_hits = len(re.findall(r"\b(college|campus|university|institute|student)\b", text))

    raw_score = min(campus_hits, 5) + min(execution_hits, 5) + min(communication_hits, 5) + min(network_hits, 5) + min(college_hits, 5)
    normalized = round((raw_score / raw_max) * config.get("scoring", {}).get("max_total", 20))

    if execution_hits > 0:
        specific_signal = "you've shown clear execution in student activities"
    elif campus_hits > 0:
        specific_signal = "you seem active in your campus ecosystem"
    else:
        specific_signal = "your profile reflects strong student potential"

    return normalized, specific_signal

def extract_profile_context(driver):
    body_text = driver.find_element(By.TAG_NAME, "body").text
    headline = ""
    headline_nodes = driver.find_elements(By.XPATH, "//div[contains(@class,'text-body-medium') and string-length(normalize-space()) > 0]")
    if headline_nodes:
        headline = headline_nodes[0].text.strip()

    college_name = None
    college_match = re.search(r"([A-Z][A-Za-z&\.\- ]+(College|University|Institute)[A-Za-z&\.\- ]*)", body_text)
    if college_match:
        college_name = college_match.group(1).strip()

    inferred_current_year = infer_current_year_from_profile(body_text)
    is_current_student = infer_student_status(body_text)

    return {
        "body_text": body_text,
        "headline": headline,
        "college_name": college_name,
        "inferred_current_year": inferred_current_year,
        "is_current_student": is_current_student,
    }

def open_message_composer(driver):
    direct_message_xpaths = [
        "//button[not(@disabled) and (.//span[normalize-space()='Message'] or normalize-space()='Message')]",
        "//a[.//span[normalize-space()='Message'] or normalize-space()='Message']",
        "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message') and not(@disabled)]",
        "//a[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
    ]
    direct_message_button = find_first_clickable(driver, direct_message_xpaths, timeout_seconds=5)
    if direct_message_button:
        driver.execute_script("arguments[0].click();", direct_message_button)
        if wait_for_message_editor(driver, timeout_seconds=7):
            return True

    more_button_xpaths = [
        "//button[.//span[normalize-space()='More'] or .//span[normalize-space()='More actions']]",
        "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'more actions')]",
    ]
    more_button = find_first_clickable(driver, more_button_xpaths, timeout_seconds=4)
    if more_button:
        driver.execute_script("arguments[0].click();", more_button)
        time.sleep(0.8)
        menu_message_xpaths = [
            "//div[@role='button' and (.//span[normalize-space()='Message'] or normalize-space()='Message')]",
            "//li[@role='menuitem']//div[.//span[normalize-space()='Message'] or normalize-space()='Message']",
            "//li[@role='menuitem']//span[normalize-space()='Message']",
            "//div[@role='button' and (.//span[contains(normalize-space(),'InMail')] or contains(normalize-space(),'InMail'))]",
            "//li[@role='menuitem']//span[contains(normalize-space(),'InMail')]",
        ]
        message_in_more = find_first_clickable(driver, menu_message_xpaths, timeout_seconds=4)
        if message_in_more:
            driver.execute_script("arguments[0].click();", message_in_more)
            if wait_for_message_editor(driver, timeout_seconds=7):
                return True

    return False

def send_direct_message(driver, message_text):
    textbox_xpaths = [
        "//div[contains(@class,'msg-form__contenteditable') and @role='textbox']",
        "//div[@role='textbox' and contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//div[@contenteditable='true' and @role='textbox']",
        "//div[@contenteditable='true' and contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//textarea[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//textarea[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
        "//textarea[contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message')]",
    ]
    textbox = find_first_visible(driver, textbox_xpaths, timeout_seconds=10)
    if not textbox:
        raise RuntimeError("Message textbox not found in composer.")

    subject_xpaths = [
        "//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'subject')]",
        "//input[contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'subject')]",
        "//input[contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'subject')]",
    ]
    subject_box = find_first_clickable(driver, subject_xpaths, timeout_seconds=2)
    if subject_box and not (subject_box.get_attribute("value") or "").strip():
        subject_box.send_keys("Quick student leadership chat")

    textbox.click()
    if (textbox.tag_name or "").lower() == "textarea":
        textbox.clear()
        textbox.send_keys(message_text)
    else:
        textbox.send_keys(Keys.CONTROL, "a")
        textbox.send_keys(Keys.BACKSPACE)
        textbox.send_keys(message_text)

    send_button_xpaths = [
        "//button[contains(@class,'msg-form__send-button') and not(@disabled)]",
        "//button[not(@disabled) and (.//span[normalize-space()='Send'] or normalize-space()='Send')]",
        "//button[not(@disabled) and (.//span[contains(normalize-space(),'Send InMail')] or contains(normalize-space(),'Send InMail'))]",
        "//button[not(@disabled) and contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'send')]",
    ]
    send_btn = find_first_clickable(driver, send_button_xpaths, timeout_seconds=10)
    if not send_btn:
        raise RuntimeError("Send button not available in composer.")

    send_btn.click()
    time.sleep(2)

def run_outreach(target_successful_sends=10, max_profiles_to_scan=MAX_PROFILES_TO_SCAN):
    print("Launching browser... Please log into LinkedIn if prompted.")
    config = load_automation_config()
    driver = setup_driver()
    driver.get("https://www.linkedin.com/feed")

    existing_sent = load_sent_candidates()
    sent_urls = {
        normalize_linkedin_url(item.get("url", ""))
        for item in existing_sent
        if item.get("url") and item.get("status", "sent") == "sent"
    }
    print(f"Loaded {len(sent_urls)} already-sent accounts from tracking.")
    strict_sequence = config.get("conversation_workflow", {}).get("strict_sequence_enforced", False)
    print(f"Strict sequence enforcement: {'ON' if strict_sequence else 'OFF'}")
    
    # Wait for feed to load (or login page if not authenticated)
    try:
        # Try multiple selectors for feed detection
        WebDriverWait(driver, 10).until(EC.url_contains("/feed"))
        time.sleep(3)  # Extra wait for JS to fully render
        print("Feed page loaded successfully. Starting outreach...")
    except:
        print("Waiting for login page... If you see login, please log in and wait.")
        WebDriverWait(driver, 300).until(EC.url_contains("/feed"))
        time.sleep(5)
        print("Login successful! Starting outreach...")

    sent_this_run = 0
    analyzed_this_run = 0
    search_keywords = build_search_keywords(config)
    candidate_queue = deque(CANDIDATES)
    queued_urls = {normalize_linkedin_url(candidate["url"]) for candidate in CANDIDATES}
    search_keyword_index = 0
    search_rounds_without_new_candidates = 0

    while sent_this_run < target_successful_sends and analyzed_this_run < max_profiles_to_scan:
        if not candidate_queue:
            if not search_keywords:
                print("No search keywords configured. Stopping run.")
                break

            current_keyword = search_keywords[search_keyword_index % len(search_keywords)]
            search_keyword_index += 1
            print(f"\nSearching additional candidates using keyword: {current_keyword}")
            discovered = search_candidate_profiles(
                driver,
                current_keyword,
                excluded_urls=sent_urls.union(queued_urls),
                max_results=25,
            )
            if not discovered:
                search_rounds_without_new_candidates += 1
                print(" No new candidates discovered for this keyword.")
                if search_rounds_without_new_candidates >= len(search_keywords):
                    print("Exhausted search keywords without finding new profiles. Stopping.")
                    break
                continue

            search_rounds_without_new_candidates = 0
            for profile in discovered:
                normalized_discovered_url = normalize_linkedin_url(profile["url"])
                if normalized_discovered_url in queued_urls:
                    continue
                candidate_queue.append(profile)
                queued_urls.add(normalized_discovered_url)
            print(f" Added {len(discovered)} candidate(s) to the queue.")
            continue

        candidate = candidate_queue.popleft()
        candidate_url = normalize_linkedin_url(candidate["url"])
        if candidate_url in sent_urls:
            print(f"\nSkipping already sent account: {candidate['name']} ({candidate['url']})")
            continue

        print(f"\nScanning profile: {candidate['name']}")
        if not safe_navigate(driver, candidate["url"]):
            print(" Could not open profile because browser window is unavailable. Skipping.")
            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "window_unavailable",
                "stage": S0_STAGE,
                "candidate_state": "sync_pending",
                "timestamp": datetime.now().isoformat()
            })
            continue
        time.sleep(4)
        analyzed_this_run += 1

        profile_context = extract_profile_context(driver)
        score, specific_signal = score_candidate(profile_context["body_text"], config)
        min_outreach_score = config.get("scoring", {}).get("minimum_for_outreach", 11)
        band_label = score_band_label(score, config)
        candidate_state = candidate_state_for_score(score, config)
        inferred_college = profile_context["college_name"] or candidate.get("college", "your college")
        msg = generate_message(candidate["name"], inferred_college, config)
        eligible, ineligibility_reasons = evaluate_profile_eligibility(profile_context, config)
        print(f"Analyzed {candidate['name']} | score={score}/20 | band={band_label} | signal={specific_signal}")
        print(f"Draft ready for {candidate['name']}: {msg}")

        if not eligible:
            print(f" Ineligible based on profile guardrails: {', '.join(ineligibility_reasons)}. Skipping send.")
            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "deferred_ineligible",
                "stage": S0_STAGE,
                "candidate_state": "rejected",
                "score": score,
                "score_band": band_label,
                "specific_signal": specific_signal,
                "inferred_current_year": profile_context.get("inferred_current_year"),
                "is_current_student": profile_context.get("is_current_student"),
                "ineligibility_reasons": ineligibility_reasons,
                "timestamp": datetime.now().isoformat()
            })
            continue

        if score < min_outreach_score:
            print(f" Score below outreach gate ({min_outreach_score}). Skipping send.")
            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "deferred_low_score",
                "stage": S0_STAGE,
                "candidate_state": candidate_state,
                "score": score,
                "score_band": band_label,
                "specific_signal": specific_signal,
                "inferred_current_year": profile_context.get("inferred_current_year"),
                "is_current_student": profile_context.get("is_current_student"),
                "timestamp": datetime.now().isoformat()
            })
            continue

        if strict_sequence and not is_allowed_stage_transition(S0_STAGE, S1_STAGE, config):
            transition_error = f"Stage transition blocked: {S0_STAGE} -> {S1_STAGE} is not allowed."
            print(f" {transition_error}")
            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "blocked_transition",
                "stage": S0_STAGE,
                "candidate_state": "sync_pending",
                "score": score,
                "score_band": band_label,
                "specific_signal": specific_signal,
                "error": transition_error,
                "timestamp": datetime.now().isoformat()
            })
            continue

        valid_message, validation_reason = validate_stage_message(msg, S1_STAGE, config)
        if not valid_message:
            print(f" Message blocked by guardrails: {validation_reason}")
            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "blocked_guardrail",
                "stage": S1_STAGE,
                "candidate_state": "sync_pending",
                "score": score,
                "score_band": band_label,
                "specific_signal": specific_signal,
                "inferred_current_year": profile_context.get("inferred_current_year"),
                "is_current_student": profile_context.get("is_current_student"),
                "error": validation_reason,
                "timestamp": datetime.now().isoformat()
            })
            continue
        
        try:
            composer_opened = open_message_composer(driver)
            if not composer_opened:
                print(" Message composer unavailable on this profile. Skipping.")
                save_tracking({
                    "name": candidate["name"],
                    "url": candidate["url"],
                    "status": "no_message",
                    "stage": S1_STAGE,
                    "candidate_state": "sync_pending",
                    "score": score,
                    "score_band": band_label,
                    "specific_signal": specific_signal,
                    "inferred_current_year": profile_context.get("inferred_current_year"),
                    "is_current_student": profile_context.get("is_current_student"),
                    "timestamp": datetime.now().isoformat()
                })
                continue

            print(" Message composer opened. Sending...")
            send_direct_message(driver, msg)
            print(" ✓ Message sent successfully!")

            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "sent",
                "stage": S1_STAGE,
                "candidate_state": "outreached",
                "score": score,
                "score_band": band_label,
                "message_template": "casual_opener",
                "specific_signal": specific_signal,
                "inferred_current_year": profile_context.get("inferred_current_year"),
                "is_current_student": profile_context.get("is_current_student"),
                "timestamp": datetime.now().isoformat()
            })
            sent_urls.add(candidate_url)
            sent_this_run += 1
            print(" -> Marked as sent.")
            time.sleep(10)
              
        except Exception as e:
            print(f" Could not automate {candidate['name']}. Error: {e}")
            save_tracking({
                "name": candidate["name"],
                "url": candidate["url"],
                "status": "error",
                "stage": S1_STAGE,
                "candidate_state": "sync_pending",
                "score": score,
                "score_band": band_label,
                "specific_signal": specific_signal,
                "inferred_current_year": profile_context.get("inferred_current_year"),
                "is_current_student": profile_context.get("is_current_student"),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })

    print(
        f"\nRun complete. Profiles analyzed: {analyzed_this_run}, "
        f"successful sends: {sent_this_run}."
    )
    if getattr(driver, "_attached_to_existing", False):
        print("Attached session mode: leaving your existing Chrome window open.")
    else:
        driver.quit()

if __name__ == "__main__":
    run_outreach(target_successful_sends=10)
