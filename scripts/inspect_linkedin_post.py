"""
scripts/inspect_linkedin_post.py
Navigates to a specific LinkedIn update/activity URL, extracts the post content, author,
reactions, comments, and saves a screenshot.
Usage: python -X utf8 scripts/inspect_linkedin_post.py <post_url>
"""

import asyncio
import json
import sys
import shutil
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROME_PROFILE = REPO_ROOT / "data-tracking" / "chrome-profile"
DATA_TRACKING = REPO_ROOT / "data-tracking"

async def inspect_post(url: str):
    print(f"\n[1/4] Preparing inspection for: {url}")
    tmp_profile = tempfile.mkdtemp(prefix="li-post-")
    
    # Fast copy of profile
    def robust_copy(src, dst):
        s_p, d_p = Path(src), Path(dst)
        d_p.mkdir(parents=True, exist_ok=True)
        for item in s_p.iterdir():
            d = d_p / item.name
            if item.is_dir():
                robust_copy(item, d)
            else:
                try: shutil.copy2(item, d)
                except: pass

    robust_copy(CHROME_PROFILE, tmp_profile)
    print("  Profile copied to temp.")

    post_data = {
        "url": url,
        "author": {},
        "text": "",
        "timestamp": "",
        "reactions": "",
        "comments_count": "",
        "comments": []
    }

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            tmp_profile,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ],
            ignore_https_errors=True,
            no_viewport=True,
        )

        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        print(f"[2/4] Navigating to target post...")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"  Warning: {e}")
        await asyncio.sleep(6)

        current_url = page.url
        print(f"  Loaded URL: {current_url}")

        # Expand "see more" on post
        try:
            see_more_btns = await page.query_selector_all("button.inline-show-more-text__button, button[aria-label*='see more']")
            for b in see_more_btns:
                await b.click()
                await asyncio.sleep(0.5)
        except:
            pass

        # Capture screenshot
        urn_id = url.rstrip("/").split(":")[-1]
        screenshot_path = DATA_TRACKING / f"post_activity_{urn_id}.png"
        print(f"[3/4] Capturing screenshot: {screenshot_path}")
        await page.screenshot(path=str(screenshot_path))

        # Deep Extraction
        print("[4/4] Extracting post details...")
        extracted = await page.evaluate("""() => {
            const data = {
                author_name: '',
                author_headline: '',
                author_url: '',
                post_text: '',
                time: '',
                reactions: '',
                comments_count: '',
                recent_comments: []
            };

            // Author
            const authorEl = document.querySelector('.update-components-actor__name span, .feed-shared-actor__name span, a[data-field="actor_name"]');
            if (authorEl) data.author_name = authorEl.innerText.trim();

            const headlineEl = document.querySelector('.update-components-actor__description, .feed-shared-actor__description');
            if (headlineEl) data.author_headline = headlineEl.innerText.trim();

            const authorLink = document.querySelector('a.update-components-actor__image, a[data-field="actor_name"]');
            if (authorLink) data.author_url = authorLink.href;

            // Timestamp
            const timeEl = document.querySelector('.update-components-actor__sub-description span, time');
            if (timeEl) data.time = timeEl.innerText.trim();

            // Text
            const textEl = document.querySelector('.update-components-text, .feed-shared-update-v2__description, div.feed-shared-text');
            if (textEl) data.post_text = textEl.innerText.trim();

            // Reactions & comments
            const reactEl = document.querySelector('.social-details-social-counts__reactions-count, .reactions-count');
            if (reactEl) data.reactions = reactEl.innerText.trim();

            const commEl = document.querySelector('button[aria-label*="comment"] span, .comments-count');
            if (commEl) data.comments_count = commEl.innerText.trim();

            // Comments
            const commentItems = document.querySelectorAll('.comments-comments-list__comment-item, article.comments-comment-item');
            commentItems.forEach((ci, idx) => {
                if (idx < 5) {
                    const cAuthor = ci.querySelector('.comments-post-meta__name-text, .comments-comment-meta__name');
                    const cText = ci.querySelector('.comments-comment-item__main-content, .feed-shared-main-content');
                    if (cText) {
                        data.recent_comments.push({
                            author: cAuthor ? cAuthor.innerText.trim() : 'Unknown',
                            text: cText.innerText.trim()
                        });
                    }
                }
            });

            return data;
        }""")

        post_data.update(extracted)
        post_data["screenshot"] = str(screenshot_path)

        out_json_path = DATA_TRACKING / f"post_activity_{urn_id}.json"
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("POST EXTRACTION REPORT")
        print("=" * 60)
        print(f"Author:     {post_data.get('author_name')}")
        print(f"Headline:   {post_data.get('author_headline')}")
        print(f"Posted:     {post_data.get('time')}")
        print(f"Reactions:  {post_data.get('reactions')}")
        print(f"Comments:   {post_data.get('comments_count')}")
        print(f"Text:       {post_data.get('post_text')[:250]}...")
        print("=" * 60)

        await asyncio.sleep(2)
        await context.close()

    shutil.rmtree(tmp_profile, ignore_errors=True)
    return post_data

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.linkedin.com/feed/update/urn:li:activity:7526519292465610753/"
    asyncio.run(inspect_post(url))

