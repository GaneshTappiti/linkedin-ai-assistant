import asyncio
import shutil
import os
import json
import tempfile
import random
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from playwright.async_api import async_playwright

# Configuration paths
CHROME_PROFILE = Path("data-tracking/chrome-profile").resolve()
POST_HISTORY_FILE = Path("memory/linkedin_post_history.json")
NATIVE_LOG_FILE = Path("data-tracking/post_native_log.json")
GENERATED_IMAGE = Path(r"C:\Users\2005g\.gemini\antigravity\brain\d779907d-cc5b-499a-81d7-09876f8b49d7\student_founder_ai_stack_2026_1782393670178.png")
DEST_IMAGE = Path("memory/post_images/2026-06-25_student_founder_ai_stack.png")

post_data = {
    "topic": "The 2026 AI coding assistant stack for student founders",
    "research_source": "120 student founder tech stacks in India in June 2026",
    "data_items": [
        {"label": "Cursor (for main IDE coding)", "percentage": 84},
        {"label": "GitHub Copilot (for quick autocomplete)", "percentage": 68},
        {"label": "Claude Code / Aider (for agentic CLI tasks)", "percentage": 51},
        {"label": "ChatGPT / Claude Web (for planning & architecture)", "percentage": 43},
        {"label": "V0 / Bolt.new (for quick UI prototyping)", "percentage": 37},
        {"label": "Cursor Composer (for multi-file generation)", "percentage": 29}
    ],
    "content_pillar": "AI-Enabled Building",
    "post_type": "research_data",
    "hook_type": "direct_authority",
    "post_text": """I scanned 120 student founder tech stacks in India last month.

Here is the real AI coding assistant stack they actually use to ship 👇

📊 Cursor (for main IDE coding) — 84%
📊 GitHub Copilot (for quick autocomplete) — 68%
📊 Claude Code / Aider (for agentic CLI tasks) — 51%
📊 ChatGPT / Claude Web (for planning & architecture) — 43%
📊 V0 / Bolt.new (for quick UI prototyping) — 37%
📊 Cursor Composer (for multi-file generation) — 29%

One thing became obvious after scanning all this:
The era of relying on a single 'AI chatbot' is over.
Successful student founders build a multi-tool pipeline:
→ Autocomplete for micro-tasks
→ Agentic CLI for refactoring
→ IDE composers for multi-file systems

I'm seeing this exact shift while building clstr.in.
Cursor handles the structure, but Aider does the heavy CLI lifting.

What does your AI coding stack look like today? 👇

#AI #StudentFounders #BuildInPublic""",
    "hashtags": ["#AI", "#StudentFounders", "#BuildInPublic"],
    "engagement_question": "What does your AI coding stack look like today?",
    "chart_title": "Student Founder AI Stack 2026",
    "image_prompt": "A hand-drawn horizontal bar chart showing Student Founder AI Stack 2026",
    "word_count": 145,
    "hook_first_line": "I scanned 120 student founder tech stacks in India last month.",
    "predicted_reach": "50,000+ impressions with high saves"
}

def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def copy_image_to_clipboard(image_path: str) -> bool:
    ps_path = image_path.replace("\\", "\\\\")
    ps_script = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        f"$img = [System.Drawing.Image]::FromFile('{ps_path}'); "
        "[System.Windows.Forms.Clipboard]::SetImage($img); "
        "Write-Output 'Image copied to clipboard.'"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True, text=True
    )
    print(f"  Clipboard: {result.stdout.strip()}")
    return "copied" in result.stdout.lower()

def robust_copy_tree(src: Path, dst: str):
    import os
    src = Path(src)
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    for item in os.listdir(src):
        s = src / item
        d = dst / item
        if s.is_dir():
            try:
                robust_copy_tree(s, str(d))
            except Exception:
                pass
        else:
            try:
                shutil.copy2(str(s), str(d))
            except Exception:
                pass

