import time
import os
import shutil
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

def copy_chrome_profile(src_dir, dest_dir):
    print(f"Copying Chrome profile to temp directory: {dest_dir}...")
    src = Path(src_dir)
    dest = Path(dest_dir)
    
    local_state = src / "Local State"
    if local_state.exists():
        shutil.copy2(local_state, dest / "Local State")
        
    default_src = src / "Default"
    default_dest = dest / "Default"
    if default_src.exists():
        shutil.copytree(default_src, default_dest, ignore=shutil.ignore_patterns("SingletonLock", "Lock", "SingletonCookie", "SingletonSocket"))

def fetch_latest_post():
    original_profile = os.path.abspath("data-tracking/chrome-profile")
    temp_profile_dir = tempfile.mkdtemp(prefix="insta-agent-")
    copy_chrome_profile(original_profile, temp_profile_dir)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=temp_profile_dir,
            headless=False,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--window-size=1280,720",
                "--no-sandbox"
            ]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("\nInstagram Agent: Navigating to @thevibefounder...")
        page.goto("https://www.instagram.com/thevibefounder/", wait_until="domcontentloaded")
        
        print("Instagram Agent: Waiting for posts to load...")
        page.wait_for_timeout(5000)
        
        post_links = page.locator('a[href*="/p/"], a[href*="/reel/"]').all()
        
        latest_url = None
        for link in post_links:
            href = link.get_attribute("href")
            if href and ("/p/" in href or "/reel/" in href):
                latest_url = "https://www.instagram.com" + href
                break
                
        if not latest_url:
            print("Instagram Agent: Could not find any posts on the profile. Saving page dump.")
            with open("insta_post.txt", "w", encoding="utf-8") as f:
                f.write(page.inner_text("body"))
            browser.close()
            return
            
        print(f"Instagram Agent: Found latest post URL: {latest_url}")
        print("Instagram Agent: Clicking post and waiting for caption...")
        page.goto(latest_url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        try:
            caption_loc = page.locator('article h1, article span[dir="auto"]').first
            caption = caption_loc.inner_text()
            caption_loc.evaluate("node => node.style.backgroundColor = 'yellow'")
            page.wait_for_timeout(1500)
            print("Instagram Agent: Caption successfully extracted.")
        except Exception as e:
            print("Instagram Agent: Could not extract exact caption, dumping article text...")
            try:
                caption = page.locator('article').first.inner_text()
            except:
                caption = page.inner_text("body")
                
        with open("insta_post.txt", "w", encoding="utf-8") as f:
            f.write(f"URL: {latest_url}\n\n")
            f.write(caption)
            
        print("Instagram Agent: Saved latest post to insta_post.txt")
        print("Instagram Agent: Done! Closing in 3 seconds...")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    fetch_latest_post()
