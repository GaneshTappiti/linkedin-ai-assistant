"""
scripts/inspect_feed.py
Directly inspects the LinkedIn feed using the saved persistent Chrome profile in data-tracking/chrome-profile.
Captures the feed state, extracts top posts, and saves a screenshot.
"""

import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROME_PROFILE = REPO_ROOT / "data-tracking" / "chrome-profile"
SCREENSHOT_PATH = REPO_ROOT / "data-tracking" / "linkedin_feed_screenshot.png"
FEED_URL = "https://www.linkedin.com/feed/"

async def inspect():
    print(f"\n[1/5] Initializing Chrome with profile: {CHROME_PROFILE}")
    
    async with async_playwright() as p:
        try:
            # We can use system chrome or chromium with the saved profile
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(CHROME_PROFILE),
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
        except Exception as e:
            print(f"[!] Failed to launch with channel='chrome': {e}")
            print("Retrying with bundled chromium...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(CHROME_PROFILE),
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--start-maximized",
                ],
                ignore_https_errors=True,
                no_viewport=True,
            )

        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        print(f"[2/5] Navigating to {FEED_URL}...")
        try:
            await page.goto(FEED_URL, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"  Warning on navigation: {e}")

        print("[3/5] Waiting for feed hydration (8 seconds)...")
        await asyncio.sleep(8)

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "login" in current_url or "authwall" in current_url:
            print("\n[!] SESSION NOT LOGGED IN / AUTHWALL DETECTED.")
            await page.screenshot(path=str(SCREENSHOT_PATH))
            print(f"Screenshot saved to: {SCREENSHOT_PATH}")
            await asyncio.sleep(3)
            await context.close()
            return {"status": "authwall", "url": current_url}

        print("\n[+] Successfully authenticated and loaded LinkedIn Feed!")

        # Check navigation / profile identity
        identity = {}
        try:
            name_el = await page.query_selector(".feed-identity-module__actor-meta a, .profile-rail-card__actor-link")
            if name_el:
                identity["name"] = (await name_el.inner_text()).strip()
        except Exception:
            pass

        # Scroll slightly to trigger feed item rendering
        print("[4/5] Scrolling feed...")
        await page.mouse.wheel(0, 800)
        await asyncio.sleep(3)

        # Extract top feed items
        feed_posts = []
        post_elements = await page.query_selector_all("div.feed-shared-update-v2, div[data-urn*='activity']")
        print(f"  Detected {len(post_elements)} posts in viewport.")

        for idx, el in enumerate(post_elements[:6]):
            post_data = {"index": idx + 1}
            try:
                # Author
                actor_el = await el.query_selector(".update-components-actor__name, .feed-shared-actor__name")
                if actor_el:
                    post_data["author"] = (await actor_el.inner_text()).strip().split("\n")[0]

                # Author sub-description / title
                sub_el = await el.query_selector(".update-components-actor__description, .feed-shared-actor__description")
                if sub_el:
                    post_data["author_headline"] = (await sub_el.inner_text()).strip()

                # Post text content
                text_el = await el.query_selector(".feed-shared-update-v2__description, .update-components-text")
                if text_el:
                    full_text = (await text_el.inner_text()).strip()
                    post_data["snippet"] = full_text[:280].replace("\n", " ")

                # Social counts
                reactions_el = await el.query_selector(".social-details-social-counts__reactions-count, .reactions-count")
                if reactions_el:
                    post_data["reactions"] = (await reactions_el.inner_text()).strip()

                if "author" in post_data or "snippet" in post_data:
                    feed_posts.append(post_data)
            except Exception as ex:
                continue

        # Save screenshot
        print(f"[5/5] Capturing screenshot: {SCREENSHOT_PATH}...")
        await page.screenshot(path=str(SCREENSHOT_PATH))
        print("  Screenshot captured successfully!")

        print("\n" + "=" * 60)
        print("LINKEDIN FEED SNAPSHOT SUMMARY")
        print("=" * 60)
        print(f"Account Profile: {identity.get('name', 'Active Session')}")
        print(f"Current URL: {current_url}")
        print(f"Posts Retrieved: {len(feed_posts)}")
        for p_item in feed_posts:
            author = p_item.get('author', 'Unknown')
            snip = p_item.get('snippet', '(no text)')[:120]
            print(f"- [{author}]: {snip}...")

        await asyncio.sleep(4)
        await context.close()
        return {"status": "success", "url": current_url, "posts": feed_posts}

if __name__ == "__main__":
    asyncio.run(inspect())

