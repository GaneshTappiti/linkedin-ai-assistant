#!/usr/bin/env python3
"""
LinkedIn Engagement Draft Assistant for Ganesh Tappiti
Searches for relevant posts and prepares contextual comment drafts for manual use.
This script does not auto-post comments.

Memory Context Loaded:
- Profile: Product Designer & Founder (21 years old, Visakhapatnam)
- Project: clstr.in (Production)
- Focus: Student ecosystem, startup validation, campus infrastructure
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import random
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote

# ============================================================================
# CONFIGURATION
# ============================================================================

# Search keywords aligned with Ganesh's profile and projects
SEARCH_KEYWORDS = {
    "startup_founder": [
        "startup validation",
        "founder journey",
        "MVP building",
        "startup ecosystem",
        "early-stage founders"
    ],
    "ai_llm": [
        "AI startup",
        "LLM integration",
        "prompt engineering",
        "AI MVP",
        "AI tools for founders"
    ],
    "student_ecosystem": [
        "student community",
        "college network",
        "campus startup",
        "student entrepreneurship",
        "campus ecosystem"
    ],
    "product_design": [
        "product design",
        "product validation",
        "design thinking",
        "product roadmap",
        "user-centric design"
    ],
    "India_tech": [
        "India startup ecosystem",
        "Indian founders",
        "India tech community"
    ]
}

# Context-aware comment templates based on post types
COMMENT_TEMPLATES = {
    "startup_validation": [
        "Strong point. At {project}, we see the same thing: fast validation beats perfect ideas. What signal do you trust first?",
        "Fully agree. We learned at {project} that repeat usage says more than hype. What metric do you watch early?",
        "Great take. Founders at {project} move faster when feedback loops are tight. How do you keep bias out of validation?"
    ],
    "ai_product": [
        "Love this. At {project}, AI speeds up output, but clarity still wins. What part of your stack improved outcomes most?",
        "Accurate. We built {project} for this exact gap: faster execution with better framing. Where do you see most teams struggle?",
        "Great insight. In {project}, prompt precision often beats bigger models. Are you seeing the same in production?"
    ],
    "student_community": [
        "This is real. Community-led learning is core to {project}. Are you seeing stronger traction in specific campus segments?",
        "Love this direction. We’re building {project} around the same belief: peer networks drive outcomes. What adoption pattern surprised you most?",
        "Spot on. Student ecosystems grow fast with trust and relevance, that’s what we see in {project}. What helped your activation most?"
    ],
    "design_thinking": [
        "Great framing. We use the same approach in {project}: user pain first, tech second. How do you test decisions quickly?",
        "Exactly. Iteration made {project} better than assumptions ever could. What is your fastest validation loop?",
        "Love this. Design thinking is mostly decision quality, not visuals. {project} taught us that early."
    ],
    "leadership": [
        "Needed this. Team culture has made or broken every project I’ve touched. What habit keeps your team aligned?",
        "So true. Building teams is harder than building product most days. Thanks for sharing this.",
        "This resonates. Authentic leadership changes execution speed more than people admit. What principle do you never compromise on?"
    ]
}

MAX_COMMENT_WORDS = 28
PROJECT_BRAND = "clstr.in"

# Engagement tracking
ENGAGEMENT_LOG = {
    "session_date": datetime.now().isoformat(),
    "mode": "draft_only",
    "posts_found": 0,
    "drafts_generated": 0,
    "comment_drafts": [],
    "search_keywords_used": [],
    "errors": []
}

# ============================================================================
# LINKEDIN AUTOMATION FUNCTIONS
# ============================================================================

class LinkedInEngagementBot:
    def __init__(self, headless: bool = False, close_on_finish: bool = True):
        """Initialize Selenium WebDriver for LinkedIn draft generation."""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(options=options)
        self.engagement_log = ENGAGEMENT_LOG.copy()
        self.close_on_finish = close_on_finish
    
    def search_posts(self, keyword: str, num_posts: int = 5) -> List[Dict]:
        """
        Search for posts with given keyword
        Returns list of post data (post text, author, post URL)
        """
        try:
            print(f"\n🔍 Searching for: '{keyword}'")
            
            # Navigate to LinkedIn search
            encoded_keyword = quote(keyword)
            self.driver.get(f"https://www.linkedin.com/search/results/content/?keywords={encoded_keyword}")
            time.sleep(random.randint(2, 4))
            
            posts = []
            
            # Primary selector for LinkedIn feed cards.
            post_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class,'feed-shared-update-v2')]")
            if not post_elements:
                # Fallback selector used by some UI variants.
                post_elements = self.driver.find_elements(By.XPATH, "//span[@data-spoof-text]/ancestor::div[contains(@class,'feed-shared-update-v2')]")

            print(f"   Found {len(post_elements)} potential posts")
            
            for idx, post_elem in enumerate(post_elements[:num_posts]):
                try:
                    # Extract post text using multiple fallbacks.
                    post_text = ""
                    text_selectors = [
                        ".//span[@data-spoof-text]",
                        ".//div[contains(@class,'update-components-text')]//span",
                        ".//span[@dir='ltr']",
                    ]
                    for selector in text_selectors:
                        text_nodes = post_elem.find_elements(By.XPATH, selector)
                        merged_text = " ".join([node.text.strip() for node in text_nodes if node.text.strip()])
                        if merged_text:
                            post_text = merged_text
                            break

                    if not post_text:
                        continue

                    # Try to get author name.
                    author = "Unknown"
                    author_selectors = [
                        ".//span[contains(@class,'update-components-actor__name')]//span[@aria-hidden='true']",
                        ".//*[@class*='name']",
                    ]
                    for selector in author_selectors:
                        author_nodes = post_elem.find_elements(By.XPATH, selector)
                        if author_nodes and author_nodes[0].text.strip():
                            author = author_nodes[0].text.strip()
                            break

                    # Capture an optional direct URL to the post when available.
                    post_url = ""
                    link_nodes = post_elem.find_elements(By.XPATH, ".//a[contains(@href,'/feed/update/')]")
                    if link_nodes:
                        post_url = link_nodes[0].get_attribute("href") or ""
                    
                    posts.append({
                        "keyword": keyword,
                        "text": post_text[:500],
                        "author": author,
                        "post_url": post_url,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"   ✓ Post {idx+1}: {post_text[:50]}...")
                except Exception as e:
                    self.engagement_log["errors"].append(f"Error parsing post {idx}: {str(e)}")
                    continue
            
            self.engagement_log["posts_found"] += len(posts)
            self.engagement_log["search_keywords_used"].append(keyword)
            
            return posts
        
        except Exception as e:
            error_msg = f"Search failed for '{keyword}': {str(e)}"
            print(f"   ❌ {error_msg}")
            self.engagement_log["errors"].append(error_msg)
            return []

    def generate_comment(self, post_text: str, project: str = PROJECT_BRAND) -> str:
        """
        Generate a contextual, meaningful comment based on post content
        Uses template matching and context awareness
        """
        # Detect post type based on keywords
        post_lower = post_text.lower()
        
        if any(word in post_lower for word in ["validation", "founder", "startup", "idea", "mvp", "test"]):
            templates = COMMENT_TEMPLATES.get("startup_validation", [])
        elif any(word in post_lower for word in ["ai", "llm", "prompt", "model", "gpt"]):
            templates = COMMENT_TEMPLATES.get("ai_product", [])
        elif any(word in post_lower for word in ["student", "campus", "college", "community", "network"]):
            templates = COMMENT_TEMPLATES.get("student_community", [])
        elif any(word in post_lower for word in ["design", "product", "user", "ux"]):
            templates = COMMENT_TEMPLATES.get("design_thinking", [])
        elif any(word in post_lower for word in ["leader", "team", "culture", "build"]):
            templates = COMMENT_TEMPLATES.get("leadership", [])
        else:
            templates = COMMENT_TEMPLATES.get("startup_validation", [])
        
        # Select random template and populate
        if templates:
            template = random.choice(templates)
            comment = template.format(project=project, mention=post_text[:30])
            return self.humanize_comment(comment)
        
        fallback = f"Great point. We’re seeing similar patterns in {project}. What signal tells you this is truly working?"
        return self.humanize_comment(fallback)

    def humanize_comment(self, comment: str) -> str:
        """Keep comments short, crisp, and human by default."""
        cleaned = " ".join(comment.split())
        words = cleaned.split(" ")
        if len(words) <= MAX_COMMENT_WORDS:
            return cleaned

        trimmed = " ".join(words[:MAX_COMMENT_WORDS]).rstrip(" ,;:-")
        if trimmed.endswith((".", "?", "!")):
            return trimmed
        return f"{trimmed}..."

    def run_engagement_session(self, keywords_to_use: List[str] = None, posts_per_keyword: int = 3):
        """
        Run full engagement session in safe draft-only mode.
        No comments are posted automatically.
        """
        if keywords_to_use is None:
            # Mix keywords from different categories
            keywords_to_use = [
                random.choice(SEARCH_KEYWORDS["startup_founder"]),
                random.choice(SEARCH_KEYWORDS["ai_llm"]),
                random.choice(SEARCH_KEYWORDS["student_ecosystem"]),
                random.choice(SEARCH_KEYWORDS["product_design"])
            ]
        
        print(f"\n{'='*60}")
        print(f"🚀 LINKEDIN ENGAGEMENT DRAFT SESSION (SAFE MODE)")
        print(f"{'='*60}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Keywords to search: {', '.join(keywords_to_use)}")
        print(f"Posts to draft per keyword: {posts_per_keyword}")
        print("Auto-posting is disabled. Manual review required for every comment.")
        
        try:
            # Navigate to LinkedIn feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)
            
            for keyword in keywords_to_use:
                posts = self.search_posts(keyword, num_posts=posts_per_keyword)
                
                for post_data in posts:
                    # Generate contextual comment
                    comment = self.generate_comment(post_data["text"], project=PROJECT_BRAND)

                    self.engagement_log["drafts_generated"] += 1
                    self.engagement_log["comment_drafts"].append({
                        "keyword": post_data["keyword"],
                        "project_context": PROJECT_BRAND,
                        "author": post_data["author"],
                        "post_preview": post_data["text"][:180],
                        "post_url": post_data["post_url"],
                        "draft_comment": comment,
                        "timestamp": datetime.now().isoformat(),
                        "status": "draft_only_not_posted"
                    })
                    print(f"   📝 Draft generated for {post_data['author']}: {comment[:70]}...")

                    # Lightweight pacing between reads and draft generation.
                    time.sleep(random.randint(3, 6))
            
            print(f"\n{'='*60}")
            print(f"✅ SESSION COMPLETE")
            print(f"{'='*60}")
            print(f"Posts found: {self.engagement_log['posts_found']}")
            print(f"Drafts generated: {self.engagement_log['drafts_generated']}")
            print("Comments posted automatically: 0")
            print(f"Errors: {len(self.engagement_log['errors'])}")
            
            return self.engagement_log
        
        except Exception as e:
            print(f"\n❌ Session error: {str(e)}")
            self.engagement_log["errors"].append(str(e))
            return self.engagement_log
        
        finally:
            if self.close_on_finish:
                self.driver.quit()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run the LinkedIn engagement draft workflow in safe mode."""
    
    # Initialize bot
    bot = LinkedInEngagementBot(headless=False, close_on_finish=True)
    
    # Run engagement session
    # Customize keywords and posts per keyword as needed
    results = bot.run_engagement_session(
        keywords_to_use=[
            "startup validation",
            "AI MVP",
            "student entrepreneurship",
            "product design thinking"
        ],
        posts_per_keyword=2
    )
    
    # Save results to file
    output_file = "engagement_session_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {output_file}")
    print("\n🔒 Safe mode complete: draft suggestions created and saved.")
    print("Next step: review each draft manually before posting from your account.")

if __name__ == "__main__":
    main()
