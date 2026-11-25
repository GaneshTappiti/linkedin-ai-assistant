"""
check_linkedin_posts.py
========================
Pure Playwright - NO Ollama, NO LLM, NO browser-use.
Uses the existing saved Chrome profile (already logged into LinkedIn).

Run: python -X utf8 check_linkedin_posts.py
"""

import asyncio
import sys
import shutil
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

CHROME_PROFILE = Path("data-tracking/chrome-profile").resolve()
PROFILE_URL    = "https://www.linkedin.com/in/ganeshtappiti/recent-activity/all/"
SCREENSHOT     = Path("linkedin_check_screenshot.png").resolve()


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


async def main():
    print("\n=== LinkedIn Post Checker (Pure Playwright, Saved Profile) ===")
    print(f"Using profile: {CHROME_PROFILE}")
    print("=" * 60 + "\n")

    # Copy profile to temp dir to avoid lock conflicts
    tmp_profile = tempfile.mkdtemp(prefix="li-check-")
    print(f"Copying profile to temp: {tmp_profile}")
    robust_copy_tree(CHROME_PROFILE, tmp_profile)
    print("Profile copied.\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=tmp_profile,
            headless=False,
            channel="chrome",           # Use system Chrome (not Playwright's Chromium)
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

        # ── Navigate directly (already logged in via saved profile) ──
        try:
            await page.goto(PROFILE_URL, wait_until="commit", timeout=60000)
        except Exception as e:
            print(f"  Navigation warning: {e}")
        await asyncio.sleep(8)

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "login" in current_url or "authwall" in current_url:
            print("  Session expired - profile cookies may be stale.")
            await page.screenshot(path=str(SCREENSHOT))
            print(f"  Screenshot: {SCREENSHOT}")
            await context.close()
            return

        print("  Logged in via saved profile.\n")

        # ── Scroll to load posts ──────────────────────────────────────
        print("[2/3] Scrolling to load posts...")
        for _ in range(5):
            await page.keyboard.press("End")
            await asyncio.sleep(1.5)

        # ── Extract posts ─────────────────────────────────────────────
        print("[3/3] Extracting posts...\n")

        SELECTORS = [
            "div.feed-shared-update-v2",
            "div[data-urn*='activity']",
            "li.profile-creator-shared-feed-update__container",
            "div.occludable-update",
        ]

        containers = []
        for sel in SELECTORS:
            containers = await page.query_selector_all(sel)
            if containers:
                print(f"  Found {len(containers)} posts (selector: {sel})\n")
                break

        if not containers:
            print("  No posts found with standard selectors.")
            await page.screenshot(path=str(SCREENSHOT), full_page=False)
            print(f"  Screenshot saved for manual check: {SCREENSHOT}")
            await context.close()
            return

        posts = []
        for i, container in enumerate(containers[:6]):
            try:
                # Text
                text = ""
                for sel in [
                    "div.feed-shared-update-v2__description",
                    "div[class*='commentary'] span[dir]",
                    "span.break-words",
                    "span[dir='ltr']",
                ]:
                    el = await container.query_selector(sel)
                    if el:
                        t = (await el.inner_text()).strip()
                        if len(t) > 20:
                            text = t
                            break

                # Timestamp
                ts = "unknown"
                for sel in [
                    "span.feed-shared-actor__sub-description span:not(.visually-hidden)",
                    "time",
                    "a[class*='app-aware-link'] span span",
                ]:
                    el = await container.query_selector(sel)
                    if el:
                        t = (await el.inner_text()).strip()
                        if t and len(t) < 40:
                            ts = t
                            break

                # Reactions
                reactions = "unknown"
                for sel in [
                    "span.social-counts-reactions__count-value",
                    "span[class*='reactions__count']",
                ]:
                    el = await container.query_selector(sel)
                    if el:
                        r = (await el.inner_text()).strip()
                        if r:
                            reactions = r
                            break

                if text and len(text) > 15:
                    posts.append({
                        "n": i + 1,
                        "hook": text[:200].replace("\n", " | "),
                        "ts": ts,
                        "reactions": reactions,
                        "key": text[:70].lower().strip(),
                    })

            except Exception as e:
                print(f"  Error on container {i+1}: {e}")

        # ── Screenshot ─────────────────────────────────────────────────
        await page.screenshot(path=str(SCREENSHOT), full_page=False)

        # ── Report ─────────────────────────────────────────────────────
        print("=" * 60)
        print("RECENT POSTS")
        print("=" * 60)

        if not posts:
            print("\n  No post text extracted — see screenshot for manual check.")
        else:
            for post in posts:
                try:
                    # Clean hook text of non-ascii characters for display safety
                    safe_hook = post['hook'].encode('ascii', errors='replace').decode('ascii')
                    print(f"\nPOST {post['n']}:")
                    print(f"  Hook:      {safe_hook}")
                    print(f"  Posted:    {post['ts']}")
                    print(f"  Reactions: {post['reactions']}")
                except Exception as e:
                    print(f"\nPOST {post['n']}: (Error printing details: {e})")

            print("\n" + "=" * 60)
            print("DUPLICATE CHECK")
            print("=" * 60)
            dupes = []
            for i in range(len(posts)):
                for j in range(i + 1, len(posts)):
                    a = posts[i]["key"]
                    b = posts[j]["key"]
                    if len(a) > 20 and a[:50] == b[:50]:
                        dupes.append((posts[i]["n"], posts[j]["n"], a[:60]))
            if dupes:
                for d in dupes:
                    safe_match = d[2].encode('ascii', errors='replace').decode('ascii')
                    print(f"\n  [!!] DUPLICATE: Post {d[0]} and Post {d[1]}")
                    print(f"       Matching: \"{safe_match}...\"")
            else:
                print("\n  No duplicates detected in first 6 posts.")

        print(f"\n  Screenshot: {SCREENSHOT}\n")
        await asyncio.sleep(2)
        await context.close()

    # Cleanup temp profile copy
    shutil.rmtree(tmp_profile, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
