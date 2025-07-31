import sys
from loguru import logger
from .config import settings

def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="{time:ISO8601} | {level} | {message}",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        rotation="10 MB",
        retention="7 days",
        serialize=False,  # switch to True for JSON if desired
    )
