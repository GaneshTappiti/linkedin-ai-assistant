"""
LinkedIn Messaging-Enabled Profile Discovery
Strategy: Search for roles/keywords indicating profiles MORE likely to have messaging open
- College coordinators/placement officers
- Current/past brand ambassadors
- Active community builders
- Student org leaders with professional presence
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus
import os

# Keywords specifically targeting profiles that likely have messaging ENABLED
HIGH_MESSAGING_KEYWORDS = [
    "placement coordinator",
    "campus placement officer", 
    "brand ambassador manager",
    "student ambassador program",
    "community builder",
    "outreach coordinator",
    "student recruiter",
    "campus hiring",
    "college coordinator",
    "student coordinator"
]

def setup_driver():
    """Setup Selenium Chrome driver"""
    options = webdriver.ChromeOptions()
    profile_path = os.path.abspath("data-tracking/chrome-profile")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=options)
    return driver

def search_and_extract_profiles(driver, keyword, max_results=30):
    """Search for keyword and extract profile URLs"""
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(keyword)}"
    print(f"\n🔍 Searching for: {keyword}")
    print(f"URL: {search_url}")
    
    driver.get(search_url)
    time.sleep(3)
    
    profiles = []
    
    try:
        # Scroll to load more results
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Extract profile links
        profile_elements = driver.find_elements(
            By.XPATH, 
            "//a[contains(@href, '/in/') and contains(@class, 'app-aware-link')]"
        )
        
        urls_seen = set()
        for elem in profile_elements:
            try:
                href = elem.get_attribute('href')
                if href and '/in/' in href and href not in urls_seen:
                    urls_seen.add(href)
                    profiles.append(href)
                    if len(profiles) >= max_results:
                        break
            except:
                pass
        
        print(f"✓ Found {len(profiles)} profiles")
        return profiles
        
    except Exception as e:
        print(f"Error extracting profiles: {e}")
        return []

def check_messaging_available(driver, profile_url):
    """Check if messaging is available on a profile"""
    try:
        driver.get(profile_url)
        time.sleep(2)
        
        # Look for Message button
        message_buttons = driver.find_elements(
            By.XPATH,
            "//button[contains(@aria-label, 'Message')] | //a[contains(., 'Message')] | //button[contains(., 'Message')]"
        )
        
        return len(message_buttons) > 0
        
    except Exception as e:
        print(f"Error checking profile: {e}")
        return False

def run_discovery():
    """Run discovery for messaging-enabled profiles"""
    driver = setup_driver()
    
    print("\n" + "="*80)
    print("🔗 LINKEDIN MESSAGING-ENABLED PROFILE DISCOVERY")
    print("="*80)
    print("Searching for profiles likely to have messaging open...")
    
    messaging_ready_profiles = []
    all_profiles = []
    
    try:
        # Navigate to LinkedIn
        driver.get("https://www.linkedin.com/feed")
        time.sleep(3)
        print("✓ LinkedIn loaded")
        
        # Search each keyword
        for keyword in HIGH_MESSAGING_KEYWORDS:
            found = search_and_extract_profiles(driver, keyword, max_results=20)
            all_profiles.extend(found)
            
            # Sample check first 5 for messaging availability
            print(f"  Checking messaging availability on sample profiles...")
            for profile in found[:5]:
                time.sleep(1)
                if check_messaging_available(driver, profile):
                    messaging_ready_profiles.append(profile)
                    print(f"  ✓ Messaging ENABLED: {profile}")
                else:
                    print(f"  ✗ Messaging blocked: {profile}")
            
            if len(messaging_ready_profiles) >= 10:
                print(f"\nFound {len(messaging_ready_profiles)} messaging-ready profiles!")
                break
        
        print("\n" + "="*80)
        print(f"RESULTS:")
        print(f"  Total profiles found: {len(all_profiles)}")
        print(f"  Messaging-enabled found: {len(messaging_ready_profiles)}")
        print("="*80)
        
        if messaging_ready_profiles:
            # Save messaging-ready profiles
            with open('data-tracking/messaging_ready_profiles.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'profiles': messaging_ready_profiles,
                    'keywords_searched': HIGH_MESSAGING_KEYWORDS
                }, f, indent=2)
            print("\n✓ Messaging-ready profiles saved to messaging_ready_profiles.json")
            print("\nThese profiles are ready for automated messaging!")
        else:
            print("\n⚠ No messaging-enabled profiles found in this search")
        
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_discovery()
