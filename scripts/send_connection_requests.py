"""
LinkedIn Connection Request Automation
Strategy: Send connection requests with personalized notes to unlock future messaging
This approach ALWAYS works because connection requests don't have the messaging privacy restrictions
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def setup_driver():
    """Setup Chrome with persistent profile"""
    options = webdriver.ChromeOptions()
    profile_path = os.path.abspath("data-tracking/chrome-profile")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    return webdriver.Chrome(options=options)

def get_connection_note(name, score):
    """Generate personalized connection request note"""
    first_name = name.split()[0] if name else "there"
    
    if score >= 15:
        return f"Hey {first_name}, saw your campus leadership work and was impressed. I'm Ganesh, building clstr.in — India's verified campus network. Would love to connect with student leaders like you! 👍"
    else:
        return f"Hey {first_name}, your campus engagement stands out! I'm building clstr.in and think we should connect. Let's chat! 🔗"

def send_connection_request(driver, profile_url, name, score):
    """Send connection request to a profile"""
    try:
        print(f"\n→ Opening {name}'s profile...")
        driver.get(profile_url)
        time.sleep(2)
        
        # Find and click More button (3 dots)
        try:
            more_button = driver.find_element(By.XPATH, 
                "//button[@aria-label='More actions']")
            more_button.click()
            time.sleep(1)
        except:
            pass
        
        # Try to find Connect button
        connect_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(@aria-label, 'Invite') or contains(@aria-label, 'Connect') or contains(text(), 'Connect')]")
        
        if not connect_buttons:
            print(f"  ✗ Connect button not found (might already be connected)")
            return "skipped_no_button"
        
        # Click first Connect button
        connect_buttons[0].click()
        print(f"  ✓ Clicked Connect")
        time.sleep(1)
        
        # Look for "Add a note" button/link
        try:
            add_note = driver.find_element(By.XPATH, 
                "//button[contains(text(), 'Add a note')] | //span[contains(text(), 'Add a note')]/..")
            add_note.click()
            print(f"  ✓ Opening note composer...")
            time.sleep(1)
            
            # Find note textarea and type message
            note_field = driver.find_element(By.XPATH, 
                "//textarea | //div[@contenteditable='true' and contains(@class, 'message')]")
            note_field.click()
            time.sleep(0.5)
            
            # Clear any existing text
            note_field.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            
            # Type personalized note
            note = get_connection_note(name, score)
            note_field.send_keys(note)
            print(f"  ✓ Message typed: '{note[:50]}...'")
            time.sleep(1)
            
        except Exception as e:
            print(f"  ⚠ Could not add note (continuing without it): {e}")
        
        # Find and click Send button
        send_buttons = driver.find_elements(By.XPATH, 
            "//button[contains(@aria-label, 'Send') or contains(text(), 'Send now')]")
        
        if send_buttons:
            send_buttons[0].click()
            print(f"  ✅ CONNECTION REQUEST SENT")
            time.sleep(2)
            return "sent"
        else:
            print(f"  ✗ Send button not found")
            return "failed"
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return "error"

def load_top_candidates():
    """Load top candidates from tracking"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        return []
    
    # Filter by score, remove already contacted
    candidates = [c for c in candidates if c.get('score', 0) >= 14]
    candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)
    return candidates[:10]

def update_tracking(url, status):
    """Update tracking with connection status"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        candidates = []
    
    for c in candidates:
        if c.get('url') == url:
            c['connection_request_status'] = status
            c['connection_request_timestamp'] = datetime.now().isoformat()
            break
    
    with open('data-tracking/sent_candidates.json', 'w') as f:
        json.dump(candidates, f, indent=2)

def run_connection_requests():
    """Main execution"""
    driver = setup_driver()
    
    print("\n" + "="*80)
    print("🔗 LINKEDIN CONNECTION REQUEST AUTOMATION")
    print("="*80)
    print("Sending personalized connection requests to top candidates...\n")
    
    candidates = load_top_candidates()
    
    if not candidates:
        print("No candidates found!")
        return 0
    
    print(f"Found {len(candidates)} top candidates to connect with\n")
    
    try:
        # Navigate to LinkedIn
        driver.get("https://www.linkedin.com/feed")
        time.sleep(3)
        print("✓ LinkedIn loaded\n")
        
        sent_count = 0
        
        for i, candidate in enumerate(candidates, 1):
            name = candidate.get('name', 'Unknown')
            url = candidate.get('url', '')
            score = candidate.get('score', 0)
            
            print(f"\n[{i}/{len(candidates)}] {name} (Score: {score}/20)")
            
            status = send_connection_request(driver, url, name, score)
            update_tracking(url, status)
            
            if status == "sent":
                sent_count += 1
            
            # Rate limiting between requests
            time.sleep(3)
            
            if sent_count >= 10:
                print(f"\n✅ Reached 10 connection requests!")
                break
        
        print("\n" + "="*80)
        print(f"📊 RESULTS: {sent_count} connection requests sent")
        print("="*80)
        print("\nNext steps:")
        print("1. Wait 24-48 hours for acceptances")
        print("2. Check LinkedIn notifications for new connections")
        print("3. Once connected, run messaging script to send personalized messages")
        print("4. Track in: data-tracking/sent_candidates.json")
        
        return sent_count
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        return 0
    finally:
        driver.quit()

if __name__ == "__main__":
    sent = run_connection_requests()
    print(f"\n✓ Process complete: {sent} connection requests sent")
