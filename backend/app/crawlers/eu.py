from __future__ import annotations
from typing import List, Any, Dict, Optional
import json
import logging

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


class EUCrawler(BaseCrawler):
    """Crawler for Tenders Electronic Daily (TED).

    Implementation strategy:
    - Try an OData/JSON endpoint (common pattern: /api/odata/v1/Notices) and parse notices.
    - Fall back to an RSS/HTML search page and parse links.
    - As a last resort, attempt Playwright rendering of the search page and parse the DOM.

    The implemention is defensive: if endpoints are unavailable or blocked it returns an empty list.
    """

    ODATA_ENDPOINT = "https://ted.europa.eu/api/odata/v1/Notices"  # best-effort guess; may be blocked/changed
    SEARCH_PAGE = "https://ted.europa.eu/"  # fallback search page

    def _parse_odata_results(self, data: dict) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        value = data.get('value') if isinstance(data, dict) else None
        if not value or not isinstance(value, list):
            return results
        for item in value:
            try:
                # Attempt to read common fields - adapt if TED's schema differs
                notice_id = item.get('NoticeID') or item.get('ID') or item.get('Id') or item.get('NoticeNumber')
                title = item.get('Title') or item.get('NoticeTitle') or item.get('title')
                link = None
                # Some OData responses include a Link or Url
                if 'Url' in item:
                    link = item.get('Url')
                elif 'Link' in item:
                    link = item.get('Link')
                elif notice_id:
                    link = f"https://ted.europa.eu/udl?uri=TED:NOTICE:{notice_id}:EN:HTML"

                results.append({
                    'id': str(notice_id) if notice_id else (link or title),
                    'title': title or "",
                    'source_url': link or "",
                })
            except Exception:
                continue
        return results

    def discover(self) -> List[Dict[str, Any]]:
        # 1) Try OData/JSON endpoint
        try:
            resp = self.session.get(self.ODATA_ENDPOINT, params={'$top': 25}, timeout=getattr(self, 'timeout', 15))
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    parsed = self._parse_odata_results(data)
                    if parsed:
                        return parsed
                except Exception:
                    logging.debug("TED OData response not JSON or parse failed")
        except Exception:
            pass

        # 2) Try RSS/HTML search page
        try:
            resp = self.session.get(self.SEARCH_PAGE, timeout=getattr(self, 'timeout', 15))
            if resp.status_code == 200:
                html = resp.content
            else:
                html = None
        except Exception:
            html = None

        if not html:
            # 3) Try Playwright render fallback
            rendered = self._render_with_playwright(self.SEARCH_PAGE)
            if rendered:
                html = rendered

        if not html:
            return []

        results: List[Dict[str, Any]] = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            # Look for common notice links
            for a in soup.find_all('a', href=True):
                href = a.get('href') or ''
                text = (a.get_text() or '').strip()
                if not href or not text:
                    continue
                # heuristic: TED notice links often contain 'Notice' or '/TED/notice/'
                if 'notice' in href.lower() or 'ted' in href.lower() or 'Notice' in text:
                    url = href if href.startswith('http') else f"https://ted.europa.eu{href}"
                    results.append({'id': url, 'title': text, 'source_url': url})
        except Exception:
            return []

        # Deduplicate by source_url
        seen = set()
        deduped: List[Dict[str, Any]] = []
        for r in results:
            k = r.get('source_url') or r.get('id') or r.get('title')
            if not k or k in seen:
                continue
            seen.add(k)
            deduped.append(r)
        return deduped[:25]

    def download(self, doc: Dict[str, Any]) -> bytes:
        url = doc.get('source_url') or doc.get('id')
        if not url:
            return b''
        try:
            resp = self._fetch_with_retry(url, max_retries=2)
            return resp.content
        except Exception:
            # try Playwright if direct fetch fails
            rendered = self._render_with_playwright(url)
            if rendered:
                return rendered
            return b''

    def parse(self, content: bytes) -> Dict[str, Any]:
        if not content:
            return {}
        try:
            html = content.decode('utf-8', errors='replace')
        except Exception:
            html = str(content)
        text = self._extract_text_from_html(html)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        title = lines[0] if lines else None
        description = '\n'.join(lines[1:8]) if len(lines) > 1 else None

        # best-effort extraction
        reference = None
        issuing_body = None
        value = None
        cpv = None
        location = None
        import re

        # reference patterns
        ref_match = re.search(r"(Notice|Reference|Ref(?:erence)?|TED\s*No)[:\s]*#?\s*([A-Za-z0-9\-_/]+)", text, flags=re.I)
        if ref_match:
            reference = ref_match.group(2) if ref_match.lastindex and ref_match.lastindex >= 2 else ref_match.group(0)
        # fallback: some notices include 'Notice: TED No TED-2026-0001' so the first capture may be 'TED' — look for full TED-YYYY-NNNN pattern
        if not reference or (isinstance(reference, str) and reference.strip().upper() == 'TED'):
            mref = re.search(r"(TED[-\s]*\d{4}[-\d]+)", text, flags=re.I)
            if mref:
                reference = mref.group(1).replace(' ', '-')

        # issuing body
        ib_match = re.search(r"(Ministry|Authority|Agency|Contracting authority|Contracting entity)[:\s\-]*(.+)", text, flags=re.I)
        if ib_match:
            issuing_body = ib_match.group(2).split('\n')[0].strip()

        # value/currency
        val_match = re.search(r"(EUR|€|GBP|£|USD|US\$)\s*([0-9,]+(\.[0-9]+)?)", text)
        if val_match:
            value = f"{val_match.group(1)} {val_match.group(2)}"

        # CPV codes
        cpv_match = re.search(r"CPV\s*[:\s]*([0-9\-]+)", text, flags=re.I)
        if cpv_match:
            cpv = cpv_match.group(1).strip()

        # location
        loc_match = re.search(r"(Place of performance|Location|Country)[:\s]*(.+)", text, flags=re.I)
        if loc_match:
            location = loc_match.group(2).split('\n')[0].strip()

        # attempt to find date
        m = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", text)
        deadline = None
        if m:
            try:
                from datetime import datetime, timezone
                deadline = datetime.strptime(m.group(0), "%d %B %Y").replace(tzinfo=timezone.utc)
            except Exception:
                deadline = None

        return {
            'title': title,
            'reference': reference,
            'issuing_body': issuing_body,
            'value': value,
            'cpv': cpv,
            'location': location,
            'description': description,
            'deadline': deadline,
            'raw_text': text,
            'metadata': {},
            'source_url': None,
        }

    def normalize(self, parsed: Dict[str, Any]) -> Any:
        if not parsed:
            return {}
        document_id = str(parsed.get('reference') or parsed.get('title') or 'eu_tender')
        metadata = {
            'issuing_body': parsed.get('issuing_body'),
            'value': parsed.get('value'),
            'cpv': parsed.get('cpv'),
            'location': parsed.get('location'),
            'deadline': parsed.get('deadline'),
            **(parsed.get('metadata') or {}),
        }
        return GovernmentDocument(
            connector_name='eu_crawler',
            country_code='EU',
            source_url=parsed.get('source_url') or 'https://ted.europa.eu',
            document_id=document_id,
            title=parsed.get('title'),
            publication_date=None,
            document_type=None,
            language=None,
            raw_content=parsed.get('raw_text') or '',
            metadata=metadata,
        )