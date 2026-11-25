import asyncio
import sys
from pathlib import Path

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && python -m playwright install chromium")
        sys.exit(1)

    REPO_ROOT = Path(__file__).parent.parent
    CHROME_PROFILE = str(REPO_ROOT / "data-tracking" / "chrome-profile")
    
    print("\n" + "="*80)
    print("LINKEDIN SESSION LOGIN HELPER")
    print("="*80)
    print(f"This script will open Chrome using your persistent profile: {CHROME_PROFILE}")
    print("Please make sure all other Chrome processes using this profile are closed first.\n")
    
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                CHROME_PROFILE,
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
        except Exception as e:
            print(f"ERROR launching browser: {e}")
            print("Please ensure no other script or Chrome window is currently using the profile directory.")
            return

        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")

        print("Navigating to LinkedIn homepage...")
        await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded")
        
        print("\n>>> ACTION REQUIRED: <<<")
        print("1. A Chrome window has opened.")
        print("2. If you are not logged in, please log in manually now.")
        print("3. Solve any CAPTCHAs/verification challenges if prompted.")
        print("4. Once you are successfully logged in and see your home feed, come back here.")
        
        # We run inside an async event loop, so we can run an executor or loop to wait for input.
        # But to be simple, we can just do a loop checking the page URL or wait for the user to press Enter.
        # Let's use asyncio.to_thread for input() so it doesn't block the loop.
        await asyncio.to_thread(input, "\nPress [ENTER] here in the terminal once you are logged in and ready to save your session...")
        
        # Save cookies and state
        print("Saving cookies and closing browser...")
        await context.close()
        print("Done! Session successfully saved to your persistent profile.")

if __name__ == "__main__":
    asyncio.run(main())
