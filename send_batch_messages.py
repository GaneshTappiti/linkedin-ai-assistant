#!/usr/bin/env python3
"""
LinkedIn Direct Message Automation using Playwright
Sends personalized campus ambassador recruitment messages to 9 candidates
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
from pathlib import Path

# Candidates to message (excluding Madhuri who was already sent)
CANDIDATES = [
    ("oluwatimileyinomowore", "Oluwatimi", "Oluwatimi"),
    ("saiteja2408", "Sai Teja", "Sai Teja"),
    ("yeluri-durga-raja-sekhar-628257255", "Durga", "Durga"),
    ("lagudukumarswamykishan", "Kishan", "Kumar Swamy"),
    ("subhash-addepalli-b14a95293", "Subhash", "Subhash"),
    ("vishal-epu-646822222", "Vishal", "Vishal"),
    ("siva-nellipudi", "Siva", "Siva"),
    ("chinmay-guntuku-173861282", "Chinmay", "Chinmay"),
    ("sainaidu77", "Sainaidu", "Sainaidu"),
    ("praveen-seelaboyina-500898243", "Praveen", "Praveen"),
]

MESSAGE_TEMPLATE = """Hey {first_name}, saw your profile — you're clearly building great things. I'm working on clstr.in, India's verified campus network connecting students, alumni mentors, events, and real opportunities in one place. We're bringing on strong campus ambassadors to shape how this rolls out across colleges. What's the biggest thing students at your college need right now?"""

async def send_message_to_candidate(page, username, first_name):
    """Send message to a single candidate"""
    try:
        profile_url = f"https://www.linkedin.com/in/{username}/"
        print(f"\n[→] Processing: {first_name} ({username})")
        
        # Navigate to profile
        await page.goto(profile_url, wait_until='networkidle')
        await page.wait_for_timeout(1500)
        
        # Click Message button - try multiple selectors
        message_clicked = False
        
        # Try selector 1: href containing messaging
        try:
            msg_link = await page.query_selector('a[href*="/messaging/compose"]')
            if msg_link:
                await msg_link.click()
                message_clicked = True
        except:
            pass
        
        # Try selector 2: Button with text "Message"
        if not message_clicked:
            try:
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    text = await btn.text_content()
                    if text and 'Message' in text:
                        await btn.click()
                        message_clicked = True
                        break
            except:
                pass
        
        if not message_clicked:
            print(f"  ✗ Could not find Message button")
            return False
        
        # Wait for compose modal
        await page.wait_for_timeout(2000)
        
        # Find and fill message textarea
        text_area = await page.query_selector('[contenteditable="true"]')
        if not text_area:
            text_area = await page.query_selector('textarea')
        
        if not text_area:
            print(f"  ✗ Could not find message textarea")
            return False
        
        # Type message
        message = MESSAGE_TEMPLATE.format(first_name=first_name)
        await text_area.fill(message)
        await page.wait_for_timeout(800)
        
        # Find and click Send button
        send_btn = None
        
        # Try to find send button by aria-label
        buttons = await page.query_selector_all('button')
        for btn in buttons:
            aria_label = await btn.get_attribute('aria-label')
            if aria_label and 'send' in aria_label.lower():
                send_btn = btn
                break
        
        # If not found, try to find the rightmost button in the message dialog
        if not send_btn:
            # Look for any button with send icon next to textarea
            try:
                send_btn = await page.query_selector('button >> nth=0')  # First visible button near textarea
            except:
                pass
        
        if not send_btn:
            # Last resort: find any enabled button that's visible
            buttons = await page.query_selector_all('button')
            for btn in reversed(buttons):
                is_visible = await btn.is_visible()
                is_enabled = await btn.is_enabled()
                if is_visible and is_enabled:
                    send_btn = btn
                    break
        
        if send_btn:
            await send_btn.click()
            await page.wait_for_timeout(2000)
            print(f"  ✓ Message sent to {first_name}")
            return True
        else:
            print(f"  ✗ Could not find Send button")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

async def main():
    """Main automation loop"""
    async with async_playwright() as p:
        # Connect to existing Chrome profile
        browser = await p.chromium.connect_over_cdp(
            "http://localhost:9222"  # Make sure Chrome is running with --remote-debugging-port=9222
        ) if False else await p.chromium.launch_persistent_context(
            user_data_dir="data-tracking/chrome-profile",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            slow_mo=500
        )
        
        page = await browser.new_page()
        
        # Statistics
        sent_count = 0
        failed_count = 0
        results = {
            'timestamp': datetime.now().isoformat(),
            'sent': [],
            'failed': []
        }
        
        print("=" * 70)
        print("LINKEDIN BATCH MESSAGE SENDER")
        print("=" * 70)
        print(f"Total candidates to message: {len(CANDIDATES)}")
        print("=" * 70)
        
        for username, display_name, first_name in CANDIDATES:
            success = await send_message_to_candidate(page, username, first_name)
            
            if success:
                sent_count += 1
                results['sent'].append({'username': username, 'name': display_name})
            else:
                failed_count += 1
                results['failed'].append({'username': username, 'name': display_name})
            
            # Delay between messages to avoid detection
            await page.wait_for_timeout(3000)
        
        # Save results
        results_path = Path('data-tracking/batch_send_results.json')
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n" + "=" * 70)
        print("BATCH SEND COMPLETE")
        print("=" * 70)
        print(f"✓ Successfully sent: {sent_count}")
        print(f"✗ Failed: {failed_count}")
        print(f"Results saved to: {results_path}")
        print("=" * 70)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