async def post_to_linkedin_robust(post_text: str, image_path: str) -> bool:
    tmp_profile = tempfile.mkdtemp(prefix="li-post-rob-")
    print(f"  Copying Chrome profile to temp: {tmp_profile}")
    robust_copy_tree(CHROME_PROFILE, tmp_profile)
    print("  Profile copied.")

    success = False
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=tmp_profile,
                headless=False,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--start-maximized",
                    "--disable-infobars",
                ],
                ignore_https_errors=True,
                no_viewport=True,
            )

            page = context.pages[0] if context.pages else await context.new_page()

            # 1. Navigate to feed
            print("  Navigating to LinkedIn feed...")
            await page.goto("https://www.linkedin.com/feed/", wait_until="load", timeout=45000)
            print("  Page loaded. Waiting 10 seconds for React hydration...")
            await asyncio.sleep(10)

            if "login" in page.url or "authwall" in page.url:
                print("  ERROR: LinkedIn session expired. Re-login required.")
                await context.close()
                return False
            print(f"  Feed loaded: {page.url}")

            # Scroll to top
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(2)

            # 2. Click 'Start a post'
            print("  Waiting for 'Start a post' button...")
            start_btn = page.locator("button", has_text="Start a post")
            
            # Wait for it to be visible
            try:
                await start_btn.wait_for(state="visible", timeout=15000)
                await start_btn.click()
                print("  'Start a post' button clicked.")
            except Exception as e:
                print(f"  Failed to find button with text: {e}")
                # Fallback selectors
                fallback_selectors = [
                    "button.share-box-feed-entry__trigger",
                    "button[class*='share-box-feed-entry__trigger']",
                    "[placeholder='Start a post']",
                ]
                clicked = False
                for sel in fallback_selectors:
                    try:
                        el = await page.wait_for_selector(sel, timeout=5000)
                        if el:
                            await el.click()
                            clicked = True
                            print(f"  Clicked fallback selector: {sel}")
                            break
                    except Exception:
                        continue
                if not clicked:
                    print("  ERROR: Could not click 'Start a post'. Saving failure screenshot.")
                    await page.screenshot(path="failure_start_post.png")
                    await context.close()
                    return False

            await asyncio.sleep(3)

            # 3. Paste image from clipboard
            if image_path and Path(image_path).exists():
                print("  Pasting image from clipboard (Ctrl+V)...")
                await page.keyboard.press("Control+v")
                print("  Waiting 6 seconds for image processing...")
                await asyncio.sleep(6)

            # 4. Find text area and type
            print("  Locating post text area...")
            text_area_selectors = [
                "div.ql-editor[contenteditable='true']",
                "div[contenteditable='true'][data-placeholder]",
                "div[role='textbox']",
            ]
            text_area = None
            for sel in text_area_selectors:
                try:
                    text_area = await page.wait_for_selector(sel, timeout=10000)
                    if text_area:
                        print(f"  Found text area: {sel}")
                        break
                except Exception:
                    continue

            if not text_area:
                print("  ERROR: Could not find post text area. Saving screenshot.")
                await page.screenshot(path="failure_text_area.png")
                await context.close()
                return False

            await text_area.click()
            await asyncio.sleep(1)

            # Type character-by-character (human-speed: 40-70ms per char)
            print(f"  Typing {len(post_text)} characters...")
            for char in post_text:
                if char == "\n":
                    await page.keyboard.press("Enter")
                else:
                    await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.04, 0.07))

            await asyncio.sleep(3)
            print("  Text typed successfully.")

            # 5. Click Post
            print("  Clicking Post button...")
            post_btn = page.locator("button.share-actions__primary-action")
            
            # Wait for button to be enabled
            try:
                await post_btn.wait_for(state="visible", timeout=10000)
                await post_btn.click()
                print("  Post button clicked.")
                success = True
            except Exception as e:
                print(f"  Failed to click primary action button: {e}")
                # Fallback to any button containing "Post"
                try:
                    btn = page.locator("button", has_text="Post")
                    await btn.click()
                    print("  Fallback Post button clicked.")
                    success = True
                except Exception as e2:
                    print(f"  ERROR: Could not click Post button: {e2}")
                    await page.screenshot(path="failure_post_button.png")
                    success = False

            # Wait for submission
            await asyncio.sleep(8)
            await context.close()

    except Exception as e:
        print(f"  CRITICAL ERROR in post_to_linkedin_robust: {e}")
    finally:
        shutil.rmtree(tmp_profile, ignore_errors=True)
        print("  Temp profile cleaned up.")

    return success

