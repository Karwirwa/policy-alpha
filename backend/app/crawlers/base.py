from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Any
import requests
import time
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict

class BaseCrawler(ABC):
    """Abstract base crawler providing helpers and interface."""

    @abstractmethod
    def discover(self) -> List[Any]:
        """Discover recent government documents or notices."""
        raise NotImplementedError

    @abstractmethod
    def download(self, doc: Any) -> bytes:
        """Download the raw content for a discovered doc."""
        raise NotImplementedError

    @abstractmethod
    def parse(self, content: bytes) -> dict:
        """Parse raw content into structured fields."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, parsed: dict) -> Any:
        """Normalize parsed fields into a GovernmentDocument or dict."""
        raise NotImplementedError

    def _fetch_with_retry(self, url: str, max_retries: int = 3, backoff: float = 1.0, verify: bool = True) -> requests.Response:
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.get(url, timeout=15, verify=verify)
                resp.raise_for_status()
                return resp
            except Exception as e:
                last_exc = e
                time.sleep(backoff * attempt)
        raise last_exc

    def _render_with_playwright(self, url: str, wait_for: str | None = None, timeout_ms: int = 15000) -> bytes | None:
        """Render the page using Playwright to execute JavaScript and return the rendered HTML bytes.

        Returns None if Playwright is unavailable or rendering fails.
        """
        try:
            # Import locally so Playwright is optional for environments that don't have it
            from playwright.sync_api import sync_playwright
        except Exception:
            return None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, timeout=timeout_ms)
                if wait_for:
                    try:
                        page.wait_for_selector(wait_for, timeout=timeout_ms)
                    except Exception:
                        # ignore waiting failures, still try to get content
                        pass
                content = page.content()
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass
                return content.encode("utf-8")
        except Exception:
            return None

    def _extract_text_from_html(self, html: str) -> str:
        if BeautifulSoup is None:
            return html
        soup = BeautifulSoup(html, "html.parser")
        texts = soup.stripped_strings
        return "\n".join(texts)

    def _safe_extract(self, data: dict, keys: list, default: str = "") -> str:
        for k in keys:
            if k in data and data[k]:
                return data[k]
        return default
