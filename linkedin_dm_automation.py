"""
LinkedIn DM Automation - Sequential Outreach
Processes candidates one-by-one with tracking to avoid duplicate messaging
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_outreach.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LinkedInContactTracker:
    """Tracks contacted accounts to prevent duplicate messaging"""
    
    def __init__(self, tracker_file: str = "contacted_accounts.json"):
        self.tracker_file = tracker_file
        self.contacted = self._load_tracker()
    
    def _load_tracker(self) -> Dict:
        """Load existing contact history"""
        if Path(self.tracker_file).exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def save(self):
        """Persist tracker to disk"""
        with open(self.tracker_file, 'w') as f:
            json.dump(self.contacted, f, indent=2, default=str)
    
    def has_contacted(self, linkedin_url: str) -> bool:
        """Check if account already contacted"""
        return linkedin_url in self.contacted
    
    def mark_contacted(self, linkedin_url: str, message: str, status: str = "sent"):
        """Mark account as contacted"""
        self.contacted[linkedin_url] = {
            "contacted_at": datetime.now().isoformat(),
            "message_sent": message,
            "status": status  # sent, pending, failed
        }
        self.save()
    
    def get_status(self, linkedin_url: str) -> Optional[Dict]:
        """Get contact history for an account"""
        return self.contacted.get(linkedin_url)


class LinkedInDMAutomation:
    """Selenium-based LinkedIn DM automation with sequential processing"""
    
    def __init__(self, config_path: str, email: str, password: str):
        self.config = self._load_config(config_path)
        self.email = email
        self.password = password
        self.driver = None
        self.tracker = LinkedInContactTracker()
        self.wait = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load hiring automation config"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def start_browser(self):
        """Initialize Selenium WebDriver"""
        logger.info("Starting Selenium WebDriver...")
        options = webdriver.ChromeOptions()
        # Uncomment for headless mode: options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("Browser started successfully")
    
    def login_linkedin(self):
        """Authenticate with LinkedIn"""
        logger.info("Logging into LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")
        
        try:
            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Sign in']")
            login_btn.click()
            
            # Wait for dashboard to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "global-nav")))
            logger.info("✓ LinkedIn login successful")
        except TimeoutException as e:
            logger.error(f"Login failed: {e}")
            raise
    
    def get_candidate_profiles(self, search_keywords: List[str]) -> List[Dict]:
        """
        Search for and extract candidate profiles
        Returns list of profiles with minimal info for screening
        """
        logger.info(f"Searching for candidates with keywords: {search_keywords}")
        profiles = []
        
        for keyword in search_keywords[:3]:  # Limit to first 3 keywords
            try:
                # Navigate to search
                self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={keyword}")
                time.sleep(3)
                
                # Extract profile links
                profile_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "a.app-aware-link[href*='/in/']"
                )
                
                for elem in profile_elements[:5]:  # Limit to first 5 per keyword
                    try:
                        link = elem.get_attribute('href')
                        if link and '/in/' in link:
                            # Extract clean URL
                            clean_url = link.split('?')[0]
                            if clean_url not in [p['url'] for p in profiles]:
                                profiles.append({
                                    'url': clean_url,
                                    'keyword': keyword,
                                    'extracted_at': datetime.now().isoformat()
                                })
                    except Exception as e:
                        logger.debug(f"Error extracting profile link: {e}")
                
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Error searching keyword '{keyword}': {e}")
        
        logger.info(f"✓ Extracted {len(profiles)} candidate profiles")
        return profiles
    
    def analyze_profile(self, profile_url: str) -> Dict:
        """
        Visit profile and extract key info for personalization
        """
        logger.info(f"Analyzing profile: {profile_url}")
        
        try:
            self.driver.get(profile_url)
            time.sleep(2)
            
            profile_data = {
                'url': profile_url,
                'first_name': '',
                'headline': '',
                'college': '',
                'year': '',
                'recent_activity': '',
                'leadership_signals': []
            }
            
            # Extract name
            try:
                name_elem = self.driver.find_element(By.CLASS_NAME, "text-heading-xlarge")
                profile_data['first_name'] = name_elem.text.split()[0]
            except:
                pass
            
            # Extract headline
            try:
                headline_elem = self.driver.find_element(By.CLASS_NAME, "text-body-medium")
                profile_data['headline'] = headline_elem.text
            except:
                pass
            
            # Extract about section
            try:
                about_elem = self.driver.find_element(By.ID, "about")
                profile_data['about'] = about_elem.text[:500]
            except:
                pass
            
            # Check for leadership signals in headline/about
            text_to_analyze = (profile_data['headline'] + " " + profile_data.get('about', '')).lower()
            leadership_keywords = [
                'campus ambassador', 'student council', 'club lead', 'event coordinator',
                'marketing lead', 'growth', 'community lead', 'founder', 'coordinator'
            ]
            
            for keyword in leadership_keywords:
                if keyword in text_to_analyze:
                    profile_data['leadership_signals'].append(keyword)
            
            logger.info(f"  Profile: {profile_data['first_name']} | Headline: {profile_data['headline'][:50]}")
            return profile_data
        
        except Exception as e:
            logger.error(f"Error analyzing profile: {e}")
            return None
    
    def score_profile(self, profile_data: Dict) -> int:
        """
        Quick scoring to determine if outreach is worthwhile
        """
        score = 0
        
        # Check for college signals
        if 'college' in profile_data['about'].lower():
            score += 3
        
        # Check for leadership signals
        score += min(len(profile_data['leadership_signals']) * 2, 6)
        
        # Check for recent activity
        if profile_data['recent_activity']:
            score += 2
        
        return min(score, 20)
    
    def generate_personalized_message(self, profile_data: Dict) -> str:
        """
        Generate personalized outreach message based on profile and config
        """
        first_name = profile_data.get('first_name', 'there')
        headline = profile_data.get('headline', '')
        leadership_signals = profile_data.get('leadership_signals', [])
        college_name = profile_data.get('college', 'your college')
        
        # Select template based on signals
        if leadership_signals:
            specific_signal = leadership_signals[0]
            template = self.config['message_templates']['casual_opener']
        else:
            template = self.config['message_templates']['casual_opener']
        
        # Personalize template
        message = template.format(
            first_name=first_name,
            college_name=college_name
        )
        
        return message
    
    def open_messaging(self, profile_url: str) -> bool:
        """
        Navigate to messaging interface and prepare to send DM
        """
        logger.info(f"Opening messaging for: {profile_url}")
        
        try:
            self.driver.get(profile_url)
            time.sleep(2)
            
            # Click message button
            try:
                message_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Message')]"))
                )
                message_btn.click()
                time.sleep(1)
                logger.info("✓ Message button clicked")
                return True
            except TimeoutException:
                logger.warning("Message button not found or not clickable")
                return False
        
        except Exception as e:
            logger.error(f"Error opening messaging: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """
        Type and send the message in the compose area
        """
        logger.info(f"Sending message ({len(message)} chars)...")
        
        try:
            # Find message input area
            message_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".msg-form__contenteditable"))
            )
            
            # Type message
            message_input.click()
            message_input.send_keys(message)
            time.sleep(1)
            
            # Send button
            send_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='Send']")
            send_btn.click()
            
            time.sleep(2)
            logger.info("✓ Message sent successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def process_single_account(self, profile_url: str) -> Tuple[bool, str]:
        """
        Process ONE account end-to-end:
        1. Check if already contacted
        2. Analyze profile
        3. Score profile
        4. Generate personalized message
        5. Send message
        6. Track contact
        
        Returns: (success: bool, message_sent: str)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {profile_url}")
        logger.info('='*60)
        
        # Step 1: Check if already contacted
        if self.tracker.has_contacted(profile_url):
            status = self.tracker.get_status(profile_url)
            logger.warning(f"⚠ Already contacted on {status['contacted_at']}")
            return False, f"SKIPPED - Already contacted: {status['status']}"
        
        # Step 2: Analyze profile
        profile_data = self.analyze_profile(profile_url)
        if not profile_data:
            logger.error("Could not analyze profile")
            return False, "FAILED - Could not analyze profile"
        
        # Step 3: Score profile
        score = self.score_profile(profile_data)
        logger.info(f"Profile score: {score}/20")
        
        if score < self.config['scoring']['minimum_for_outreach']:
            logger.warning(f"Score too low ({score} < {self.config['scoring']['minimum_for_outreach']})")
            self.tracker.mark_contacted(profile_url, "N/A - Low score", "skipped")
            return False, f"SKIPPED - Low score: {score}"
        
        # Step 4: Generate personalized message
        message = self.generate_personalized_message(profile_data)
        logger.info(f"\n📝 Personalized Message:\n{message}\n")
        
        # Step 5: Open messaging
        if not self.open_messaging(profile_url):
            logger.error("Could not open messaging")
            self.tracker.mark_contacted(profile_url, message, "failed_messaging")
            return False, "FAILED - Could not open messaging"
        
        # Step 6: Send message
        if not self.send_message(message):
            logger.error("Could not send message")
            self.tracker.mark_contacted(profile_url, message, "failed_send")
            return False, "FAILED - Could not send message"
        
        # Step 7: Track contact
        self.tracker.mark_contacted(profile_url, message, "sent")
        logger.info("✓ Contact tracked in database")
        
        return True, f"SENT - Message delivered to {profile_data['first_name']}"
    
    def run_sequential_outreach(self, candidate_urls: List[str]):
        """
        Process candidates ONE AT A TIME sequentially
        Never parallel - scan, draft, send for each before moving to next
        """
        logger.info(f"\n\n{'*'*70}")
        logger.info(f"Starting Sequential Outreach - {len(candidate_urls)} candidates")
        logger.info('*'*70)
        
        self.start_browser()
        
        try:
            self.login_linkedin()
            
            results = {
                'sent': [],
                'skipped': [],
                'failed': []
            }
            
            for idx, candidate_url in enumerate(candidate_urls, 1):
                logger.info(f"\n[{idx}/{len(candidate_urls)}] Processing...")
                
                success, message = self.process_single_account(candidate_url)
                
                if success:
                    results['sent'].append((candidate_url, message))
                elif 'SKIPPED' in message:
                    results['skipped'].append((candidate_url, message))
                else:
                    results['failed'].append((candidate_url, message))
                
                # Wait before next account (be respectful to LinkedIn)
                if idx < len(candidate_urls):
                    logger.info("Waiting 5 seconds before next account...")
                    time.sleep(5)
            
            self._print_summary(results)
            return results
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
    
    def _print_summary(self, results: Dict):
        """Print final summary"""
        logger.info(f"\n\n{'='*70}")
        logger.info("OUTREACH SUMMARY")
        logger.info('='*70)
        logger.info(f"✓ Sent: {len(results['sent'])}")
        for url, msg in results['sent']:
            logger.info(f"  • {url}: {msg}")
        
        logger.info(f"⊘ Skipped: {len(results['skipped'])}")
        for url, msg in results['skipped']:
            logger.info(f"  • {url}: {msg}")
        
        logger.info(f"✗ Failed: {len(results['failed'])}")
        for url, msg in results['failed']:
            logger.info(f"  • {url}: {msg}")
        
        logger.info('='*70)


def main():
    """Main entry point"""
    
    # Configuration
    CONFIG_PATH = "docs/automation/clstr_hiring_automation_config.json"
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        logger.error("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD env vars")
        return
    
    # Initialize automation
    automation = LinkedInDMAutomation(CONFIG_PATH, LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
    
    # Get candidate profiles
    keywords = automation.config['candidate_sources']['preferred_search_keywords']
    candidate_urls = automation.get_candidate_profiles(keywords)
    
    if not candidate_urls:
        logger.error("No candidates found")
        return
    
    # Run sequential outreach
    results = automation.run_sequential_outreach([p['url'] for p in candidate_urls])
    
    logger.info("\n✓ Automation complete")


if __name__ == "__main__":
    main()
