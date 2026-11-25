"""
Scrape Vivek Shiva's LinkedIn profile posts for content analysis.
Uses persistent Chrome profile so LinkedIn session is authenticated.
"""
import asyncio
import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

PROFILE_URL = "https://www.linkedin.com/in/vivekshiva/"
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
CHROME_PROFILE = (REPO_ROOT / "data-tracking" / "chrome-profile").resolve()
OUTPUT_FILE = str(REPO_ROOT / "memory" / "vivek_shiva_posts_analysis.json")

async def scrape_profile():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && python -m playwright install chromium")
        sys.exit(1)

    print(f"Using profile source: {CHROME_PROFILE}")
    # Copy profile to temp dir to avoid lock conflicts
    tmp_profile = tempfile.mkdtemp(prefix="li-scrape-")
    print(f"Copying profile to temp: {tmp_profile}")
    shutil.copytree(str(CHROME_PROFILE), tmp_profile, dirs_exist_ok=True)
    print("Profile copied.\n")

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            tmp_profile,
            headless=False,
            channel="chrome",           # Use system Chrome (not Playwright's Chromium)
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--disable-default-apps",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--start-maximized",
                "--disable-infobars",
            ],
            ignore_https_errors=True,
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        posts_url = PROFILE_URL.rstrip("/") + "/recent-activity/all/"
        print(f"Navigating directly to posts page: {posts_url}...")
        await page.goto(posts_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        print(f"Current URL: {page.url}")
        print(f"Current Title: {await page.title()}")
        await page.screenshot(path=str(REPO_ROOT / "debug_scrape_activity.png"))
        print(f"Saved debug screenshot to debug_scrape_activity.png")

        if "challenge" in page.url or "Rate Limited" in await page.title():
            print("WARNING: Cloudflare challenge or Rate Limit detected! Let's wait 10 seconds and try to refresh...")
            await asyncio.sleep(10)
            await page.reload(wait_until="domcontentloaded")
            await asyncio.sleep(5)
            print(f"After refresh - URL: {page.url}, Title: {await page.title()}")
            await page.screenshot(path=str(REPO_ROOT / "debug_scrape_activity_after_refresh.png"))

        # Scroll to load posts
        print("Scrolling to load posts...")
        for i in range(10):
            await page.evaluate("window.scrollBy(0, 1200)")
            await asyncio.sleep(2.5)
            print(f"  Scroll {i+1}/10...")

        # Extract posts
        print("Extracting posts...")
        posts_data = await page.evaluate("""
            () => {
                const posts = [];
                const containers = document.querySelectorAll(
                    '.feed-shared-update-v2, .occludable-update, [data-urn*="activity"], .profile-creator-shared-feed-update__container'
                );
                containers.forEach((container, idx) => {
                    try {
                        const textEl = container.querySelector('.feed-shared-text, .break-words, .update-components-text');
                        const text = textEl ? textEl.innerText.trim() : '';
                        const reactionsEl = container.querySelector('.social-details-social-counts__reactions-count, .social-details-social-counts__count-value');
                        const reactions = reactionsEl ? reactionsEl.innerText.trim() : '0';
                        const commentsEl = container.querySelector('button[aria-label*="comment"]');
                        const comments = commentsEl ? commentsEl.innerText.trim() : '0';
                        const timeEl = container.querySelector('.feed-shared-actor__sub-description span, time, .update-components-actor__sub-description');
                        const timestamp = timeEl ? timeEl.innerText.trim() : '';
                        const hasImage = container.querySelector('img.feed-shared-image__image, .update-components-image') !== null;
                        const hasVideo = container.querySelector('video, .feed-shared-linkedin-video') !== null;
                        const hasDocument = container.querySelector('.feed-shared-document, .update-components-document') !== null;
                        if (text.length > 10) {
                            posts.push({
                                index: idx, text: text.substring(0, 600),
                                reactions, comments, timestamp,
                                hasImage, hasVideo, hasDocument,
                                format: hasDocument ? 'carousel' : hasVideo ? 'video' : hasImage ? 'image' : 'text-only'
                            });
                        }
                    } catch(e) {}
                });
                return posts;
            }
        """)

        profile_info = await page.evaluate("""
            () => {
                const name = document.querySelector('.text-heading-xlarge, h1')?.innerText?.trim() || '';
                const headline = document.querySelector('.text-body-medium')?.innerText?.trim() || '';
                return { name, headline };
            }
        """)

        print(f"\\nProfile: {profile_info}")
        print(f"Found {len(posts_data)} posts")

        result = {"profile": profile_info, "posts_count": len(posts_data), "posts": posts_data}
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved to {OUTPUT_FILE}")

        for i, post in enumerate(posts_data[:15]):
            print(f"\\n--- Post {i+1} ({post['format']}) ---")
            print(f"Reactions: {post['reactions']} | Comments: {post['comments']} | Time: {post['timestamp']}")
            print(f"Text: {post['text'][:250]}...")

        await context.close()
        shutil.rmtree(tmp_profile, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(scrape_profile())
