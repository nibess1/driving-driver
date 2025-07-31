
## 1  Functional Requirements

| ID   | Requirement                                                                                                                                                  |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| F-1  | Authenticate to the driving-lesson portal with stored credentials (username + password, and optional OTP/TOTP code if the portal supports it).               |
| F-2  | Navigate to the “Book / Reschedule lesson” page and load the calendar or timeslot table.                                                                     |
| F-3  | Parse the DOM (not raw HTML text) to extract **all** open slots (date, time, location, instructor, etc.).                                                    |
| F-4  | Persist the last-seen slot set (e.g., in an SQLite DB or local JSON).                                                                                        |
| F-5  | Compare the freshly scraped slots with the persisted set; detect *only* newly opened slots.                                                                  |
| F-6  | When ≥ 1 new slot is found, send a Telegram message via a Bot to a configured chat-ID, including a deep link or clear instructions to book manually.         |
| F-7  | Run the refresh check on a configurable schedule (default: every 2–4 min with ±30 sec jitter).                                                               |
| F-8  | Gracefully handle portal outages, login failures, CAPTCHA/queue pages, and rate-limit responses; retry with exponential back-off up to *N* attempts/session. |
| F-9  | Provide CLI options: `--once`, `--daemon`, `--headful` (visible browser) and `--headless` (default).                                                         |
| F-10 | Expose Prometheus-ready metrics (last-run, scrape-time, failures, new-slots-found) on `localhost:8000/metrics` when `--metrics` is enabled.                  |

---

## 2  Non-Functional Requirements

| Category      | Requirement                                                                                                                                          |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stealth       | Minimise bot-footprint: randomised user-agent, viewport size, and think-time; obey robots.txt if present; never flood with > 30 requests per minute. |
| Reliability   | Mean Time Between Failures ≥ 7 days. Automatic re-login when session expires.                                                                        |
| Idempotency   | Never send duplicate Telegram alerts for the same slot.                                                                                              |
| Observability | Structured JSON logging + rotating log files; log levels `INFO` (default) & `DEBUG`.                                                                 |
| Security      | Credentials stored in a `.env` / OS secrets manager; never logged.                                                                                   |
| Portability   | Runs on Linux, macOS, and Windows with Python 3.10+.                                                                                                 |
| Extensibility | Slot detection logic isolated in a module so new portals can be supported by subclassing.                                                            |
| Compliance    | Must respect the portal’s Terms of Service; configurable minimum poll interval.                                                                      |
| Resource Use  | CPU < 5 % average on a t3.micro; memory < 300 MB in steady state.                                                                                    |

---

## 3  Environment & Dependencies

```text
python >= 3.10
playwright==1.*          # Chromium/Firefox/WebKit drivers
playwright-stealth==1.*  # Evasion helpers
python-telegram-bot==20.*
APScheduler==3.*
python-dotenv==1.*
pydantic==2.*            # typed settings & data models
orjson==3.*              # fast JSON for logs/state
prometheus-client==0.*   # optional metrics
```

*Install Playwright browsers once with* `playwright install chromium`.

---

## 4  Configuration (example `.env`)

```ini
# Portal creds
PORTAL_USER=alice@example.com
PORTAL_PASS=super-secret-pw

# For TOTP (if needed)
PORTAL_TOTP_SECRET=JBSWY3DPEHPK3PXP

# Telegram
TG_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TG_CHAT_ID=987654321

# Scheduler
POLL_MIN_SECONDS=120
POLL_MAX_SECONDS=240

# Misc
HEADLESS=true
```

---

## 5  High-Level Architecture

```
 ┌────────────┐     fetch DOM      ┌────────────┐
 │Scheduler / │ ─────────────────► │Browser     │
 │APScheduler │                    │(Playwright)│
 └─────┬──────┘                    └─────┬──────┘
       │                              parse
       │ new slots                     │
       ▼                              ▼
 ┌────────────┐  diff + persist  ┌────────────┐
 │State Store │◄─────────────────│Slot Parser │
 │(SQLite/JSON)                   └─────┬──────┘
 └────────────┘                        │ new
                                       ▼
                                 ┌────────────┐
                                 │Notifier    │
                                 │(Telegram)  │
                                 └────────────┘
```

---

## 6  Key Implementation Notes

1. **Browser automation** – Use Playwright’s Chromium driver with [stealth](https://github.com/requireCool/playwright-stealth) features; randomise viewport & delay every click / navigation event.
2. **CAPTCHA / queue handling** – Detect common challenge pages; pause, alert user (optional), and retry later rather than attempting to solve.
3. **Deep link** – Some portals accept pre-filled query parameters. If available, include them in the Telegram message (`https://portal.example.com/book?date=2025-08-14&slot=09%3A00`).
4. **Persistence layer** – Store a hash of each (date, time, location) tuple; on each run compare versus stored set; clear state on manual reset command.
5. **Telegram bot rate-limit** – Telegram allows 30 msgs/sec overall; we send max 1 msg/run + aggregated slot list.
6. **Docker support** – Provide an optional `Dockerfile` and `docker-compose.yml` with healthcheck (`curl -f localhost:8000/metrics`).
7. **CI** – Include unit tests (pytest) and GitHub Actions workflow to run `pytest`, `ruff`, and `mypy`.

---

## 7  Security & Compliance Checklist

* ✅ Use HTTPS exclusively; verify SSL certs.
* ✅ Store secrets in environment variables or an OS-level secrets manager (not git).
* ✅ Respect `robots.txt` crawl delay (if declared).
* ✅ Include a *single* manual step (the actual booking click) so the pipeline merely *notifies* — reducing risk of violating “no bots” clauses.
