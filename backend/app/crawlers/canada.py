from __future__ import annotations
from typing import List, Any, Dict
import time
from datetime import datetime, timezone

import requests

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


class CanadaCrawler(BaseCrawler):
    """Crawler for Canadian procurement sources (Buy and Sell / CanadaBuys) (skeleton)."""

    BUY_AND_SELL = "https://buyandsell.gc.ca/tenders"

    def discover(self) -> List[Dict[str, Any]]:
        import logging
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-CA,en;q=0.9',
            }
            params = {'page': 1}
            resp = None
            try:
                resp = self.session.get(self.BUY_AND_SELL, params=params, headers=headers, timeout=getattr(self, 'timeout', 15))
            except Exception:
                resp = None

            html = None
            if resp is not None and getattr(resp, 'status_code', None) == 200:
                html = resp.content
            else:
                logging.warning("BuyAndSell returned %s; attempting Playwright render", getattr(resp, 'status_code', 'no-response'))
                rendered = self._render_with_playwright(self.BUY_AND_SELL)
                if rendered:
                    html = rendered
                else:
                    return []
        except Exception as e:
            import logging as _log
            _log.error("BuyAndSell fetch failed: %s", e)
            return []

        results: List[Dict[str, Any]] = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a.get("href") or ""
                text = (a.get_text() or "").strip()
                if not href or not text:
                    continue
                if "/tenders" in href or "tender" in text.lower():
                    url = href if href.startswith("http") else requests.compat.urljoin(self.BUY_AND_SELL, href)
                    results.append({"id": url, "title": text, "source_url": url})
        except Exception:
            return []

        return results[:30]

    def download(self, doc: Dict[str, Any]) -> bytes:
        url = doc.get("source_url")
        if not url:
            return b""
        try:
            resp = self._fetch_with_retry(url, max_retries=2)
            return resp.content
        except Exception:
            return b""

    def parse(self, content: bytes) -> Dict[str, Any]:
        if not content:
            return {}
        try:
            html = content.decode("utf-8", errors="replace")
        except Exception:
            html = str(content)
        text = self._extract_text_from_html(html)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = lines[0] if lines else None
        description = "\n".join(lines[1:8]) if len(lines) > 1 else None

        reference = None
        ministry = None
        value = None
        location = None
        procurement_type = None
        import re

        # reference
        ref_match = re.search(r"(Reference|Ref(?:erence)?|Tender\s*(No|Number))[:\s]*#?\s*([A-Za-z0-9\-_/]+)", text, flags=re.I)
        if ref_match:
            reference = ref_match.group(3) if ref_match.lastindex and ref_match.lastindex >= 3 else ref_match.group(0)

        # ministry
        min_match = re.search(r"(Ministry|Department|Agency|Branch|Office)[:\s\-]*(.+)", text, flags=re.I)
        if min_match:
            ministry = re.sub(r"<[^>]+>", "", min_match.group(2)).split('\n')[0].strip()

        # value
        val_match = re.search(r"(CAD|CA\$|\$)\s*([0-9,]+(\.[0-9]+)?)", text)
        if val_match:
            value = f"{val_match.group(1)} {val_match.group(2)}"

        # location
        loc_match = re.search(r"(Location|Place of Performance|Region)[:\s]*(.+)", text, flags=re.I)
        if loc_match:
            location = re.sub(r"<[^>]+>", "", loc_match.group(2)).split('\n')[0].strip()

        # procurement type
        type_match = re.search(r"(Procurement Type|Contract Type|Procurement Method)[:\s]*(.+)", text, flags=re.I)
        if type_match:
            procurement_type = re.sub(r"<[^>]+>", "", type_match.group(2)).split('\n')[0].strip()
            procurement_type = re.split(r"(?i)Deadline[:\s]", procurement_type)[0].strip()
            procurement_type = re.split(r"(\d{1,2}\s+\w+\s+\d{4})", procurement_type)[0].strip()

        # date
        m = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", text)
        deadline = None
        if m:
            try:
                from datetime import datetime
                deadline = datetime.strptime(m.group(0), "%d %B %Y").replace(tzinfo=timezone.utc)
            except Exception:
                deadline = None

        return {
            "title": title,
            "reference": reference,
            "ministry": ministry,
            "value": value,
            "location": location,
            "procurement_type": procurement_type,
            "description": description,
            "deadline": deadline,
            "raw_text": text,
            "metadata": {},
            "source_url": None,
        }

    def normalize(self, parsed: Dict[str, Any]) -> Any:
        if not parsed:
            return {}
        document_id = str(parsed.get("reference") or parsed.get("title") or "canada_tender")
        metadata = {
            "ministry": parsed.get("ministry"),
            "value": parsed.get("value"),
            "location": parsed.get("location"),
            "procurement_type": parsed.get("procurement_type"),
            "deadline": parsed.get("deadline"),
            **(parsed.get("metadata") or {}),
        }
        return GovernmentDocument(
            connector_name="canada_crawler",
            country_code="CAN",
            source_url=parsed.get("source_url") or "https://www.tenders.gc.ca",
            document_id=document_id,
            title=parsed.get("title"),
            publication_date=None,
            document_type=None,
            language=None,
            raw_content=parsed.get("raw_text") or "",
            metadata=metadata,
        )