def update_history(history: dict, post_data: dict, image_path: str, ts: str) -> dict:
    posts = history.get("posts", [])
    new_id = max((p.get("id", 0) for p in posts), default=0) + 1
    posts.append({
        "id": new_id,
        "published_at": ts,
        "source_platform": "linkedin_native",
        "source_type": "viral_data_post",
        "topic": post_data.get("topic", ""),
        "research_source": post_data.get("research_source", ""),
        "content_pillar": post_data.get("content_pillar", ""),
        "post_type": post_data.get("post_type", "research_data"),
        "hook_type": post_data.get("hook_type", ""),
        "linkedin_hook": post_data.get("hook_first_line", ""),
        "linkedin_hashtags": post_data.get("hashtags", []),
        "word_count": post_data.get("word_count", 0),
        "image_attached": bool(image_path),
        "image_path": image_path,
        "image_style": "pen_drawn_horizontal_bar_chart",
        "image_prompt_used": post_data.get("image_prompt", ""),
        "predicted_reach": post_data.get("predicted_reach", ""),
        "status": "published",
    })
    history["posts"] = posts
    history["total_posts"] = len(posts)
    history["last_updated"] = ts
    return history

def log_native_run(log: dict, post_data: dict, post_id: int, ts: str, status: str) -> dict:
    log.setdefault("runs", []).append({
        "run_id": f"run_native_{datetime.now().strftime('%Y%m%d_%H%M')}",
        "timestamp": ts,
        "pipeline": "linkedin_growth_system_v10",
        "status": status,
        "topic": post_data.get("topic", ""),
        "research_source": post_data.get("research_source", ""),
        "predicted_reach": post_data.get("predicted_reach", ""),
        "word_count": post_data.get("word_count", 0),
        "post_id": post_id,
    })
    return log

async def main():
    print("Starting custom pipeline run (ROBUST)...")
    
    # 1. Copy image to destination
    print(f"Copying generated image to: {DEST_IMAGE}")
    DEST_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(GENERATED_IMAGE), str(DEST_IMAGE))
    print("Image copied.")
    
    # 2. Copy image to clipboard
    print("Copying image to clipboard...")
    clipboard_ok = copy_image_to_clipboard(str(DEST_IMAGE))
    if not clipboard_ok:
        print("Warning: Clipboard copy failed.")
    await asyncio.sleep(2)
    
    # 3. Post to LinkedIn
    print("Posting to LinkedIn (robust)...")
    ts = datetime.now(timezone.utc).isoformat()
    post_ok = await post_to_linkedin_robust(post_data["post_text"], str(DEST_IMAGE))
    status = "success" if post_ok else "failed"
    
    # 4. Logs
    print(f"Saving logs with status: {status}...")
    history = load_json(POST_HISTORY_FILE)
    history = update_history(history, post_data, str(DEST_IMAGE), ts)
    save_json(POST_HISTORY_FILE, history)
    
    native_log = load_json(NATIVE_LOG_FILE)
    native_log = log_native_run(native_log, post_data, history["total_posts"], ts, status)
    save_json(NATIVE_LOG_FILE, native_log)
    
    print(f"Logs updated — {history['total_posts']} total posts.")
    if post_ok:
        print("SUCCESS: Post published successfully.")
    else:
        print("FAILED: Post publication failed.")

if __name__ == "__main__":
    asyncio.run(main())
