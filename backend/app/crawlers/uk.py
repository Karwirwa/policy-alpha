from __future__ import annotations
from typing import List, Any, Dict
import re
import time
from datetime import datetime, timezone

import requests

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


class UKCrawler(BaseCrawler):
    """Crawler for UK procurement sources (Contracts Finder and FTS) (skeleton)."""

    CONTRACTS_FINDER = "https://www.contractsfinder.service.gov.uk/Search/Results"

    def _extract_id_from_url(self, href: str) -> str:
        if not href:
            return ""
        try:
            from urllib.parse import urlparse
            path = urlparse(href).path
            segs = [s for s in path.split('/') if s]
            return segs[-1] if segs else href
        except Exception:
            return href

    def discover(self) -> List[Dict[str, Any]]:
        import logging
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-GB,en;q=0.9',
            }
            params = {'page': 1, 'sort': 'published', 'publishedWithin': 7}
            resp = None
            try:
                resp = self.session.get(self.CONTRACTS_FINDER, params=params, headers=headers, timeout=getattr(self, 'timeout', 15))
            except Exception:
                resp = None

            html = None
            if resp is not None and getattr(resp, 'status_code', None) == 200:
                html = resp.content
            else:
                logging.warning("Contracts Finder returned %s; attempting Playwright render", getattr(resp, 'status_code', 'no-response'))
                rendered = self._render_with_playwright(self.CONTRACTS_FINDER)
                if rendered:
                    html = rendered
                else:
                    return []
        except Exception as e:
            import logging as _log
            _log.error("Contracts Finder fetch failed: %s", e)
            return []

        results: List[Dict[str, Any]] = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select('.search-result, .result, .contract-item'):
                title_elem = item.select_one('a, .title, .result-title')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                href = title_elem.get('href') if hasattr(title_elem, 'get') else None
                url = href if href and href.startswith('http') else (f"https://www.contractsfinder.service.gov.uk{href}" if href else '')
                results.append({
                    'id': self._extract_id_from_url(href) if href else '',
                    'title': title,
                    'source_url': url,
                })
        except Exception:
            return []

        return results[:20]

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

        # heuristics for fields
        reference = None
        ministry = None
        value = None
        location = None
        contract_type = None
        import re

        # reference patterns
        ref_match = re.search(r"(?:Reference|Ref(?:erence)?|Tender\s*(No|Number))[:\s]*#?\s*([A-Za-z0-9\-_/]+)", text, flags=re.I)
        if ref_match:
            reference = ref_match.group(2) if ref_match.lastindex and ref_match.lastindex >= 2 else ref_match.group(0)

        # ministry/issuing body
        min_match = re.search(r"(Ministry|Department|Agency|Authority)[:\s\-]*(.+)", text, flags=re.I)
        if min_match:
            ministry = re.sub(r"<[^>]+>", "", min_match.group(2)).split('\n')[0].strip()

        # value/currency
        val_match = re.search(r"(GBP|£|EUR|USD|US\$|\$)\s*([0-9,]+(\.[0-9]+)?)", text)
        if val_match:
            value = f"{val_match.group(1)} {val_match.group(2)}"

        # location
        loc_match = re.search(r"(Location|Place of Performance|Region)[:\s]*(.+)", text, flags=re.I)
        if loc_match:
            location = re.sub(r"<[^>]+>", "", loc_match.group(2)).split('\n')[0].strip()

        # contract type / procurement type
        type_match = re.search(r"(Contract type|Procurement Type|Framework|Contracting Method)[:\s]*(.+)", text, flags=re.I)
        if type_match:
            contract_type = re.sub(r"<[^>]+>", "", type_match.group(2)).split('\n')[0].strip()
            # Trim common trailing tokens that may follow in raw HTML text
            contract_type = re.split(r"(?i)Deadline[:\s]", contract_type)[0].strip()
            contract_type = re.split(r"(\d{1,2}\s+\w+\s+\d{4})", contract_type)[0].strip()

        # attempt to find date
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
            "contract_type": contract_type,
            "description": description,
            "deadline": deadline,
            "raw_text": text,
            "metadata": {},
            "source_url": None,
        }

    def normalize(self, parsed: Dict[str, Any]) -> Any:
        if not parsed:
            return {}
        document_id = str(parsed.get("reference") or parsed.get("title") or "uk_tender")
        metadata = {
            "ministry": parsed.get("ministry"),
            "value": parsed.get("value"),
            "location": parsed.get("location"),
            "contract_type": parsed.get("contract_type"),
            "deadline": parsed.get("deadline"),
            **(parsed.get("metadata") or {}),
        }
        return GovernmentDocument(
            connector_name="uk_crawler",
            country_code="GBR",
            source_url=parsed.get("source_url") or "https://www.contractsfinder.service.gov.uk",
            document_id=document_id,
            title=parsed.get("title"),
            publication_date=None,
            document_type=None,
            language=None,
            raw_content=parsed.get("raw_text") or "",
            metadata=metadata,
        )
