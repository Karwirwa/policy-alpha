from __future__ import annotations
from typing import List, Any, Dict, Optional
import re
import time
from datetime import datetime, timezone

import requests

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})|(\d{1,2}\s+\w+\s+\d{4})")


class KenyaCrawler(BaseCrawler):
    """Crawler for Kenyan public procurement and treasury sources.

    The tenders.go.ke site exposes a JSON API at /api/tender, while the HTML shell
    page itself contains no actual tender records. Prefer the API and fall back to
    conservative HTML discovery only when the API is unavailable.
    """

    LISTING_URL = "https://www.tenders.go.ke/tenders"
    API_URLS = [
        "https://www.tenders.go.ke/api/tender",
        "https://www.tenders.go.ke/api/tenders",
        "https://www.tenders.go.ke/api/opportunities",
    ]

    def _discover_api(self) -> List[Dict[str, Any]]:
        for url in self.API_URLS:
            try:
                resp = self._fetch_with_retry(url, max_retries=2, verify=False)
                if resp.status_code != 200:
                    continue
                payload = resp.json()
                if not payload:
                    continue
                items = payload.get("data") if isinstance(payload, dict) and isinstance(payload.get("data"), list) else payload
                if not isinstance(items, list):
                    continue

                candidates: List[Dict[str, Any]] = []
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title") or item.get("name") or item.get("tender_title") or "Untitled tender"
                    tender_ref = item.get("tender_ref") or item.get("ocid") or item.get("reference") or item.get("id")
                    api_id = item.get("id")
                    if not title and not tender_ref:
                        continue
                    source_url = item.get("source_url") or item.get("url")
                    if not source_url and api_id is not None:
                        source_url = f"https://www.tenders.go.ke/api/tender/{api_id}"
                    candidates.append(
                        {
                            "id": str(api_id) if api_id is not None else str(tender_ref),
                            "title": str(title),
                            "source_url": source_url or f"https://www.tenders.go.ke/api/tender/{api_id or tender_ref}",
                            "reference": str(tender_ref),
                            "published_at": item.get("published_at") or item.get("close_at") or item.get("deadline"),
                            "raw": item,
                        }
                    )
                if candidates:
                    return candidates
            except Exception:
                continue
        return []

    def discover(self) -> List[Dict[str, Any]]:
        """Discover recent tender notices from tenders.go.ke via its public API."""
        api_candidates = self._discover_api()
        if api_candidates:
            return api_candidates

        try:
            resp = self._fetch_with_retry(self.LISTING_URL, max_retries=3, verify=False)
            html = resp.text
        except Exception:
            return []

        candidates: List[Dict[str, Any]] = []
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            anchors = soup.find_all("a", href=True)
            seen = set()
            for a in anchors:
                href = a.get("href") or ""
                text = (a.get_text() or "").strip()
                if not href or not text:
                    continue
                if "/tenders" in href or "tender" in href.lower():
                    url = href if href.startswith("http") else requests.compat.urljoin(self.LISTING_URL, href)
                    key = (url, text)
                    if key in seen:
                        continue
                    seen.add(key)
                    id_match = re.search(r"([A-Za-z0-9_-]{6,})", url)
                    doc_id = id_match.group(1) if id_match else url
                    candidates.append({"id": doc_id, "title": text, "source_url": url})
        except Exception:
            return []

        return candidates

    def download(self, doc: Dict[str, Any]) -> bytes:
        """Download the raw content for a tender detail page or API payload."""
        if isinstance(doc, dict) and "raw" in doc and doc["raw"] is not None:
            return __import__("json").dumps(doc["raw"], default=str).encode("utf-8")

        url = doc.get("source_url")
        if not url:
            return b""
        try:
            verify = not url.startswith("https://www.tenders.go.ke")
            resp = self._fetch_with_retry(url, max_retries=2, verify=verify)
            time.sleep(1)
            return resp.content
        except Exception:
            return b""

    def parse(self, content: bytes) -> Dict[str, Any]:
        """Parse HTML or JSON tender content into structured fields."""
        if not content:
            return {}

        try:
            if content[:4] == b"%PDF":
                return {"raw_text": "", "is_pdf": True}
        except Exception:
            pass

        try:
            raw_text = content.decode("utf-8", errors="replace")
        except Exception:
            raw_text = str(content)

        payload = None
        try:
            if raw_text.lstrip().startswith("{") or raw_text.lstrip().startswith("["):
                payload = __import__("json").loads(raw_text)
        except Exception:
            payload = None

        if payload:
            item = payload
            if isinstance(payload, dict):
                if isinstance(payload.get("data"), list):
                    item = payload["data"][0] if payload["data"] else {}
                elif isinstance(payload.get("items"), list):
                    item = payload["items"][0] if payload["items"] else {}
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or item.get("tender_title")
                reference = item.get("tender_ref") or item.get("ocid") or item.get("reference") or item.get("id")
                ministry = item.get("ministry") or item.get("agency") or item.get("department")
                value = item.get("tender_fee") or item.get("estimated_value") or item.get("value") or item.get("budget")
                deadline = item.get("close_at") or item.get("closing_date") or item.get("deadline") or item.get("published_at")
                return {
                    "title": title,
                    "reference": str(reference) if reference is not None else None,
                    "ministry": ministry,
                    "value": str(value) if value is not None else None,
                    "deadline": deadline,
                    "raw_text": raw_text,
                    "is_pdf": False,
                    "source_url": None,
                    "metadata": {"api_payload": item},
                }

        html = raw_text
        text = self._extract_text_from_html(html)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        joined = "\n".join(lines)

        title = lines[0] if lines else None
        reference = None
        ministry = None
        value = None
        deadline = None

        ref_match = re.search(r"(Ref(?:erence)?[:\s]*#?\s*([A-Za-z0-9\-_/]+))", joined, flags=re.I)
        if ref_match:
            reference = ref_match.group(2)
        else:
            m = re.search(r"Tender\s*(No|Number)[:\s]*([A-Za-z0-9\-_/]+)", joined, flags=re.I)
            if m:
                reference = m.group(2)

        min_match = re.search(r"(Ministry|Department|Agency|Authority)[:\s\-]*(.+)", joined, flags=re.I)
        if min_match:
            ministry = min_match.group(2).split('\n')[0].strip()

        val_match = re.search(r"(KES|KSh|USD|US\$|\$)\s*([0-9,]+)", joined)
        if val_match:
            value = f"{val_match.group(1)} {val_match.group(2)}"

        dmatch = DATE_RE.search(joined)
        if dmatch:
            raw_date = dmatch.group(0)
            try:
                parsed_date = datetime.fromisoformat(raw_date)
            except Exception:
                try:
                    parsed_date = datetime.strptime(raw_date, "%d %B %Y")
                except Exception:
                    parsed_date = None
            if parsed_date:
                deadline = parsed_date.replace(tzinfo=timezone.utc)

        return {
            "title": title,
            "reference": reference,
            "ministry": ministry,
            "value": value,
            "deadline": deadline,
            "raw_text": text,
            "is_pdf": False,
            "source_url": None,
            "metadata": {},
        }

    def normalize(self, parsed: Dict[str, Any]) -> Any:
        """Normalize parsed dict into a GovernmentDocument for the KEN source."""
        if not parsed:
            return {}
        document_id = str(parsed.get("reference") or parsed.get("title") or "kenya_tender")
        metadata = {
            "deadline": parsed.get("deadline"),
            "ministry": parsed.get("ministry"),
            "value": parsed.get("value"),
            **(parsed.get("metadata") or {}),
        }
        return GovernmentDocument(
            connector_name="kenya_crawler",
            country_code="KEN",
            source_url=parsed.get("source_url") or "https://www.tenders.go.ke/api/tender",
            document_id=document_id,
            title=parsed.get("title"),
            publication_date=None,
            document_type=None,
            language=None,
            raw_content=parsed.get("raw_text") or "",
            metadata=metadata,
        )
