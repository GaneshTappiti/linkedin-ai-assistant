import asyncio
import os
import inspect
from pathlib import Path
from browser_use import Agent, Browser, BrowserProfile
from langchain_ollama import ChatOllama

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
        ],
        disable_security=False,
        keep_alive=True,
        wait_between_actions=1.5,
        minimum_wait_page_load_time=3.0,
        wait_for_network_idle_page_load_time=3.0
    )
    
    browser = Browser(browser_profile=profile)
    
    class ChatOllamaWithProvider(ChatOllama):
        model_config = {'extra': 'allow'}
        provider: str = 'ollama'

    llm = ChatOllamaWithProvider(
        model="qwen2.5:7b",
        temperature=0.3,
        num_ctx=4096,
        num_predict=512,
        repeat_penalty=1.1,
    )
    llm.model_name = "qwen2.5:7b"
    
    task = """
    1. Navigate directly to https://www.instagram.com/thevibefounder/
    2. Wait for the page to load, then click on the first post/reel in the grid (it should be the most recent one).
    3. Read the caption/text of the post carefully.
    4. Save the full caption text to a file named "latest_insta_post.txt".
    5. After saving the text to the file, finish the task.
    """
    
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        max_failures=3,
        max_actions_per_step=3,
        use_vision=False
    )
    
    print("Starting Instagram browser agent...")
    try:
        await agent.run()
        print("Agent finished execution.")
    except Exception as e:
        print(f"Agent crashed: {e}")
    finally:
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
