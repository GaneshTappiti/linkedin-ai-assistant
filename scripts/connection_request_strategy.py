"""
LinkedIn Connection Request Strategy
Bypasses messaging restrictions by:
1. Sending connection request with personalized note (always works)
2. Following up with message once accepted
"""

import json
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote_plus
from collections import deque

# Load top candidates from tracking
def load_top_candidates(min_score=12):
    """Load candidates sorted by score, targeting top performers"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        return []
    
    # Filter already contacted, sort by score
    candidates = [c for c in candidates if c.get('status') not in ['sent', 'connected']]
    candidates = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)
    return candidates[:20]  # Top 20 by score

def extract_first_name(name):
    """Extract first name from full name"""
    return name.split()[0] if name else "there"

def get_connection_note(name, college, signal):
    """Generate personalized connection request note"""
    first_name = extract_first_name(name)
    notes = [
        f"Hey {first_name}, I saw your work at {college} — impressive student leadership there. Building clstr.in and would love to connect campus leaders like you.",
        f"{first_name}, your campus engagement stands out. I'm Ganesh, building clstr.in (verified campus network). Let's connect!",
        f"Impressed by your role at {college}. I'm working on something special for student leaders — would love to chat. Let's connect!",
    ]
    return notes[hash(name) % len(notes)]

def send_connection_request(driver, candidate_url, candidate_name, college, signal):
    """Send connection request with personalized note"""
    try:
        driver.get(candidate_url)
        time.sleep(2)
        
        # Look for "Connect" button
        try:
            connect_button = driver.find_element(By.XPATH, 
                "//button[contains(@aria-label, 'Invite') or contains(., 'Connect')]")
            connect_button.click()
            time.sleep(1)
            
            # Check if note option appears
            try:
                add_note_button = driver.find_element(By.XPATH, 
                    "//button[contains(., 'Add a note')]")
                add_note_button.click()
                time.sleep(1)
                
                # Type personalized note
                note = get_connection_note(candidate_name, college, signal)
                note_field = driver.find_element(By.XPATH, 
                    "//textarea[@placeholder='Say something about why you'd like to connect']")
                note_field.send_keys(note)
                time.sleep(0.5)
                
            except:
                pass  # Continue without note
            
            # Send request
            send_button = driver.find_element(By.XPATH, 
                "//button[contains(@aria-label, 'Send now')]")
            send_button.click()
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f" Connection button not found or already connected. Error: {e}")
            return False
            
    except Exception as e:
        print(f" Error sending connection: {e}")
        return False

def update_tracking(candidate_url, status, notes=""):
    """Update tracking file with connection status"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        candidates = []
    
    for c in candidates:
        if c.get('url') == candidate_url:
            c['status'] = status
            c['connection_timestamp'] = datetime.now().isoformat()
            if notes:
                c['notes'] = notes
            break
    
    with open('data-tracking/sent_candidates.json', 'w') as f:
        json.dump(candidates, f, indent=2)

def run_connection_phase(driver):
    """Execute connection request phase"""
    candidates = load_top_candidates(min_score=12)
    print(f"\n🔗 Starting connection request phase for top {len(candidates)} candidates...\n")
    
    connected = 0
    for candidate in candidates:
        name = candidate.get('name', 'Unknown')
        url = candidate.get('url')
        score = candidate.get('score', 0)
        college = candidate.get('college', 'your college')
        signal = candidate.get('specific_signal', '')
        
        print(f"Connecting: {name} | Score: {score}/20 | From: {college}")
        
        if send_connection_request(driver, url, name, college, signal):
            update_tracking(url, 'connection_request_sent')
            print(f" ✓ Connection request sent")
            connected += 1
            time.sleep(3)  # Rate limit
        else:
            update_tracking(url, 'connection_failed')
            print(f" ✗ Connection failed")
        
        if connected >= 10:
            print(f"\n✅ Sent 10 connection requests. Waiting for acceptances...")
            break
    
    return connected

if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    import os
    
    # Setup Chrome driver with persistent profile
    options = webdriver.ChromeOptions()
    profile_path = os.path.abspath("data-tracking/chrome-profile")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.linkedin.com/feed")
        
        # Wait for login if needed
        print("Checking LinkedIn login status...")
        time.sleep(3)
        
        # Run connection phase
        connected = run_connection_phase(driver)
        
        print(f"\n📊 Phase 1 Complete: {connected} connection requests sent")
        print("Next step: Wait 2-3 hours for acceptances, then run message follow-up script")
        
        driver.quit()
    except Exception as e:
        print(f"Fatal error: {e}")
