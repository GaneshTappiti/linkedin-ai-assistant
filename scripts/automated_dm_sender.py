"""
LinkedIn Automated Direct Message Sender
Robust Selenium automation for sending personalized messages
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os

def setup_driver():
    """Setup Chrome with persistent profile"""
    options = webdriver.ChromeOptions()
    profile_path = os.path.abspath("data-tracking/chrome-profile")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    return webdriver.Chrome(options=options)

def get_message_text(name, score):
    """Get personalized message"""
    first_name = name.split()[0] if name else "there"
    
    if score >= 15:
        return f"""Hey {first_name}, saw your profile and impressed by your campus leadership. I'm Ganesh, building clstr.in — India's verified campus network where students connect with batchmates, alumni mentors, events, and real opportunities. 

Would love to have you as an early voice building this with us. You'd be perfect as a campus ambassador. Interested?"""
    else:
        return f"""Hey {first_name}, your campus engagement stands out! I'm building clstr.in — verified campus network. Would you be interested in being a campus ambassador? Let's chat!"""

def click_message_button(driver, wait):
    """Find and click the Message button"""
    try:
        # Try multiple selectors for Message button
        message_selectors = [
            "//button[contains(@aria-label, 'Message')]",
            "//a[contains(@aria-label, 'Message')]",
            "//button[contains(., 'Message')]",
            "//div[@data-test-id='top-card-action-menu']//button[1]",
            "//button[contains(@aria-label, 'Open')]"
        ]
        
        for selector in message_selectors:
            try:
                button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)), timeout=5)
                print(f"  ✓ Found Message button: {selector[:40]}...")
                time.sleep(0.5)
                button.click()
                return True
            except:
                continue
        
        print(f"  ✗ Message button not found with any selector")
        return False
        
    except Exception as e:
        print(f"  ✗ Error clicking message button: {e}")
        return False

def send_message_in_modal(driver, wait, message_text):
    """Send message through the modal/composer"""
    try:
        print(f"  ✓ Message compose opened, typing message...")
        
        # Wait for message field to appear
        message_field_selectors = [
            "//div[@data-test-id='message-form-text-area']",
            "//textarea[@placeholder*='message']",
            "//div[@contenteditable='true' and contains(@class, 'msg-form')]",
            "//textarea"
        ]
        
        message_field = None
        for selector in message_field_selectors:
            try:
                message_field = wait.until(EC.presence_of_element_located((By.XPATH, selector)), timeout=3)
                print(f"  ✓ Found message field: {selector[:40]}...")
                break
            except:
                continue
        
        if not message_field:
            print(f"  ✗ Message field not found")
            return False
        
        # Click field to focus
        message_field.click()
        time.sleep(0.5)
        
        # Type message
        message_field.send_keys(message_text)
        print(f"  ✓ Message typed ({len(message_text)} chars)")
        time.sleep(1)
        
        # Find and click Send button
        send_selectors = [
            "//button[@data-test-id='message-form-send']",
            "//button[contains(@aria-label, 'Send')]",
            "//button[@type='submit' and contains(., 'Send')]",
            "//button[contains(., 'Send')]"
        ]
        
        send_button = None
        for selector in send_selectors:
            try:
                send_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)), timeout=3)
                print(f"  ✓ Found Send button: {selector[:40]}...")
                break
            except:
                continue
        
        if not send_button:
            print(f"  ✗ Send button not found")
            return False
        
        # Click Send
        send_button.click()
        print(f"  ✓ Clicked Send button")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error sending message: {e}")
        return False

def send_dm_to_profile(driver, profile_url, name, score):
    """Send DM to a specific profile"""
    wait = WebDriverWait(driver, 10)
    
    try:
        print(f"\n→ Navigating to {name}'s profile...")
        driver.get(profile_url)
        time.sleep(3)
        
        # Click Message button
        if not click_message_button(driver, wait):
            return "message_button_not_found"
        
        time.sleep(2)
        
        # Send message through modal
        message_text = get_message_text(name, score)
        if send_message_in_modal(driver, wait, message_text):
            print(f"  ✅ MESSAGE SENT TO {name}")
            return "sent"
        else:
            return "send_failed"
        
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
    
    # Filter by score >= 12, sort by score
    candidates = [c for c in candidates if c.get('score', 0) >= 12]
    candidates = sorted(candidates, key=lambda x: x['score'], reverse=True)
    return candidates[:15]

def update_tracking(url, status):
    """Update tracking with send status"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        candidates = []
    
    for c in candidates:
        if c.get('url') == url:
            c['dm_send_status'] = status
            c['dm_send_timestamp'] = datetime.now().isoformat()
            if status == 'sent':
                c['status'] = 'sent'
            break
    
    with open('data-tracking/sent_candidates.json', 'w') as f:
        json.dump(candidates, f, indent=2)

def run_automated_dms():
    """Main automation loop"""
    driver = setup_driver()
    
    print("\n" + "="*80)
    print("📧 LINKEDIN AUTOMATED DM SENDER")
    print("="*80)
    print("Sending personalized direct messages to top candidates...\n")
    
    candidates = load_top_candidates()
    
    if not candidates:
        print("No candidates found!")
        return 0
    
    print(f"Found {len(candidates)} candidates ready to message\n")
    
    try:
        # Navigate to LinkedIn
        driver.get("https://www.linkedin.com/feed")
        time.sleep(3)
        print("✓ LinkedIn loaded\n")
        
        sent_count = 0
        failed_count = 0
        
        for i, candidate in enumerate(candidates, 1):
            name = candidate.get('name', 'Unknown')
            url = candidate.get('url', '')
            score = candidate.get('score', 0)
            
            print(f"[{i}/{len(candidates)}] Sending to: {name} (Score: {score}/20)")
            
            status = send_dm_to_profile(driver, url, name, score)
            update_tracking(url, status)
            
            if status == "sent":
                sent_count += 1
            else:
                failed_count += 1
            
            # Rate limiting
            if sent_count < 10:
                time.sleep(5)
            else:
                break
            
            if sent_count >= 10:
                print(f"\n✅ Reached 10 message sends!")
                break
        
        print("\n" + "="*80)
        print(f"📊 FINAL RESULTS")
        print("="*80)
        print(f"✅ Successfully sent: {sent_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📍 Total attempted: {sent_count + failed_count}")
        print("="*80)
        print(f"\nTracking saved to: data-tracking/sent_candidates.json")
        
        return sent_count
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        return 0
    finally:
        driver.quit()

if __name__ == "__main__":
    sent = run_automated_dms()
    print(f"\n✓ Automation complete: {sent} messages sent")
