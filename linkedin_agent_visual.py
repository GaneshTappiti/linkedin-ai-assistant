"""
LinkedIn Post Publisher - Antigravity Edition
Uses the real Chrome profile directly (no temp copy).
Image goes in via clipboard Ctrl+V (browser cannot access local files directly).
Auto-logins with credentials if session not saved.
"""

import os
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ── CONFIG ─────────────────────────────────────────────────────────────────
PROFILE_DIR = Path(__file__).parent / "data-tracking" / "chrome-profile"
EMAIL       = os.getenv("LINKEDIN_EMAIL", "")
PASSWORD    = os.getenv("LINKEDIN_PASSWORD", "")
IMAGE_PATH  = r"C:\Users\2005g\.gemini\antigravity\brain\b5aea9ca-3754-43d2-a111-556bc9dd7399\solo_founder_no_hiring_1779951441586.png"

POST_TEXT = """\
Hiring early used to be the flex.

Now it's the liability.

AI compresses execution so fast that coordination has become the new cost. Every meeting, every approval chain, every new hire you add - that's coordination overhead eating into your build speed.

One founder with sharp AI loops is moving faster than a 10-person team with onboarding rituals.

I'm seeing this with clstr.in. Every time I thought "we need more people for this," the real answer was "we need a better system."

The builders winning right now aren't the ones hiring fastest.

They're the ones who kept the team small and the loops tight.

Are you still hiring before validating - or building first?

#BuildInPublic #AI #Startups"""


# ── HELPERS ────────────────────────────────────────────────────────────────

def copy_image_to_clipboard(image_path):
    print("[+] Copying image to clipboard via PowerShell...")
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        f"$img = [System.Drawing.Image]::FromFile('{image_path}'); "
        "[System.Windows.Forms.Clipboard]::SetImage($img); "
        "Write-Output 'DONE'"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        capture_output=True, text=True
    )
    if "DONE" in result.stdout:
        print("    [OK] Image on clipboard.")
    else:
        print(f"    [WARN] Clipboard stderr: {result.stderr.strip()}")


def kill_chrome():
    print("[+] Killing any existing Chrome processes...")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    time.sleep(2)
    print("    [OK] Chrome killed.")


def try_click(page, selectors, label, timeout=5000):
    """Try each selector in order, click the first visible one. Returns True on success."""
    for sel in selectors:
        try:
            el = page.locator(sel).first
            el.wait_for(state="visible", timeout=timeout)
            el.click()
            print(f"    [OK] {label} clicked -> {sel}")
            return True
        except Exception:
            continue
    print(f"    [FAIL] Could not click: {label}")
    return False


# ── MAIN ───────────────────────────────────────────────────────────────────

