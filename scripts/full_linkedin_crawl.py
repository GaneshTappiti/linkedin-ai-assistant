"""
scripts/full_linkedin_crawl.py
================================
Full LinkedIn crawl using Playwright + saved Chrome profile.
Inspects: feed posts, profile details, notifications, engagement stats.
"""

import asyncio
import json
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROME_PROFILE = REPO_ROOT / "data-tracking" / "chrome-profile"
OUTPUT_DIR = REPO_ROOT / "data-tracking"
SCREENSHOT_FEED = OUTPUT_DIR / "crawl_feed.png"
SCREENSHOT_PROFILE = OUTPUT_DIR / "crawl_profile.png"
SCREENSHOT_NOTIFS = OUTPUT_DIR / "crawl_notifications.png"
CRAWL_REPORT = OUTPUT_DIR / "crawl_report.json"


def robust_copy_tree(src: Path, dst: str):
    import os
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for item in os.listdir(src):
        s, d = src / item, dst / item
        if s.is_dir():
            try: robust_copy_tree(s, str(d))
            except: pass
        else:
            try: shutil.copy2(str(s), str(d))
            except: pass


async def main():
    report = {
        "crawl_timestamp": datetime.now().isoformat(),
        "status": "started",
        "identity": {},
        "sidebar_stats": {},
        "feed_posts": [],
        "profile": {},
        "notifications": {},
    }

    print("\n" + "=" * 70)
    print("FULL LINKEDIN CRAWL — Playwright + Saved Profile")
    print("=" * 70)

    # Copy profile to avoid lock conflicts
    tmp_profile = tempfile.mkdtemp(prefix="li-crawl-")
    print(f"\n[1/7] Copying profile to temp: {tmp_profile}")
    robust_copy_tree(CHROME_PROFILE, tmp_profile)
    print("  Profile copied.\n")

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
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        # ── STEP 2: Navigate to Feed ──────────────────────────────────
        print("[2/7] Navigating to LinkedIn feed...")
        try:
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"  Navigation warning: {e}")
        await asyncio.sleep(8)

        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "login" in current_url or "authwall" in current_url:
            print("\n[!] NOT LOGGED IN — session expired.")
            report["status"] = "authwall"
            await page.screenshot(path=str(SCREENSHOT_FEED))
            await context.close()
            shutil.rmtree(tmp_profile, ignore_errors=True)
            with open(CRAWL_REPORT, "w") as f:
                json.dump(report, f, indent=2)
            return report

        print("  ✓ Logged in successfully!\n")
        report["status"] = "authenticated"

        # ── STEP 3: Extract Sidebar Identity ──────────────────────────
        print("[3/7] Reading sidebar identity & stats...")
        try:
            # Name
            for sel in [".feed-identity-module__actor-meta a", "div.feed-identity-module a[href*='/in/']"]:
                el = await page.query_selector(sel)
                if el:
                    report["identity"]["name"] = (await el.inner_text()).strip()
                    break

            # Headline
            for sel in [".feed-identity-module__headline", ".feed-identity-module__member-headline"]:
                el = await page.query_selector(sel)
                if el:
                    report["identity"]["headline"] = (await el.inner_text()).strip()
                    break

            # Profile viewers
            for sel in ["a[href*='profile-views'] span", "a[href*='who-viewed'] span"]:
                el = await page.query_selector(sel)
                if el:
                    report["sidebar_stats"]["profile_viewers"] = (await el.inner_text()).strip()
                    break

            # Post impressions
            for sel in ["a[href*='post-impressions'] span", "a[href*='creator-analytics'] span"]:
                el = await page.query_selector(sel)
                if el:
                    report["sidebar_stats"]["post_impressions"] = (await el.inner_text()).strip()
                    break
        except Exception as e:
            print(f"  Sidebar extraction warning: {e}")

        print(f"  Identity: {report['identity']}")
        print(f"  Stats: {report['sidebar_stats']}")

        # ── STEP 4: Scroll & Extract Feed Posts ───────────────────────
        print("\n[4/7] Scrolling feed & extracting posts...")
        for _ in range(6):
            await page.keyboard.press("End")
            await asyncio.sleep(1.5)

        # Go back to top
        await page.keyboard.press("Home")
        await asyncio.sleep(2)

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
                print(f"  Found {len(containers)} posts (selector: {sel})")
                break

        for i, container in enumerate(containers[:10]):
            post = {"index": i + 1}
            try:
                # Author
                for sel in [".update-components-actor__name span", ".feed-shared-actor__name span"]:
                    el = await container.query_selector(sel)
                    if el:
                        post["author"] = (await el.inner_text()).strip().split("\n")[0]
                        break

                # Author headline
                for sel in [".update-components-actor__description", ".feed-shared-actor__description"]:
                    el = await container.query_selector(sel)
                    if el:
                        post["author_headline"] = (await el.inner_text()).strip()[:100]
                        break

                # Timestamp
                for sel in ["span.update-components-actor__sub-description span:not(.visually-hidden)", "time", "span.feed-shared-actor__sub-description span"]:
                    el = await container.query_selector(sel)
                    if el:
                        t = (await el.inner_text()).strip()
                        if t and len(t) < 40:
                            post["time"] = t
                            break

                # Post text
                for sel in [".update-components-text span[dir]", "div.feed-shared-update-v2__description span[dir]", "span.break-words span[dir='ltr']", "span[dir='ltr']"]:
                    el = await container.query_selector(sel)
                    if el:
                        txt = (await el.inner_text()).strip()
                        if len(txt) > 20:
                            post["text_snippet"] = txt[:300]
                            break

                # Reactions count
                for sel in ["span.social-details-social-counts__reactions-count", "span[class*='reactions-count']"]:
                    el = await container.query_selector(sel)
                    if el:
                        post["reactions"] = (await el.inner_text()).strip()
                        break

                # Comments count
                for sel in ["button[aria-label*='comment'] span", "span[class*='comments-count']"]:
                    el = await container.query_selector(sel)
                    if el:
                        post["comments"] = (await el.inner_text()).strip()
                        break

                if "author" in post or "text_snippet" in post:
                    report["feed_posts"].append(post)

            except Exception as e:
                continue

        print(f"  Extracted {len(report['feed_posts'])} posts with content.")

        # Save feed screenshot
        await page.screenshot(path=str(SCREENSHOT_FEED))
        print(f"  Feed screenshot: {SCREENSHOT_FEED}")

        # ── STEP 5: Check Notifications ───────────────────────────────
        print("\n[5/7] Checking notifications...")
        try:
            notif_badge = await page.query_selector(".notification-badge__count, #nav-notifications-badge-count, span.notification-badge")
            if notif_badge:
                report["notifications"]["unread_count"] = (await notif_badge.inner_text()).strip()
                print(f"  Unread notifications: {report['notifications']['unread_count']}")

            # Click notifications
            notif_link = await page.query_selector("a[href*='notifications'], #ember-notifications")
            if notif_link:
                await notif_link.click()
                await asyncio.sleep(5)

                notif_items = await page.query_selector_all(".nt-card, .notification-card, div[data-urn*='notification']")
                notif_list = []
                for ni in notif_items[:8]:
                    try:
                        txt = (await ni.inner_text()).strip()
                        if txt and len(txt) > 10:
                            notif_list.append(txt[:200].replace("\n", " | "))
                    except:
                        pass
                report["notifications"]["recent"] = notif_list
                print(f"  Captured {len(notif_list)} recent notifications.")

                await page.screenshot(path=str(SCREENSHOT_NOTIFS))
                print(f"  Notifications screenshot: {SCREENSHOT_NOTIFS}")
        except Exception as e:
            print(f"  Notifications extraction warning: {e}")

        # ── STEP 6: Visit Own Profile ─────────────────────────────────
        print("\n[6/7] Visiting own profile...")
        try:
            await page.goto("https://www.linkedin.com/in/ganeshtappiti/", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(6)

            # Name
            for sel in ["h1.text-heading-xlarge", "h1[class*='break-words']"]:
                el = await page.query_selector(sel)
                if el:
                    report["profile"]["name"] = (await el.inner_text()).strip()
                    break

            # Headline
            for sel in ["div.text-body-medium.break-words", ".pv-text-details__left-panel div.text-body-medium"]:
                el = await page.query_selector(sel)
                if el:
                    report["profile"]["headline"] = (await el.inner_text()).strip()
                    break

            # Location
            for sel in ["span.text-body-small.inline", ".pv-text-details__left-panel span.text-body-small"]:
                el = await page.query_selector(sel)
                if el:
                    report["profile"]["location"] = (await el.inner_text()).strip()
                    break

            # Followers / connections
            for sel in ["li.text-body-small span.t-bold", "span[class*='t-bold']"]:
                els = await page.query_selector_all(sel)
                counts = []
                for el in els[:3]:
                    t = (await el.inner_text()).strip()
                    if t:
                        counts.append(t)
                if counts:
                    report["profile"]["network_counts"] = counts

            # About section
            for sel in ["div#about ~ div.display-flex div span[aria-hidden='true']", "section#about div span[aria-hidden='true']"]:
                el = await page.query_selector(sel)
                if el:
                    report["profile"]["about"] = (await el.inner_text()).strip()[:500]
                    break

            await page.screenshot(path=str(SCREENSHOT_PROFILE))
            print(f"  Profile screenshot: {SCREENSHOT_PROFILE}")

        except Exception as e:
            print(f"  Profile visit warning: {e}")

        print(f"  Profile data: {report['profile']}")

        # ── STEP 7: Save Report ───────────────────────────────────────
        print("\n[7/7] Saving crawl report...")
        with open(CRAWL_REPORT, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Report saved: {CRAWL_REPORT}")

        # ── Summary ──────────────────────────────────────────────────
        print("\n" + "=" * 70)
        print("CRAWL COMPLETE — SUMMARY")
        print("=" * 70)
        print(f"  Status:          {report['status']}")
        print(f"  Identity:        {report['identity'].get('name', 'N/A')}")
        print(f"  Headline:        {report['identity'].get('headline', 'N/A')}")
        print(f"  Profile Viewers: {report['sidebar_stats'].get('profile_viewers', 'N/A')}")
        print(f"  Impressions:     {report['sidebar_stats'].get('post_impressions', 'N/A')}")
        print(f"  Feed Posts:      {len(report['feed_posts'])}")
        print(f"  Notifications:   {report['notifications'].get('unread_count', 'N/A')}")
        print(f"  Profile Name:    {report['profile'].get('name', 'N/A')}")
        print(f"  Profile HL:      {report['profile'].get('headline', 'N/A')}")
        print("=" * 70)

        for i, post in enumerate(report["feed_posts"][:5]):
            safe_author = post.get('author', 'Unknown')
            safe_snip = post.get('text_snippet', '(no text)')[:100]
            try:
                safe_author = safe_author.encode('ascii', errors='replace').decode('ascii')
                safe_snip = safe_snip.encode('ascii', errors='replace').decode('ascii')
            except: pass
            print(f"\n  POST {i+1}: [{safe_author}] ({post.get('time','?')})")
            print(f"    {safe_snip}...")
            print(f"    Reactions: {post.get('reactions','?')} | Comments: {post.get('comments','?')}")

        await asyncio.sleep(3)
        await context.close()

    shutil.rmtree(tmp_profile, ignore_errors=True)
    print("\n  Temp profile cleaned up. Done!\n")
    return report


if __name__ == "__main__":
    from playwright.async_api import async_playwright
    asyncio.run(main())

