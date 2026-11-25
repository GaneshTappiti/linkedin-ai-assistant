"""
Scrape any LinkedIn profile's posts for content analysis.
Uses persistent Chrome profile so LinkedIn session is authenticated.
Usage: python -X utf8 scripts/scrape_linkedin_profile.py <profile_url> [output_file]
"""
import asyncio
import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
CHROME_PROFILE = (REPO_ROOT / "data-tracking" / "chrome-profile").resolve()


async def scrape_profile(profile_url: str, output_file: str):
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
            channel="chrome",
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

        posts_url = profile_url.rstrip("/") + "/recent-activity/all/"
        print(f"Navigating directly to posts page: {posts_url}...")
        await page.goto(posts_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        current_url = page.url
        current_title = await page.title()
        print(f"Current URL: {current_url}")
        print(f"Current Title: {current_title}")

        # Check for auth issues
        if "login" in current_url or "authwall" in current_url or "Sign Up" in current_title:
            print("\n⚠️  SESSION EXPIRED — LinkedIn is asking you to log in.")
            print("Run: python scripts/login_linkedin.py")
            print("Then re-run this script.")
            await page.screenshot(path=str(REPO_ROOT / "debug_scrape_activity.png"))
            await context.close()
            shutil.rmtree(tmp_profile, ignore_errors=True)
            return

        # Check for rate limit / challenge
        if "challenge" in current_url or "Rate Limited" in current_title:
            print("WARNING: Cloudflare challenge or Rate Limit detected! Waiting 15 seconds...")
            await asyncio.sleep(15)
            await page.reload(wait_until="domcontentloaded")
            await asyncio.sleep(5)
            print(f"After refresh - URL: {page.url}, Title: {await page.title()}")

        await page.screenshot(path=str(REPO_ROOT / "debug_scrape_activity.png"))
        print(f"Saved debug screenshot to debug_scrape_activity.png")

        # Scroll to load posts
        print("Scrolling to load posts...")
        for i in range(12):
            await page.evaluate("window.scrollBy(0, 1200)")
            await asyncio.sleep(2.5)
            print(f"  Scroll {i+1}/12...")

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
                                index: idx, text: text.substring(0, 800),
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
                const followersEl = document.querySelector('.t-bold');
                const followers = followersEl ? followersEl.innerText.trim() : '';
                return { name, headline, followers };
            }
        """)

        print(f"\nProfile: {profile_info}")
        print(f"Found {len(posts_data)} posts")

        result = {"profile_url": profile_url, "profile": profile_info, "posts_count": len(posts_data), "posts": posts_data}
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved to {output_file}")

        for i, post in enumerate(posts_data[:20]):
            print(f"\n--- Post {i+1} ({post['format']}) ---")
            print(f"Reactions: {post['reactions']} | Comments: {post['comments']} | Time: {post['timestamp']}")
            print(f"Text: {post['text'][:300]}...")

        await context.close()
        shutil.rmtree(tmp_profile, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -X utf8 scripts/scrape_linkedin_profile.py <profile_url> [output_file]")
        sys.exit(1)
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else str(REPO_ROOT / "memory" / "scraped_profile_posts.json")
    asyncio.run(scrape_profile(url, out))
