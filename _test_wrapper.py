"""Full traceback test."""
import traceback
from langchain_ollama import ChatOllama
from browser_use import Agent, BrowserProfile

class ChatOllamaCompat(ChatOllama):
    provider: str = "ollama"
    
    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            if "has no field" in str(e):
                print(f"[BLOCKED SETATTR] name={name}, value_type={type(value).__name__}")
                traceback.print_stack()
                # Store it as object attribute instead
                object.__setattr__(self, name, value)
            else:
                raise

llm = ChatOllamaCompat(
    model="qwen2.5:7b",
    temperature=0.3,
    num_ctx=4096,
    num_predict=256,
    repeat_penalty=1.1,
)

profile = BrowserProfile(headless=True)
try:
    agent = Agent(task="test", llm=llm, browser_profile=profile, max_failures=1, use_vision=False, generate_gif=False)
    print("Agent created successfully!")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    traceback.print_exc()
