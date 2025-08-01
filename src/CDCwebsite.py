import time
import base64
import traceback

from playwright.sync_api import sync_playwright, TimeoutError
from playwright_stealth import stealth_sync
from config import settings
import captcha


class Types:
    PRACTICAL     = "practical"
    ROAD_REVISION = "rr"
    BTT           = "btt"
    RTT           = "rtt"
    PT            = "pt"


class CDCWebsitePlaywright:
    def __init__(self):
        # Load credentials and behavior from config
        self.username     = settings.portal_user
        self.password     = settings.portal_pass.get_secret_value()
        self.home_url     = getattr(settings, 'home_url', "https://www.cdc.com.sg")
        self.booking_url  = getattr(settings, 'booking_url', "https://www.cdc.com.sg:8080")
        self.is_test      = getattr(settings, 'is_test', False)
        # timeouts in ms
        self.timeout      = settings.poll_max_seconds * 1000

        self.playwright = None
        self.browser    = None
        self.context    = None
        self.page       = None

    def __enter__(self):
        # Start Playwright
        self.playwright = sync_playwright().start()
        # Launch Chromium with stealth flags
        self.browser = self.playwright.chromium.launch(
            headless=settings.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
            ]
        )
        # Create isolated context with realistic fingerprint
        self.context = self.browser.new_context(
            viewport={ 'width': 1600, 'height': 768 },
            user_agent=self._spoof_user_agent(),
            locale=settings.locale or 'en-US',
            timezone_id=settings.timezone_id or 'Asia/Singapore',
            java_script_enabled=True,
        )
        stealth_sync(self.context)
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except Exception:
            pass

    def _spoof_user_agent(self):
        # Pull from config or fallback
        return getattr(
            settings,
            'user_agent',
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )

    def _open(self, url: str):
        self.page.goto(url)

    def open_home_website(self):
        self._open(f"{self.home_url}/#login")

    def login(self):
        # Wait for login form
        self.page.wait_for_selector("#userId_4", state='visible', timeout=self.timeout)
        self.page.fill("#userId_4", self.username)
        self.page.fill("#password_4", self.password)
        # Wait for recaptcha resolution
        try:
            self.page.wait_for_selector("#userId_4", state='detached', timeout=settings.recaptcha_timeout)
        except TimeoutError:
            print("Recaptcha not solved in time—continue manually.")
        time.sleep(settings.post_captcha_pause)

    def logout(self):
        self._open(f"{self.booking_url}/NewPortal/logOut.aspx?PageName=Logout")

    def open_booking_overview(self):
        self._open(f"{self.booking_url}/NewPortal/Booking/StatementBooking.aspx")

    def open_practical_lessons_booking(self, type=Types.PRACTICAL):
        self._open(f"{self.booking_url}/NewPortal/Booking/BookingPL.aspx")
        while True:
            txt = self.page.text_content("#ctl00_ContentPlaceHolder1_lblSessionNo") or ""
            if txt.strip():
                break
            # Select appropriate course
            sel = self.page.locator("#ctl00_ContentPlaceHolder1_ddlCourse")
            opts = sel.locator('option').all()
            idx = getattr(settings, 'course_index', None) or 1
            names = [opt.text_content().strip() for opt in opts]
            for i, name in enumerate(names):
                if getattr(settings, 'course_keyword', 'Class 2B Lesson') in name:
                    idx = i
            if len(opts) > 2:
                print(f"Options {names}, choosing {names[idx]}")
            sel.select_option(index=idx)

            # CAPTCHA loop
            try:
                img = self.page.wait_for_selector("#ctl00_ContentPlaceHolder1_CaptchaImg", timeout=settings.captcha_timeout)
                b64 = img.get_attribute('src').split(',')[1]
                with open('captcha_tmp.png','wb') as f:
                    f.write(base64.b64decode(b64))
                code = captcha.resolve_3('captcha_tmp.png')
                print(f"captcha: {code}")
                self.page.fill("#ctl00_ContentPlaceHolder1_txtVerificationCode", code)
                self.page.click("#ctl00_ContentPlaceHolder1_Button1")
                time.sleep(settings.post_captcha_pause)
            except Exception:
                traceback.print_exc()
        # Ensure availability label is visible
        self.page.wait_for_selector("#ctl00_ContentPlaceHolder1_lblSessionNo", state='visible', timeout=self.timeout)

    def get_session_available_count(self):
        return int(self.page.text_content("#ctl00_ContentPlaceHolder1_lblSessionNo").strip())

    def _get_all_session_dates(self):
        times, days = [], []
        rows = self.page.locator("table#ctl00_ContentPlaceHolder1_gvLatestav tr").all()
        for r in rows:
            for i, h in enumerate(r.locator('th').all()):
                if i < 2: continue
                times.append(h.text_content().split("\n")[1])
            tds = r.locator('td').all()
            if tds:
                days.append(tds[0].text_content().strip())
        return days, times

    def get_available_sessions(self):
        sessions = {}
        days, times = self._get_all_session_dates()
        for inp in self.page.locator('input').all():
            src = inp.get_attribute('src') or ''
            if 'Images1.gif' in src or 'Images3.gif' in src:
                eid = inp.get_attribute('id')
                row = int(eid.split('_')[3][-1]) - 2
                col = int(eid[-1]) - 1
                sessions.setdefault(days[row], []).append(times[col])
        return sessions

    def wait_clickable(self, selector: str, timeout: int = None):
        return self.page.wait_for_selector(
            selector,
            state='visible',
            timeout=timeout or self.timeout
        )