def post_to_linkedin(post_text, image_path):

    # STEP 0: Copy image to clipboard BEFORE launching browser
    copy_image_to_clipboard(image_path)
    kill_chrome()

    print(f"\n[+] Launching Chrome with profile: {PROFILE_DIR.resolve()}")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR.resolve()),
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized",
                "--disable-infobars",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            ignore_https_errors=True,
        )

        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # ── STEP 1: Go to feed ─────────────────────────────────────────────
        print("[+] Navigating to https://www.linkedin.com/feed/ ...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        print(f"    Current URL: {page.url}")

        # ── STEP 2: Login if not on feed ───────────────────────────────────
        if not page.url.startswith("https://www.linkedin.com/feed"):
            print("[+] Not on feed - checking session via /login redirect...")
            # Navigate to /login — if session is valid it will auto-redirect to /feed
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            print(f"    URL after /login navigate: {page.url}")

            if page.url.startswith("https://www.linkedin.com/feed"):
                # Session is valid — LinkedIn redirected us automatically
                print("[OK] Session valid - auto-redirected to feed.")

            else:
                # Truly on login page - fill credentials
                print("[+] On login page - filling credentials...")
                try:
                    page.wait_for_selector("#username", timeout=5000)
                    page.fill("#username", EMAIL)
                    page.wait_for_timeout(400)
                    page.fill("#password", PASSWORD)
                    page.wait_for_timeout(400)
                    page.click('button[type="submit"]')
                    print("    Submitted - waiting 10s...")
                    page.wait_for_timeout(10000)
                    print(f"    URL after login: {page.url}")
                except Exception as e:
                    page.screenshot(path="debug_login_error.png")
                    print(f"[FAIL] Login form error: {e}")
                    ctx.close()
                    return

                if not page.url.startswith("https://www.linkedin.com/feed"):
                    page.screenshot(path="debug_login_failed.png")
                    print("[FAIL] Not on feed after login. Screenshot: debug_login_failed.png")
                    print(f"       URL: {page.url}")
                    ctx.close()
                    return

        print("[OK] On LinkedIn feed!")

        # -- Step 3: Open post composer -----------------------------------------
        print("[+] Opening post composer...")
        # Screenshot shows a rounded input bar with text 'Start a post'
        # It is a div/button inside .share-box-feed-entry
        opened = try_click(page, [
            # The exact placeholder text bar visible in screenshot
            'div.share-box-feed-entry__top-bar button',
            'div.share-box-feed-entry__top-bar',
            'div.share-box-feed-entry__triggers button',
            'div.share-box-feed-entry__triggers',
            # The rounded pill input that says 'Start a post'
            'div[class*="share-box-feed-entry"] button',
            # Text-based fallbacks
            ':text("Start a post")',
            'button:has-text("Start a post")',
            'span:has-text("Start a post")',
            # Any clickable element in the share box area
            'div[class*="share-box"] button',
            'div[class*="share-creation"]',
        ], "Start a post")

        if not opened:
            # Nuclear fallback: JS click on any element containing 'Start a post'
            print("    [+] Trying JS fallback for Start a post...")
            clicked = page.evaluate("""
                () => {
                    const all = document.querySelectorAll('button, div, span');
                    for (const el of all) {
                        if (el.innerText && el.innerText.trim() === 'Start a post') {
                            el.click();
                            return el.tagName + '.' + el.className;
                        }
                    }
                    return null;
                }
            """)
            if clicked:
                print(f"    [OK] JS clicked: {clicked}")
                opened = True
            else:
                page.screenshot(path="debug_linkedin_feed.png")
                print("[FAIL] Could not open composer. Screenshot: debug_linkedin_feed.png")
                ctx.close()
                return

        page.wait_for_timeout(3000)

        # ── STEP 4: Focus the text editor ──────────────────────────────────
        print("[+] Focusing text editor...")
        focused = try_click(page, [
            'div.ql-editor',
            'div[role="textbox"]',
            'div[contenteditable="true"]',
            'div[aria-label*="editor" i]',
            'div[data-placeholder*="mind" i]',
            'div[data-placeholder]',
        ], "Text editor")

        if not focused:
            page.screenshot(path="debug_linkedin_editor.png")
            print("[FAIL] Could not focus editor. Screenshot: debug_linkedin_editor.png")
            ctx.close()
            return

        page.wait_for_timeout(1000)

        # ── STEP 5: Paste image via clipboard ──────────────────────────────
        # Browser cannot access local files directly, so we use clipboard paste.
        print("[+] Pasting image from clipboard (Ctrl+V)...")
        page.keyboard.press("Control+V")
        page.wait_for_timeout(4000)
        page.screenshot(path="debug_after_paste.png")
        print("    Screenshot after paste: debug_after_paste.png")

        # ── STEP 6: Type the post text ─────────────────────────────────────
        print("[+] Typing post text (human-speed, ~28ms/char)...")
        for char in post_text:
            page.keyboard.type(char, delay=28)
        page.wait_for_timeout(2000)
        page.screenshot(path="debug_before_post.png")
        print("    Screenshot before posting: debug_before_post.png")

        # ── STEP 7: Click Post ─────────────────────────────────────────────
        print("[+] Clicking Post button...")
        posted = try_click(page, [
            'button.share-actions__primary-action',
            'button[aria-label="Post"]',
            'button:has-text("Post")',
            'div[aria-label="Post"]',
        ], "Post button")

        if not posted:
            page.screenshot(path="debug_post_btn_failed.png")
            print("[FAIL] Could not click Post. Screenshot: debug_post_btn_failed.png")
        else:
            print("[OK] Post button clicked!")
            page.wait_for_timeout(6000)
            page.screenshot(path="debug_success.png")
            print("[OK] Done! Success screenshot: debug_success.png")

        ctx.close()
        print("\n[DONE] Browser closed.")


if __name__ == "__main__":
    post_to_linkedin(POST_TEXT, IMAGE_PATH)
