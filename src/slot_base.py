from abc import ABC, abstractmethod
from typing import Set, Tuple

_SLOT = Tuple[str, str, str]  # date, time, location

class BaseSlotParser(ABC):
    @abstractmethod
    async def login(self, page) -> None:
        """Perform portal login with credentials (and TOTP if needed)."""

    @abstractmethod
    async def fetch_slots(self, page) -> Set[_SLOT]:
        """Navigate to booking page and return current available slots as set of tuples."""
