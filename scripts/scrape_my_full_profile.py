"""
scripts/scrape_my_full_profile.py
===================================
Comprehensive LinkedIn profile scraper using Playwright and saved Chrome profile.
Extracts: Intro, About, Experience, Education, Projects, Certifications, Skills, Analytics.
"""

import asyncio
import json
import os
import sys
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROME_PROFILE = REPO_ROOT / "data-tracking" / "chrome-profile"
DATA_TRACKING = REPO_ROOT / "data-tracking"
OUT_JSON = DATA_TRACKING / "scraped_full_profile.json"
PROFILE_URL = "https://www.linkedin.com/in/ganeshtappiti/"


def robust_copy_tree(src: Path, dst: str):
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
    print("\n" + "=" * 70)
    print("COMPREHENSIVE LINKEDIN PROFILE SCRAPER")
    print("=" * 70)

    tmp_profile = tempfile.mkdtemp(prefix="li-fullprof-")
    print(f"[1/6] Copying profile to temp: {tmp_profile}")
    robust_copy_tree(CHROME_PROFILE, tmp_profile)
    print("  Profile copied successfully.\n")

    profile_data = {
        "scraped_at": datetime.now().isoformat(),
        "profile_url": PROFILE_URL,
        "intro": {},
        "about": "",
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
        "skills": [],
        "analytics": {},
        "raw_sections": {}
    }

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            tmp_profile,
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

        print(f"[2/6] Navigating to {PROFILE_URL}...")
        try:
            await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"  Navigation warning: {e}")
        await asyncio.sleep(6)

        # Verify login
        if "login" in page.url or "authwall" in page.url:
            print("[!] Authwall detected. Exiting.")
            await context.close()
            shutil.rmtree(tmp_profile, ignore_errors=True)
            return

        print(f"  ✓ Connected at URL: {page.url}\n")

        # Scroll incrementally to bottom to load all lazy sections
        print("[3/6] Scrolling down full page to hydrate all sections...")
        for i in range(14):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1.2)

        # Scroll back to top
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(2)

        # Click all "see more" buttons to expand text
        print("[4/6] Expanding all 'see more' buttons...")
        try:
            await page.evaluate("""() => {
                const buttons = document.querySelectorAll('button.inline-show-more-text__button, button[aria-label*="see more"], button[aria-label*="See more"], .artdeco-button--tertiary');
                buttons.forEach(b => {
                    if (b.innerText && b.innerText.toLowerCase().includes('see more')) {
                        b.click();
                    }
                });
            }""")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"  Warning expanding buttons: {e}")

        # Capture multi-section screenshots for visual proof
        print("[5/6] Capturing high-resolution section screenshots...")
        await page.screenshot(path=str(DATA_TRACKING / "profile_section_top.png"))
        await page.evaluate("window.scrollBy(0, 900)")
        await asyncio.sleep(1)
        await page.screenshot(path=str(DATA_TRACKING / "profile_section_middle.png"))
        await page.evaluate("window.scrollBy(0, 900)")
        await asyncio.sleep(1)
        await page.screenshot(path=str(DATA_TRACKING / "profile_section_bottom.png"))

        # Deep Extraction via DOM Evaluation
        print("[6/6] Extracting structured data from all profile sections...")
        extracted = await page.evaluate("""() => {
            const result = {
                intro: {},
                about: '',
                analytics: {},
                experience: [],
                education: [],
                certifications: [],
                projects: [],
                skills: [],
                sections_found: []
            };

            // 1. INTRO CARD
            const nameEl = document.querySelector('h1');
            result.intro.name = nameEl ? nameEl.innerText.trim() : '';

            const headlineEl = document.querySelector('.text-body-medium.break-words');
            result.intro.headline = headlineEl ? headlineEl.innerText.trim() : '';

            const locEl = document.querySelector('span.text-body-small.inline');
            result.intro.location = locEl ? locEl.innerText.trim() : '';

            const followerEls = document.querySelectorAll('ul.pv-top-card--list-bullet li, li.text-body-small');
            const counts = [];
            followerEls.forEach(el => {
                const txt = el.innerText.trim();
                if (txt.includes('follower') || txt.includes('connection')) {
                    counts.push(txt);
                }
            });
            result.intro.network = counts;

            // 2. ABOUT SECTION
            const aboutSection = document.querySelector('#about, section[data-section="about"]');
            if (aboutSection) {
                const parentSection = aboutSection.closest('section');
                if (parentSection) {
                    const textEl = parentSection.querySelector('.inline-show-more-text, div.display-flex span[aria-hidden="true"]');
                    result.about = textEl ? textEl.innerText.trim() : parentSection.innerText.trim();
                }
            }
            if (!result.about) {
                // fallback about search
                const spans = document.querySelectorAll('section span');
                for (let span of spans) {
                    if (span.innerText && span.innerText.includes('I am Ganesh') || span.innerText.includes('product-first builder')) {
                        result.about = span.innerText.trim();
                        break;
                    }
                }
            }

            // 3. ANALYTICS
            const analyticsCard = document.querySelector('#analytics, section[data-section="analytics"]');
            if (analyticsCard) {
                const parent = analyticsCard.closest('section');
                if (parent) {
                    result.analytics.raw = parent.innerText.trim();
                }
            }

            // 4. SCAN ALL SECTIONS
            const allSections = document.querySelectorAll('section.artdeco-card');
            allSections.forEach(sec => {
                const headingEl = sec.querySelector('h2, span[aria-hidden="true"]');
                const heading = headingEl ? headingEl.innerText.trim().toLowerCase() : '';
                result.sections_found.push(heading);

                const fullText = sec.innerText.trim();

                // EXPERIENCE
                if (heading.includes('experience')) {
                    const listItems = sec.querySelectorAll('li.artdeco-list__item, li');
                    listItems.forEach(li => {
                        const liText = li.innerText.trim();
                        if (liText.length > 15) {
                            result.experience.push(liText);
                        }
                    });
                    if (result.experience.length === 0) {
                        result.experience.push(fullText);
                    }
                }

                // EDUCATION
                if (heading.includes('education')) {
                    const listItems = sec.querySelectorAll('li.artdeco-list__item, li');
                    listItems.forEach(li => {
                        const liText = li.innerText.trim();
                        if (liText.length > 15) {
                            result.education.push(liText);
                        }
                    });
                    if (result.education.length === 0) {
                        result.education.push(fullText);
                    }
                }

                // CERTIFICATIONS / LICENSES
                if (heading.includes('license') || heading.includes('certification')) {
                    const listItems = sec.querySelectorAll('li.artdeco-list__item, li');
                    listItems.forEach(li => {
                        const liText = li.innerText.trim();
                        if (liText.length > 15) {
                            result.certifications.push(liText);
                        }
                    });
                }

                // PROJECTS
                if (heading.includes('project')) {
                    const listItems = sec.querySelectorAll('li.artdeco-list__item, li');
                    listItems.forEach(li => {
                        const liText = li.innerText.trim();
                        if (liText.length > 15) {
                            result.projects.push(liText);
                        }
                    });
                }

                // SKILLS
                if (heading.includes('skill')) {
                    const listItems = sec.querySelectorAll('li.artdeco-list__item, li, span[aria-hidden="true"]');
                    listItems.forEach(li => {
                        const liText = li.innerText.trim();
                        if (liText.length > 2 && liText.length < 50 && !liText.toLowerCase().includes('skill')) {
                            result.skills.push(liText);
                        }
                    });
                }
            });

            return result;
        }""")

        profile_data.update(extracted)

        # Save to JSON
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70)
        print("SCRAPE RESULTS")
        print("=" * 70)
        print(f"Name:        {profile_data['intro'].get('name')}")
        print(f"Headline:    {profile_data['intro'].get('headline')}")
        print(f"Location:    {profile_data['intro'].get('location')}")
        print(f"Network:     {profile_data['intro'].get('network')}")
        print(f"About Len:   {len(profile_data.get('about', ''))} chars")
        print(f"Experience:  {len(profile_data.get('experience', []))} items found")
        print(f"Education:   {len(profile_data.get('education', []))} items found")
        print(f"Certs:       {len(profile_data.get('certifications', []))} items found")
        print(f"Projects:    {len(profile_data.get('projects', []))} items found")
        print(f"Skills:      {len(profile_data.get('skills', []))} items found")
        print(f"Sections:    {profile_data.get('sections_found', [])}")
        print("=" * 70)
        print(f"Saved full JSON to: {OUT_JSON}\n")

        await asyncio.sleep(2)
        await context.close()

    shutil.rmtree(tmp_profile, ignore_errors=True)
    print("Temp profile cleaned up. Extraction finished.")

if __name__ == "__main__":
    asyncio.run(main())

