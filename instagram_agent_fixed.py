import asyncio
import inspect
from pathlib import Path
from browser_use import Agent, Browser, BrowserProfile, Controller
from langchain_ollama import ChatOllama
from pydantic import BaseModel

controller = Controller()

class EmptyInput(BaseModel):
    pass

class UrlInput(BaseModel):
    url: str

@controller.action("Navigate to thevibefounder Instagram profile")
async def navigate_to_insta(params: EmptyInput, browser) -> str:
    page = await browser.get_current_page()
    await page.goto("https://www.instagram.com/thevibefounder/", wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(4)
    return "Navigated to thevibefounder profile."

@controller.action("Find and return the latest post URL from the profile grid")
async def get_latest_post(params: EmptyInput, browser) -> str:
    page = await browser.get_current_page()
    post_links = await page.locator('a[href*="/p/"], a[href*="/reel/"]').all()
    for link in post_links:
        href = await link.get_attribute("href")
        if href and ("/p/" in href or "/reel/" in href):
            latest_url = "https://www.instagram.com" + href
            return f"Latest post URL is: {latest_url}"
    return "Could not find any post URLs."

@controller.action("Navigate to a post URL and extract its caption text")
async def extract_caption(params: UrlInput, browser) -> str:
    page = await browser.get_current_page()
    await page.goto(params.url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(4)
    try:
        caption = await page.locator('article h1, article span[dir="auto"]').first.inner_text()
    except:
        try:
            caption = await page.locator('article').first.inner_text()
        except:
            caption = await page.inner_text("body")
            
    with open("insta_post.txt", "w", encoding="utf-8") as f:
        f.write(f"URL: {params.url}\n\n{caption}")
        
    return f"Caption extracted and saved to insta_post.txt: {caption[:100]}..."

async def main():
    CHROME_PROFILE = Path("data-tracking/chrome-profile")
    
    profile = BrowserProfile(
        user_data_dir=str(CHROME_PROFILE.resolve()),
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--start-maximized",
        ]
    )
    browser = Browser(browser_profile=profile)
    
    class ChatOllamaWithProvider(ChatOllama):
        model_config = {'extra': 'allow'}
        provider: str = 'ollama'

    llm = ChatOllamaWithProvider(
        model="qwen2.5:7b",
        temperature=0.1,
        num_ctx=4096,
        num_predict=512,
        repeat_penalty=1.1,
    )
    llm.model_name = "qwen2.5:7b"
    
    task = """
    You are an Instagram extraction agent.
    1. Call 'navigate_to_insta' to go to the profile.
    2. Call 'get_latest_post' to get the URL of the most recent post.
    3. Call 'extract_caption' with the URL you found to get the caption and save it.
    4. Once the caption is extracted and saved, you are done.
    """
    
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        controller=controller,
        max_failures=3,
        use_vision=False
    )
    
    print("Starting Fixed Instagram Browser Agent...")
    try:
        await agent.run()
        print("Agent finished successfully.")
    except Exception as e:
        print(f"Agent crashed: {e}")
    finally:
        # Give user time to see
        await asyncio.sleep(3)
        close_method = getattr(browser, "close", None) or getattr(browser, "aclose", None)
        if close_method:
            close_result = close_method()
            if inspect.isawaitable(close_result):
                await close_result
        else:
            get_context = getattr(browser, "get_context", None)
            if get_context:
                context = await get_context()
                context_close = getattr(context, "close", None) or getattr(context, "aclose", None)
                if context_close:
                    context_close_result = context_close()
                    if inspect.isawaitable(context_close_result):
                        await context_close_result

if __name__ == "__main__":
    asyncio.run(main())
