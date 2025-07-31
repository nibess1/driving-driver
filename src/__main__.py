import argparse
import asyncio
from .config import settings
from .logger import setup_logging
from .scheduler import Orchestrator
from .metrics import start_http_server
from loguru import logger

# Placeholder: user must supply their own concrete parser implementation
from .slot_base import BaseSlotParser

class DummyParser(BaseSlotParser):
    async def login(self, page):
        logger.info("Dummy login (replace with real logic)")

    async def fetch_slots(self, page):
        # simulate getting one slot
        return {("2025-08-14", "09:00", "Central Office")}


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Driving lesson slot watcher")
    parser.add_argument("--once", action="store_true", help="Run a single check and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--headful", action="store_true", help="Show browser window")
    parser.add_argument("--no-metrics", action="store_true", help="Disable metrics HTTP server")
    args = parser.parse_args()

    # override headless if headful requested
    settings.headless = not args.headful  # type: ignore

    if settings.enable_metrics and not args.no_metrics:
        start_http_server(8000)
        logger.info("Prometheus metrics exposed on :8000")

    orchestrator = Orchestrator(slot_parser=DummyParser())

    async def runner():
        if args.once:
            await orchestrator.run_once()
        elif args.daemon:
            orchestrator.start_daemon()
            # keep alive
            while True:
                await asyncio.sleep(60)
        else:
            # default: run once
            await orchestrator.run_once()

    asyncio.run(runner())


if __name__ == "__main__":
    main()
