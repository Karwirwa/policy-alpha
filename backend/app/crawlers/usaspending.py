from __future__ import annotations
from typing import List, Any, Dict

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


class USASpendingCrawler(BaseCrawler):
    """Stub crawler for USASpending / US procurement data sources.

    This is a lightweight stub that returns empty discovery results. Implement
    API calls and parsing for USASpending (or SAM.gov) as needed.
    """

    TARGET = "https://www.usaspending.gov/"

    def discover(self) -> List[Dict[str, Any]]:
        return []

    def download(self, doc: Dict[str, Any]) -> bytes:
        return b""

    def parse(self, content: bytes) -> Dict[str, Any]:
        return {}

    def normalize(self, parsed: Dict[str, Any]) -> Any:
        return {}
