import random
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from .config import settings
from .state import StateStore
from .notifier import TelegramNotifier
from .metrics import last_run, scrape_duration, new_slots_found, failures_total
from .browser import BrowserSession
from .slot_base import BaseSlotParser
import time

class Orchestrator:
    def __init__(self, slot_parser: BaseSlotParser):
        self.state = StateStore(settings.state_file)
        self.notifier = TelegramNotifier()
        self.parser = slot_parser
        self.scheduler = AsyncIOScheduler()
        self.backoff_base = 2

    async def run_once(self):
        start = time.time()
        last_run.set_to_current_time()
        try:
            async with BrowserSession(headless=settings.headless) as browser:
                page = browser.page
                await self.parser.login(page)
                fresh_slots = await self.parser.fetch_slots(page)
                new = self.state.diff_and_update(fresh_slots)
                new_slots_found.set(len(new))
                if new:
                    # format for human-readable message
                    formatted = [f"{d} {t} @ {loc}" for (d, t, loc) in new]
                    self.notifier.send_slots(formatted)
        except Exception as e:
            failures_total.inc()
            logger.exception("Error during run: %s", e)
        finally:
            duration = time.time() - start
            scrape_duration.set(duration)
            logger.info("Run completed in %.2f seconds", duration)

    def start_daemon(self):
        # schedule with jitter between min/max
        def schedule_next():
            interval = random.randint(settings.poll_min_seconds, settings.poll_max_seconds)
            return IntervalTrigger(seconds=interval)

        # APScheduler doesn't support variable interval per run natively; we schedule every min and inside jitter sleep
        self.scheduler.add_job(
            lambda: asyncio.create_task(self._wrapper_with_jitter()),
            trigger="interval",
            seconds=settings.poll_min_seconds,
            id="slot_check",
            replace_existing=True,
        )
        self.scheduler.start()

    async def _wrapper_with_jitter(self):
        jitter = random.uniform(0, settings.poll_max_seconds - settings.poll_min_seconds)
        await asyncio.sleep(jitter)
        await self.run_once()
