"""
linkedin_post_now.py
====================
Post a drafted LinkedIn post NOW using pure Playwright + saved Chrome profile.
No browser-use. No Ollama. No LLM needed for browser automation.

Edit POST_TEXT and IMAGE_PATH below then run:
  python -X utf8 linkedin_post_now.py
"""

import asyncio
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_PROFILE = Path("data-tracking/chrome-profile").resolve()

# ── Edit these before running ──────────────────────────────────────────────
POST_TEXT = """It was supposed to be a 5-minute fix. 😅

#StudentFounders #BuildInPublic #DevHumor"""

IMAGE_PATH = "c:\\Users\\2005g\\Downloads\\tappits-linkedin-agents\\memory\\post_images\\2026-07-07_dev_bugfix_meme.png"
# ──────────────────────────────────────────────────────────────────────────


def copy_image_to_clipboard(image_path: str) -> bool:
    """Copy image file to Windows clipboard via PowerShell."""
    ps = image_path.replace("\\", "\\\\")
    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        f"$img = [System.Drawing.Image]::FromFile('{ps}'); "
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


def robust_copy_tree(src: Path, dst: str):
    import os
    src = Path(src)
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for item in os.listdir(src):
        s = src / item
        d = dst / item
        if s.is_dir():
            try:
                robust_copy_tree(s, str(d))
            except Exception:
                pass
        else:
            try:
                shutil.copy2(str(s), str(d))
            except Exception:
                pass


async def post_to_linkedin(post_text: str, image_path: str = "") -> bool:
    """
    Pure Playwright posting — no browser-use, no LLM.
    Copies Chrome profile to temp dir (avoids lock), launches system Chrome,
    pastes image from clipboard, types post character-by-character, clicks Post.
    """
    from playwright.async_api import async_playwright

    # Copy profile to temp to avoid lock conflicts
    tmp_profile = tempfile.mkdtemp(prefix="li-post-")
    print(f"\n  Copying Chrome profile to temp: {tmp_profile}")
    robust_copy_tree(CHROME_PROFILE, tmp_profile)
    print("  Profile copied.\n")

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

            # ── [1] Navigate to LinkedIn feed ───────────────────────────
            print("  [1/6] Navigating to LinkedIn feed...")
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)

            if "login" in page.url or "authwall" in page.url:
                print("  ERROR: Session expired. Re-login required.")
                await context.close()
                return False
            print(f"  Feed loaded: {page.url}")

            # Scroll to top to expose the composer box
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(2)

            # ── [2] Click 'Start a post' ────────────────────────────────
            print("\n  [2/6] Clicking 'Start a post'...")
            clicked = False
            for sel in [
                "button.share-box-feed-entry__trigger",
                "button[class*='share-box-feed-entry__trigger']",
                ".share-box-feed-entry__trigger",
                "button:has-text('Start a post')",
                "div.share-box-feed-entry__top-bar button",
                "div[class*='share-box-feed-entry'] button:first-child",
                "[placeholder='Start a post']",
            ]:
                try:
                    el = await page.wait_for_selector(sel, timeout=4000)
                    if el:
                        await el.click()
                        clicked = True
                        print(f"  'Start a post' clicked.")
                        break
                except Exception:
                    continue

            if not clicked:
                # JS fallback — find by visible text
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
                    print("  'Start a post' clicked via JS fallback.")

            if not clicked:
                print("  WARNING: Could not find 'Start a post' — check page manually.")
            await asyncio.sleep(2)

            # ── [3] Paste image from clipboard ──────────────────────────
            if image_path and Path(image_path).exists():
                print("\n  [3/6] Pasting image from clipboard (Ctrl+V)...")
                await page.keyboard.press("Control+v")
                await asyncio.sleep(5)
                print("  Image paste sent.")
            else:
                print("\n  [3/6] No image path set — skipping image paste.")

            # ── [4] Find text editor ────────────────────────────────────
            print("\n  [4/6] Locating post text area...")
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
                        print(f"  Text area found.")
                        break
                except Exception:
                    continue

            if not text_area:
                print("  ERROR: Text area not found.")
                await context.close()
                return False

            await text_area.click()
            await asyncio.sleep(0.5)

            # ── [5] Type post text ──────────────────────────────────────
            print(f"\n  [5/6] Typing {len(post_text)} characters (human speed)...")
            for char in post_text:
                if char == "\n":
                    await page.keyboard.press("Enter")
                else:
                    await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.04, 0.09))

            await asyncio.sleep(2)
            print("  Text typed.")

            # ── [6] Click Post button ───────────────────────────────────
            print("\n  [6/6] Clicking Post button...")
            post_btn = None
            for sel in [
                "button.share-actions__primary-action",
                "button[class*='share-actions__primary-action']",
                "button.artdeco-button--primary:has-text('Post')",
                "button:has-text('Post')",
                "button[aria-label='Post']",
            ]:
                try:
                    btn = await page.wait_for_selector(sel, timeout=5000)
                    if btn:
                        disabled = await btn.get_attribute("disabled")
                        if disabled:
                            print("  Post button is disabled — waiting 3s for content to load...")
                            await asyncio.sleep(3)
                        await btn.click()
                        post_btn = sel
                        print(f"  Post button clicked!")
                        break
                except Exception:
                    continue

            if not post_btn:
                print("  ERROR: Could not click Post button.")
                await context.close()
                return False

            # ── Confirm success ─────────────────────────────────────────
            await asyncio.sleep(6)
            modal_gone = True
            try:
                modal = await page.query_selector("div.share-creation-state")
                if modal:
                    modal_gone = not await modal.is_visible()
            except Exception:
                modal_gone = True

            if modal_gone:
                print("\n  Post modal closed — POST SUBMITTED SUCCESSFULLY.")
                success = True
            else:
                print("\n  WARNING: Modal still visible. Post may not have gone through.")
                success = False

            await asyncio.sleep(3)
            await context.close()

    except Exception as e:
        print(f"\n  ERROR: {e}")
        import traceback; traceback.print_exc()
        success = False
    finally:
        shutil.rmtree(tmp_profile, ignore_errors=True)
        print("  Temp profile cleaned up.")

    return success


async def main():
    print("\n" + "=" * 60)
    print("  LinkedIn Post Publisher — Pure Playwright")
    print("=" * 60)

    # Copy image to clipboard FIRST (before browser opens)
    if IMAGE_PATH and Path(IMAGE_PATH).exists():
        print("\nCopying image to clipboard...")
        ok = copy_image_to_clipboard(IMAGE_PATH)
        if not ok:
            print("WARNING: Clipboard copy may have failed. Continuing anyway.")
        await asyncio.sleep(2)
    else:
        print(f"\nNo image found at: {IMAGE_PATH}")
        print("Proceeding as text-only post.\n")

    result = await post_to_linkedin(POST_TEXT, IMAGE_PATH)

    print("\n" + "=" * 60)
    if result:
        print("  SUCCESS — Post published to LinkedIn!")
    else:
        print("  FAILED — Check output above for details.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
