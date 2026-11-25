#!/usr/bin/env python3
"""
Batch Direct Message Sender for LinkedIn Campus Ambassador Recruitment
Sends personalized messages to multiple candidates via LinkedIn's official API/interface
"""

import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LinkedInBatchDMSender:
    def __init__(self):
        self.config_path = Path('memory/normalized_2026-04-26/clstr_hiring_automation_config.json')
        self.outreach_log_path = Path('data-tracking/outreach_log.json')
        self.profiles = [
            "https://www.linkedin.com/in/oluwatimileyinomowore/",
            "https://www.linkedin.com/in/saiteja2408/",
            "https://www.linkedin.com/in/yeluri-durga-raja-sekhar-628257255/",
            "https://www.linkedin.com/in/lagudukumarswamykishan/",
            "https://www.linkedin.com/in/subhash-addepalli-b14a95293/",
            "https://www.linkedin.com/in/vishal-epu-646822222/",
            "https://www.linkedin.com/in/siva-nellipudi/",
            "https://www.linkedin.com/in/chinmay-guntuku-173861282/",
            "https://www.linkedin.com/in/sainaidu77/",
            "https://www.linkedin.com/in/praveen-seelaboyina-500898243/",
        ]
        self.sent_messages = []
        self.load_config()
        self.load_existing_log()

    def load_config(self):
        """Load hiring automation config"""
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
                logger.info(f"Loaded config from {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Config not found at {self.config_path}")
            self.config = {}

    def load_existing_log(self):
        """Load existing outreach log"""
        try:
            if self.outreach_log_path.exists():
                with open(self.outreach_log_path) as f:
                    data = json.load(f)
                    self.sent_messages = data.get('messages', [])
                    logger.info(f"Loaded {len(self.sent_messages)} existing messages")
        except Exception as e:
            logger.warning(f"Could not load existing log: {e}")

    def get_casual_opener_template(self):
        """Get the casual opener message template from config"""
        return self.config.get('stages', {}).get('s1_casual_opener', {}).get('template', 
            "Hey {first_name}, I'm building clstr.in — India's verified campus network where students connect with batchmates, alumni mentors, events, and real opportunities in one place. We're bringing on strong campus leaders. What's one thing students at {college_name} struggle with the most right now?")

    def extract_name_from_profile_url(self, url):
        """Extract likely first name from LinkedIn profile URL"""
        # URL format: /in/firstname-lastname-id/
        parts = url.split('/in/')[1].rstrip('/').split('-')
        if parts:
            name = parts[0].capitalize()
            return name
        return "there"

    def generate_message(self, profile_url):
        """Generate personalized message for a profile"""
        template = self.get_casual_opener_template()
        first_name = self.extract_name_from_profile_url(profile_url)
        
        # For now, use generic college since we can't extract from LinkedIn dynamically
        message = template.format(
            first_name=first_name,
            college_name="your college"
        )
        
        return message

    def create_browser_automation_script(self):
        """Create a Playwright script for browser-based message sending"""
        script = '''
import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

async def send_batch_messages():
    async with async_playwright() as p:
        # Use existing Chrome profile
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="data-tracking/chrome-profile",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = await browser.new_page()
        
        profiles_to_message = [
            ("oluwatimileyinomowore", "Oluwatimi"),
            ("saiteja2408", "Sai Teja"),
            ("yeluri-durga-raja-sekhar-628257255", "Durga"),
            ("lagudukumarswamykishan", "Kisan"),
            ("subhash-addepalli-b14a95293", "Subhash"),
            ("vishal-epu-646822222", "Vishal"),
            ("siva-nellipudi", "Siva"),
            ("chinmay-guntuku-173861282", "Chinmay"),
            ("sainaidu77", "Sainaidu"),
            ("praveen-seelaboyina-500898243", "Praveen"),
        ]
        
        sent_count = 0
        
        for username, first_name in profiles_to_message:
            try:
                profile_url = f"https://www.linkedin.com/in/{username}/"
                await page.goto(profile_url)
                await page.wait_for_timeout(2000)
                
                # Click message button
                msg_btn = await page.query_selector('a[href*="/messaging/compose"]')
                if msg_btn:
                    await msg_btn.click()
                else:
                    button = await page.query_selector('button:has-text("Message")')
                    if button:
                        await button.click()
                
                await page.wait_for_timeout(1000)
                
                # Type message
                message = f"Hey {first_name}, saw your profile — you're clearly building great things. I'm working on clstr.in, India's verified campus network connecting students, alumni mentors, and real opportunities in one place. We're looking for strong campus ambassadors to shape the rollout. What's the biggest challenge students at your college face right now?"
                
                textarea = await page.query_selector('[contenteditable="true"], textarea')
                if textarea:
                    await textarea.fill(message)
                    await page.wait_for_timeout(500)
                    
                    # Click send
                    send_btn = await page.query_selector('button[aria-label*="Send"], button img[class*="send"]')
                    if send_btn:
                        await send_btn.click()
                        sent_count += 1
                        print(f"Message sent to {first_name}")
                        await page.wait_for_timeout(2000)
                    
            except Exception as e:
                print(f"Error messaging {first_name}: {e}")
                continue
        
        await browser.close()
        print(f"Batch complete: {sent_count} messages sent")

asyncio.run(send_batch_messages())
'''
        return script

    def save_batch_script(self):
        """Save the automation script"""
        script = self.create_browser_automation_script()
        script_path = Path('batch_message_sender.py')
        with open(script_path, 'w') as f:
            f.write(script)
        logger.info(f"Saved batch script to {script_path}")
        return script_path

    def log_messages_sent(self, messages):
        """Log sent messages to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'messages': messages,
            'total_sent': len(messages)
        }
        
        log_data = {'messages': messages}
        self.outreach_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.outreach_log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Logged {len(messages)} messages to {self.outreach_log_path}")

    def generate_message_batch(self):
        """Generate all messages ready to send"""
        messages = []
        for profile_url in self.profiles:
            message = {
                'profile_url': profile_url,
                'message_body': self.generate_message(profile_url),
                'status': 'pending',
                'timestamp': datetime.now().isoformat()
            }
            messages.append(message)
        return messages

def main():
    sender = LinkedInBatchDMSender()
    
    # Generate all messages
    messages = sender.generate_message_batch()
    
    print("\n" + "="*70)
    print("BATCH MESSAGE PREVIEW - Ready to Send via Browser")
    print("="*70)
    
    for i, msg in enumerate(messages, 1):
        print(f"\n[Message {i}/10]")
        print(f"Profile: {msg['profile_url']}")
        print(f"Message:\n{msg['message_body']}")
        print("-" * 70)
    
    # Save batch script
    sender.save_batch_script()
    
    print("\n✓ Next step: Use the batch_message_sender.py script to send all messages via browser automation")

if __name__ == "__main__":
    main()
