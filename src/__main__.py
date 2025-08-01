# __main__.py
import argparse
import time
import traceback
import random
from loguru import logger

from config import settings
from logger import setup_logging
from metrics import start_http_server
from notifier import TelegramNotifier
from CDCwebsite import CDCWebsitePlaywright, Types


def sleep_randomish(min_s: int, max_s: int):
    wait = random.randint(min_s, max_s)
    logger.info(f"Sleeping for {wait}s…")
    time.sleep(wait)


def main():
    # Initialize logging
    setup_logging()
    parser = argparse.ArgumentParser(description="Driving lesson slot watcher")
    parser.add_argument("--once", action="store_true", help="Run a single check and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--headful", action="store_true", help="Show browser window")
    parser.add_argument("--no-metrics", action="store_true", help="Disable metrics HTTP server")
    args = parser.parse_args()

    # Override headless mode based on CLI
    settings.headless = not args.headful  # type: ignore

    # Start metrics if enabled
    if settings.enable_metrics and not args.no_metrics:
        start_http_server(8000)
        logger.info("Prometheus metrics exposed on :8000")

    # Telegram notifier
    notifier = None
    if hasattr(settings, 'tg_bot_token') and settings.tg_bot_token and settings.tg_chat_id:
        notifier = TelegramNotifier(
            token=settings.tg_bot_token,
            chat_id=settings.tg_chat_id,
        )
        notifier.send_message("Starting CDC slot watcher...")

    # Use the CDCWebsitePlaywright scraper
    with CDCWebsitePlaywright() as cdc:
        cdc.open_home_website()
        cdc.login()

        def run_cycle():
            try:
                cdc.open_booking_overview()
                cdc.open_practical_lessons_booking(type=Types.PRACTICAL)
                cnt = cdc.get_session_available_count()
                sessions = cdc.get_available_sessions()
                logger.info(f"Available slots: {cnt} → {sessions}")
                if notifier and cnt > 0:
                    notifier.send_message(f"Available slots: {cnt}")
                    notifier.send_message(f"Sessions: {sessions}")
            except Exception:
                logger.exception("Error during slot check")

        # Single run and exit
        if args.once:
            run_cycle()
            return

        # Continuous run
        if args.daemon:
            while True:
                run_cycle()
                sleep_randomish(settings.poll_min_seconds, settings.poll_max_seconds)
        else:
            # Default: single cycle
            run_cycle()


if __name__ == "__main__":
    main()
