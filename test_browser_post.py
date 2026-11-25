"""
test_browser_post.py
====================
Tests ONLY the browser automation part of the posting pipeline.
Uses a short dummy post text so we can verify the browser opens,
logs in, finds the composer, and can type — WITHOUT actually posting.

Run: python -X utf8 test_browser_post.py
"""

import asyncio
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_PROFILE = Path("data-tracking/chrome-profile").resolve()

# Short test text — we will NOT click Post (dry run)
TEST_POST_TEXT = "Testing browser automation - do not post. #test"


async def test_browser_open():
    """
    Dry-run test:
    1. Opens Chrome with saved profile
    2. Navigates to LinkedIn feed
    3. Clicks 'Start a post'
    4. Finds text area
    5. Types test text
    6. STOPS before clicking Post (does NOT post)
    Reports pass/fail for each step.
    """
    from playwright.async_api import async_playwright

    tmp_profile = tempfile.mkdtemp(prefix="li-test-")
    print(f"\n  Copying Chrome profile to temp: {tmp_profile}")
    shutil.copytree(str(CHROME_PROFILE), tmp_profile, dirs_exist_ok=True)
    print("  Profile copied.\n")

    results = {
        "browser_open": False,
        "feed_loaded": False,
        "start_post_clicked": False,
        "text_area_found": False,
        "text_typed": False,
    }

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
            results["browser_open"] = True
            print("  [PASS] Browser opened.")

            page = context.pages[0] if context.pages else await context.new_page()

            # Step 1: Navigate to LinkedIn feed
            print("\n  Navigating to LinkedIn feed...")
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            if "login" in page.url or "authwall" in page.url:
                print(f"  [FAIL] Session expired — URL: {page.url}")
                await context.close()
                return results

            results["feed_loaded"] = True
            print(f"  [PASS] Feed loaded: {page.url}")

            # Scroll to top to expose the 'Start a post' box
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(2)

            # Step 2: Click Start a post
            print("\n  Clicking 'Start a post'...")
            clicked = False

            # Try standard selectors first
            for sel in [
                "button.share-box-feed-entry__trigger",
                "button[class*='share-box-feed-entry__trigger']",
                "button:has-text('Start a post')",
                ".share-box-feed-entry__trigger",
                "div.share-box-feed-entry__top-bar button",
                "div[class*='share-box-feed-entry'] button:first-child",
                "div[class*='share-creation-state'] button",
                "[placeholder='Start a post']",
                "[aria-placeholder='Start a post']",
            ]:
                try:
                    el = await page.wait_for_selector(sel, timeout=4000)
                    if el:
                        await el.click()
                        clicked = True
                        print(f"  [PASS] 'Start a post' clicked (selector: {sel})")
                        break
                except Exception:
                    continue

            # JS fallback: find any button/div whose text includes 'Start a post'
            if not clicked:
                print("  Trying JS text-search fallback...")
                clicked = await page.evaluate("""
                    () => {
                        const all = document.querySelectorAll('button, div[role=button], input[placeholder]');
                        for (const el of all) {
                            const t = (el.textContent || el.getAttribute('placeholder') || '').trim();
                            if (t.toLowerCase().includes('start a post') || 
                                t.toLowerCase().includes('what do you want to talk about')) {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if clicked:
                    print("  [PASS] 'Start a post' clicked via JS fallback.")

            if not clicked:
                print("  [FAIL] Could not find 'Start a post' button.")
                await page.screenshot(path="test_fail_start_post.png")
                print("  Screenshot saved: test_fail_start_post.png")
                await context.close()
                return results

            results["start_post_clicked"] = True
            await asyncio.sleep(2)

            # Step 3: Find text area
            print("\n  Locating post text area...")
            text_area = None
            for sel in [
                "div.ql-editor[contenteditable='true']",
                "div[contenteditable='true'][data-placeholder]",
                "div.share-creation-state__text-editor div[contenteditable='true']",
                "div[role='textbox']",
                "div.editor-content div[contenteditable='true']",
            ]:
                try:
                    text_area = await page.wait_for_selector(sel, timeout=5000)
                    if text_area:
                        print(f"  [PASS] Text area found (selector: {sel})")
                        break
                except Exception:
                    continue

            if not text_area:
                print("  [FAIL] Text area not found.")
                await page.screenshot(path="test_fail_text_area.png")
                print("  Screenshot saved: test_fail_text_area.png")
                await context.close()
                return results

            results["text_area_found"] = True

            # Step 4: Type test text (dry run)
            await text_area.click()
            await asyncio.sleep(0.5)
            print(f"\n  Typing test text ({len(TEST_POST_TEXT)} chars)...")
            for char in TEST_POST_TEXT:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.04, 0.09))

            results["text_typed"] = True
            print("  [PASS] Text typed successfully.")

            # Take success screenshot
            await page.screenshot(path="test_success.png")
            print("  Screenshot saved: test_success.png")

            print("\n  DRY RUN COMPLETE — NOT clicking Post (this is a test).")
            print("  Close the browser window manually or press Ctrl+C.\n")

            # Press Escape to close modal without posting
            await asyncio.sleep(2)
            await page.keyboard.press("Escape")
            await asyncio.sleep(2)
            await context.close()

    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback; traceback.print_exc()
    finally:
        shutil.rmtree(tmp_profile, ignore_errors=True)
        print("  Temp profile cleaned up.")

    return results


async def main():
    print("\n" + "=" * 60)
    print("  LinkedIn Browser Test — Pure Playwright Dry Run")
    print("=" * 60)

    results = await test_browser_open()

    print("\n" + "=" * 60)
    print("  TEST RESULTS")
    print("=" * 60)
    all_pass = True
    for step, passed in results.items():
        status = "PASS" if passed else "FAIL"
        icon = "OK" if passed else "!!"
        print(f"  [{icon}] {status}  {step.replace('_', ' ').title()}")
        if not passed:
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("  ALL STEPS PASSED — Browser automation is working correctly.")
        print("  You can now safely run: python -X utf8 linkedin_original_post.py")
    else:
        print("  SOME STEPS FAILED — Check output above and screenshots.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
