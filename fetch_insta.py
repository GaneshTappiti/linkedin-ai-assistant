import time
import os
from playwright.sync_api import sync_playwright

profile_dir = os.path.abspath("data-tracking/chrome-profile")

def fetch_latest_post():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--window-size=1280,720"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("Navigating to Instagram Profile...")
        page.goto("https://www.instagram.com/thevibefounder/", wait_until="domcontentloaded")
        
        # Wait for the post grid to load
        print("Waiting for posts to load...")
        time.sleep(5)
        
        # Find the first post link (could be /p/ or /reel/)
        post_links = page.locator('a[href*="/p/"], a[href*="/reel/"]').all()
        
        latest_url = None
        for link in post_links:
            href = link.get_attribute("href")
            # Avoid tags, audio, or other non-post links
            if href and ("/p/" in href or "/reel/" in href):
                latest_url = "https://www.instagram.com" + href
                break
                
        if not latest_url:
            print("Could not find any posts on the profile. Saving page dump.")
            with open("insta_post.txt", "w", encoding="utf-8") as f:
                f.write(page.inner_text("body"))
            browser.close()
            return
            
        print(f"Found latest post URL: {latest_url}")
        print("Clicking post and waiting for caption...")
        page.goto(latest_url, wait_until="domcontentloaded")
        time.sleep(5)
        
        # Extract caption
        try:
            # Instagram captions are usually inside an article and have dir="auto" or are the h1
            caption = page.locator('article h1, article span[dir="auto"]').first.inner_text()
            print("Caption successfully extracted.")
        except Exception as e:
            print("Could not extract exact caption, dumping article text...")
            try:
                caption = page.locator('article').first.inner_text()
            except:
                caption = page.inner_text("body")
                
        # Save to file
        with open("insta_post.txt", "w", encoding="utf-8") as f:
            f.write(f"URL: {latest_url}\n\n")
            f.write(caption)
            
        print("Saved latest post to insta_post.txt")
        time.sleep(2) # Give user a moment to see
        browser.close()

if __name__ == "__main__":
    fetch_latest_post()
