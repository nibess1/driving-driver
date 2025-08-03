import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pathlib import Path
import random

PROFILE_PATH = str(Path.home() / ".mozilla\Firefox\Profiles\qq7ofcsu.default-release")
class CDCWebsite:

    def example(self):
        with sync_playwright() as p:
            browser = p.firefox.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            headless=False,
            viewport={"width":1920,"height":1080},
            screen={"width":1920,"height":1080},
        )
            page = browser.new_page()
            page.goto("https://example.com")
            print(page.title())


    
    def example_human(self):
        with sync_playwright() as p:
            # 1) Launch your real profile
            context = p.firefox.launch_persistent_context(
                user_data_dir=PROFILE_PATH,
                headless=False,
                viewport={"width": 1920, "height": 1080},
                screen={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            # 2) Spoof normal headers
            page.set_extra_http_headers({
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            })

            # 3) “Type” a URL into the address bar (optional step to mimic typing)
            url = "https://google.com"
            # simulate thinking…
            time.sleep(random.uniform(0.5, 1.5))

            # navigate:
            page.goto(url)

            # 4) Wait for full load (including images, fonts, etc.)
            page.wait_for_load_state("networkidle")

            # 8) Final read / print
            print("Final URL:", page.url)
            print("Page title:", page.title())

            context.close()
