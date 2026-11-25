"""
scripts/scrape_spark_live.py
Navigates to https://spark.clstr.in in headless mode, takes a screenshot,
and dumps the complete visible innerText of the homepage.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT = REPO_ROOT / "data-tracking" / "spark_live_screenshot.png"
OUTPUT_TXT = REPO_ROOT / "data-tracking" / "spark_live_text.txt"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        print("Navigating to https://spark.clstr.in...")
        await page.goto("https://spark.clstr.in", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        # Scroll down to hydrate everything
        for _ in range(8):
            await page.keyboard.press("PageDown")
            await asyncio.sleep(0.5)

        await page.screenshot(path=str(SCREENSHOT), full_page=True)
        print(f"Screenshot saved to: {SCREENSHOT}")

        text = await page.evaluate("() => document.body.innerText")
        with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text dumped to: {OUTPUT_TXT} ({len(text)} characters)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

