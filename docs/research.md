Thanks! I’ll find the best Python-based automation libraries and techniques to stealthily log in to [https://www.cdc.com.sg/](https://www.cdc.com.sg/), navigate to the driving lessons booking page, and refresh every minute with slight timing variation. I’ll also look into captcha handling strategies and extracting date/time slot data once available.

I’ll be back shortly with the best tools and example implementation guidance.


# Stealthy Browser Automation for CDC Slot Availability

Setting up a script to log in and monitor **ComfortDelGro Driving Centre (CDC)** slot availability requires careful handling of bot-detection measures. Below we outline **the latest stealth automation libraries** and best practices to make your Python script as undetectable as possible. The script can run with a visible browser window (headed mode) for reliability, refreshing the target page about every 1 minute (with some randomized jitter).

## 1. Choose a Stealth Automation Library (Python)

To avoid detection, use a browser automation tool that mimics real user behavior. Two top choices in 2025 are:

* **Playwright with Stealth Plugin** – Modern browser automation by Microsoft, augmented with a stealth plugin to mask automation fingerprints.
* **Undetected ChromeDriver (Selenium)** – A customized Selenium ChromeDriver that modifies browser properties to evade anti-bot scripts.

Both approaches have **high success rates (≈92–95%)** against anti-bot systems. They handle tasks like disabling the `navigator.webdriver` flag and other clues that sites use to identify bots. Below we discuss each in detail.

## 2. Playwright + Stealth Plugin (Highly Stealthy)

Playwright is a robust, up-to-date automation library, and adding the **`playwright-stealth`** plugin helps it evade bot detection:

* **How it works:** The stealth plugin *masks Playwright’s built-in identifiers*, overriding certain default browser APIs so the automation appears more genuine. For example, it removes the `HeadlessChrome` traces and ensures `navigator.webdriver` is false, so detection scripts think it's a regular browser. After applying the plugin, tests show the browser is no longer flagged as headless or automated.

* **Installation:** Use pip to install both Playwright and the stealth plugin:

  ```bash
  pip install playwright  playwright-stealth
  ```

  \**(Playwright's first use will require an extra step to install browser binaries via `playwright install`.)*

* **Usage (Python):** You can use either async or sync API. For simplicity, here's an **async** example with stealth:

  ```python
  import asyncio
  from playwright.async_api import async_playwright
  from playwright_stealth import stealth_async

  async def monitor_slots():
      async with async_playwright() as p:
          # Launch browser in headed mode (visible window)
          browser = await p.chromium.launch(headless=False)  
          page = await browser.new_page()
          await stealth_async(page)  # Apply stealth plugin to mask automation:contentReference[oaicite:8]{index=8}

          # Log in to the site
          await page.goto("https://www.cdc.com.sg/login")
          # ... (code to fill username/password and submit, handle CAPTCHA if prompted)

          # Navigate to the slots page after login
          await page.goto("https://www.cdc.com.sg/slots")  
          print("Logged in. Starting slot monitoring...")

          # Periodically refresh and check for availability
          import random, time
          while True:
              # Example check: look for an element or text that indicates an available slot
              content = await page.content()
              if "No slots available" not in content:
                  print("🚗🎉 A slot just opened up!")
                  # (Optionally, add code to notify or break out)
              # Wait ~60s with jitter before next refresh
              await asyncio.sleep(60 + random.uniform(-5, 5))
              await page.reload()  # refresh the page
  asyncio.run(monitor_slots())
  ```

  **Sync API:** If you prefer synchronous code, Playwright offers a sync variant. In that case, use `from playwright.sync_api import sync_playwright` and `from playwright_stealth import stealth_sync`, then call `stealth_sync(page)` on a new page. The rest of the logic remains similar.

* **Why Playwright Stealth?** It’s actively maintained and *designed to fool advanced detectors*. It can intercept network requests, control timing, and supports plugins for proxies or CAPTCHA solving if needed. Many anti-bot systems specifically target Selenium, so Playwright with stealth is a fresh alternative.

**Sources:** Playwright Stealth plugin adapts the Puppeteer stealth techniques to Playwright, masking identifiable browser attributes. By overriding default automation configurations, it prevents websites from flagging your script as a bot. This yields a high success rate in evading detection, as evidenced by test pages recognizing it as a non-automation browser.

## 3. Undetected ChromeDriver (Selenium-Based Option)

If you prefer Selenium, **undetected-chromedriver** is the go-to for stealth:

* **How it works:** Undetected-ChromeDriver is a drop-in replacement for Selenium’s Chrome WebDriver that *automatically patches many detectable traits*. It creates more **“human-like” browser fingerprints** by modifying or hiding typical Selenium signatures. For example, it disables the `"enable-automation"` flag, removes the Selenium extension, and ensures `navigator.webdriver` is undefined, among other tricks.

* **Installation:**

  ```bash
  pip install undetected-chromedriver
  ```

  *(This will also install Selenium if not already present.)*

* **Basic Usage:** Using undetected-chromedriver is very similar to standard Selenium:

  ```python
  import undetected_chromedriver as uc

  # Launch Chrome with stealth modifications
  driver = uc.Chrome(use_subprocess=False)  # use_subprocess=False helps with stealth:contentReference[oaicite:18]{index=18}

  driver.get("https://www.cdc.com.sg/login")
  # ... (find fields and input credentials, possibly handle CAPTCHA manually)
  driver.get("https://www.cdc.com.sg/slots")
  print("Logged in. Starting slot monitoring...")

  import time, random
  while True:
      page_text = driver.page_source
      if "No slots available" not in page_text:
          print("🚗🎉 A slot is available!")
          # (Optionally trigger an alert/notification here)
      time.sleep(60 + random.uniform(-5, 5))  # 60s +/- 5s jitter
      driver.refresh()
  ```

  This script uses a continuous loop with a 1-minute interval (with some randomness) to reload the page. The **jitter** ensures the refresh isn’t at an exact fixed cadence, which makes the behavior more human-like.

* **Additional Options:** You can further customize `ChromeOptions` if needed – e.g. setting a specific User-Agent string, screen size, or adding a slight delay in page interactions. However, **avoid headless mode** unless necessary. Running with a visible browser is less likely to be flagged, since headless browsers are easier to detect (many anti-bot systems treat headless usage as suspicious). If you must run headless (e.g. on a server), consider using Chrome’s new headless mode (`options.add_argument("--headless=new")`) which is closer to headed behavior.

**Sources:** Undetected-ChromeDriver has been reported to bypass Cloudflare, Imperva, DataDome and other WAF bot checks by patching the driver at runtime. It essentially **fakes being a regular Chrome** by altering the very properties that anti-bot scripts look for. Using it is straightforward – as one StackOverflow example shows, you can simply replace `webdriver.Chrome()` with `undetected_chromedriver.Chrome()` to get a stealth browser instance.

## 4. CAPTCHA Handling for Login

Logging into the CDC website may trigger a CAPTCHA challenge (e.g. reCAPTCHA or a simple verification) to ensure a human is signing in. Stealth techniques will reduce the chance of frequent CAPTCHAs, but you should be prepared to handle them:

* **Manual Solution:** Since your script runs with a real browser window, the simplest approach is to **pause and notify you to solve the CAPTCHA**. For example, after loading the login page, if a CAPTCHA is present, you could use `input("Solve CAPTCHA and press Enter to continue...")` to wait until you manually solve it in the browser, then let the script proceed.

* **Automated Solving:** For full automation, you can integrate third-party CAPTCHA-solving services. Services like **2Captcha** or **AntiCaptcha** take an image or sitekey and return the solved text or token. There are Python APIs available (e.g. `2captcha-python` library). Keep in mind these services cost money and add complexity. Alternatively, some high-end solutions like Bright Data’s **Web Unlocker** include automated CAPTCHA handling with proxy/IP rotation, but these are commercial. Given that speed is not critical here, a reasonable approach is to handle CAPTCHA manually at login and rely on stealth to avoid further challenges during the refresh loop.

* **One-Time Login Session:** To avoid solving CAPTCHAs repeatedly, **reuse the same browser session** for continuous monitoring. Both Playwright and Selenium will maintain cookies/session after the initial login. Don’t call the login page every time; log in once, then keep that browser instance alive while refreshing the slots page. This way, you won’t trigger the login CAPTCHA frequently.

## 5. Best Practices for Stealth and Reliability

In addition to using the right library, keep these tips in mind to maximize stealth:

* **Run in Headed Mode:** As noted, use a visible browser (non-headless) if possible. Headless mode can be detected by certain scripts (e.g., checking for `'HeadlessChrome'` in the user agent or special headless-only properties). If you need background execution, the stealth tools discussed can still help — just ensure to use the latest headless Chrome with proper flags if required.

* **Randomize Timing:** You’re already planning a \~60-second refresh; make it *60 ± a few seconds* to avoid an exact interval pattern. For example, sleep 55–65 seconds randomly. This small jitter makes the traffic pattern less robotic.

* **Mimic Human Interaction:** If the site is very strict, consider adding some human-like behavior:

  * Randomly scroll the page or move the mouse via script between refreshes.
  * Vary the refresh interval further if needed, or take occasional longer breaks.
  * Avoid performing actions *too quickly* (e.g., add a short `await page.wait_for_timeout(1000)` after page loads or before clicking buttons, so it emulates a user reading content). Since speed isn't a priority, err on the side of slower, natural interactions.

* **Use Realistic Headers:** Stealth libraries typically handle this, but ensure the browser uses a common **user-agent string** and has typical settings (languages, platform, etc.). For instance, Selenium Stealth (if used) sets navigator languages, WebGL vendor, and other attributes to mimic a normal Chrome on Windows. These details help maintain a *normal reCAPTCHA score* and pass bot tests. Undetected-Chromedriver and Playwright-stealth already cover most of these, but it’s good to be aware.

* **Monitor Site Responses:** Be mindful of any signs your script is getting flagged (e.g., if the page suddenly redirects to a "verify you are human" step or shows a lot of CAPTCHAs). If that happens, you might need to incorporate proxies or reduce frequency. However, one page load per minute is a low rate, so with the above stealth measures, it should remain under the radar.

## 6. Summary

By using **modern stealth automation tools**, you can log in and check CDC for open driving lesson slots with minimal risk of detection:

* **Playwright + `playwright-stealth`** offers an up-to-date, robust solution that directly tackles Playwright’s detectable traits. It’s a great choice if you want a cutting-edge tool maintained by a big team (Microsoft) and are comfortable with its async Python style or the sync helper API.
* **Undetected ChromeDriver (Selenium)** is a battle-tested option that *augments Selenium’s ChromeDriver to be stealthy*, automatically evading common bot-detection tricks. If you’re familiar with Selenium’s API, this might be the quickest path to implement your script. It has been shown to bypass many WAFs and bot checks out-of-the-box.

Both approaches are valid. **Implement the one you're most comfortable with**, apply the best practices (timing jitter, single login session, etc.), and your script will repeatedly refresh the target page and pull lesson slot availability without drawing attention. With these tools, the automation should appear **“absolutely human”** to CDC’s servers, and you can confidently monitor for that elusive open driving lesson slot!

**Sources:** Research data indicates that Playwright-Extra (with stealth plugins) and Undetected-Chromedriver achieve the highest success rates against anti-bot systems. Playwright Stealth works by masking identifiable automation features of the browser, while Undetected-Chromedriver creates more human-like browser fingerprints to avoid detection. Selenium can also be made stealthy via plugins that adjust its automation footprint. Using these tools, testers have bypassed bot checks that normally trap automated browsers, including Cloudflare and other WAF checks. By integrating such a library and following human-like timing, your monitoring script will remain stealthy and effective. Good luck with your driving lesson slot hunting!
