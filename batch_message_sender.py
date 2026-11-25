
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
