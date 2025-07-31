from prometheus_client import start_http_server, Gauge
from .config import settings

last_run = Gauge("slot_watcher_last_run_timestamp", "Unix timestamp of last run")
scrape_duration = Gauge("slot_watcher_scrape_duration_seconds", "Duration of the slot scraping")
new_slots_found = Gauge("slot_watcher_new_slots_found", "Number of new slots detected")
failures_total = Gauge("slot_watcher_failures_total", "Total failure count")
