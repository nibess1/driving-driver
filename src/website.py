import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pathlib import Path
import random
import stealth
import nodriver as uc


load_dotenv()
#load up user details
PROFILE_PATH = str(Path.home() / os.getenv("PROFILE_PATH"))
VIEWPORT = {
    "width":  int(os.getenv("VIEWPORT_WIDTH",  1920)),
    "height": int(os.getenv("VIEWPORT_HEIGHT", 1080))
}

MARGIN_PCT = 0.1  # 10% margin from each edge

class CDCWebsite:

    def __init__(self):
        w, h = VIEWPORT["width"], VIEWPORT["height"]
        min_x, max_x = w * MARGIN_PCT, w * (1 - MARGIN_PCT)
        min_y, max_y = h * MARGIN_PCT, h * (1 - MARGIN_PCT)
        # pick a random start within the central 80% of the screen
        self.current_pos = (
            random.uniform(min_x, max_x),
            random.uniform(min_y, max_y)
        )



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


    
    def load_web_page(self):
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

            url = "http://www.cdc.com.sg"
            # simulate thinking…
            self.current_pos = stealth.human_wait(page, 3, current_pos=self.current_pos)
            # navigate:
            page.goto(url)

            # 4) Wait for full load (including images, fonts, etc.)
            page.wait_for_load_state("networkidle")
            self.current_pos = stealth.human_wait(page, 2, current_pos=self.current_pos)

            # 8) Final read / print
            print("Final URL:", page.url)
            print("Page title:", page.title())

