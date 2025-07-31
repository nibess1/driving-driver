import asyncio
import random
from playwright.async_api import async_playwright
from .config import settings
from loguru import logger

USER_AGENTS = [
    # a few realistic user agents; could be extended or randomized from a list
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko)",
]


from playwright.async_api import async_playwright
# ...

class BrowserSession:
    def __init__(self, headless: bool = True, browser_name: str = "firefox"):
        self.headless = headless
        self.browser_name = browser_name.lower()
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        if self.browser_name == "firefox":
            self.browser = await self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_name == "webkit":
            self.browser = await self.playwright.webkit.launch(headless=self.headless)
        else:
            self.browser = await self.playwright.chromium.launch(headless=self.headless)

        user_agent = random.choice(USER_AGENTS)
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": random.randint(1000, 1400), "height": random.randint(700, 1000)},
        )
        self.page = await self.context.new_page()
        await self._stealth()
        return self


    async def _stealth(self):
        # Simplified stealth: random delays, etc. You can integrate playwright-stealth if installed.
        await self.page.add_init_script("""() => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        }""")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
