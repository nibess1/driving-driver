import orjson
import threading
from pathlib import Path
from typing import Set, Tuple
from .config import settings

_SLOT = Tuple[str, str, str]  # e.g., (date, time, location) or extend as needed

class StateStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.slots: Set[_SLOT] = set()
        self._load()

    def _load(self):
        if self.path.exists():
            raw = self.path.read_bytes()
            try:
                data = orjson.loads(raw)
                self.slots = set(tuple(item) for item in data.get("slots", []))
            except Exception:
                self.slots = set()

    def persist(self):
        with self.lock:
            payload = {"slots": [list(s) for s in self.slots]}
            self.path.write_bytes(orjson.dumps(payload))

    def diff_and_update(self, fresh: Set[_SLOT]) -> Set[_SLOT]:
        with self.lock:
            new = fresh - self.slots
            if new:
                self.slots |= new
                self.persist()
            return new

    def reset(self):
        with self.lock:
            self.slots = set()
            self.persist()
