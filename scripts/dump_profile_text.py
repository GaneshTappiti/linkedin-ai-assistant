"""
scripts/dump_profile_text.py
Dumps the complete innerText and structured sections of Ganesh's profile using Playwright keyboard navigation.
"""
import asyncio
import json
import shutil
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
CHROME_PROFILE = REPO_ROOT / "data-tracking" / "chrome-profile"
OUT_TEXT = REPO_ROOT / "data-tracking" / "profile_full_text.txt"
OUT_JSON = REPO_ROOT / "data-tracking" / "profile_full_structured.json"

def robust_copy(src, dst):
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        d = dst / item.name
        if item.is_dir():
            robust_copy(item, d)
        else:
            try: shutil.copy2(item, d)
            except: pass

async def main():
    tmp_profile = tempfile.mkdtemp(prefix="li-text-")
    print(f"Copying profile to: {tmp_profile}")
    robust_copy(CHROME_PROFILE, tmp_profile)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            tmp_profile,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--start-maximized"],
            ignore_https_errors=True,
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        print("Navigating to profile...")
        await page.goto("https://www.linkedin.com/in/ganeshtappiti/", wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(6)

        # Click on the middle of page to ensure focus
        await page.mouse.click(500, 400)
        await asyncio.sleep(1)

        # Scroll incrementally with PageDown and mouse wheel
        print("Scrolling through all sections...")
        for i in range(15):
            await page.keyboard.press("PageDown")
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(1.2)
            # Take screenshot at step 3, 7, 12
            if i == 3:
                await page.screenshot(path=str(REPO_ROOT / "data-tracking" / "prof_scroll_1.png"))
            elif i == 7:
                await page.screenshot(path=str(REPO_ROOT / "data-tracking" / "prof_scroll_2.png"))
            elif i == 12:
                await page.screenshot(path=str(REPO_ROOT / "data-tracking" / "prof_scroll_3.png"))

        # Try to click any 'see more' buttons
        try:
            buttons = await page.query_selector_all("button")
            for b in buttons:
                txt = (await b.inner_text()).lower()
                if "see more" in txt or "show all" in txt:
                    try:
                        await b.click()
                        await asyncio.sleep(0.5)
                    except:
                        pass
        except:
            pass

        # Extract full page inner text
        full_text = await page.evaluate("() => document.body.innerText")
        with open(OUT_TEXT, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"Full page text saved to: {OUT_TEXT} ({len(full_text)} characters)")

        # Extract all section blocks
        sections_data = await page.evaluate("""() => {
            const data = {};
            const sections = document.querySelectorAll('section');
            sections.forEach((sec, idx) => {
                const header = sec.querySelector('h2, [class*="title"]');
                const title = header ? header.innerText.trim() : 'Section_' + idx;
                data[title] = sec.innerText.trim();
            });
            return data;
        }""")

        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
        print(f"Sections JSON saved to: {OUT_JSON} ({len(sections_data)} sections)")

        await context.close()

    shutil.rmtree(tmp_profile, ignore_errors=True)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())

