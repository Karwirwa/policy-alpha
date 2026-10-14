from __future__ import annotations
from typing import List, Any, Dict, Optional
import time
from datetime import datetime, timezone
import requests

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


class USCrawler(BaseCrawler):
    """Crawler for U.S. procurement sources using SAM.gov (skeleton implementation).

    The discover() method calls the SAM.gov opportunities search endpoint to fetch
    recent opportunities. This implementation is defensive and will return an empty
    list on any error.
    """

    SAM_SEARCH_URL = "https://www.sam.gov/api/prod/opps/v1/search"

    def discover(self) -> List[Dict[str, Any]]:
        """Discover recent opportunities from SAM.gov (last 7 days).

        Returns a list of dicts with keys: id, title, source_url, agency, naics_code, deadline, description
        """
        import os
        import logging

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        api_key = os.environ.get('SAM_GOV_API_KEY')
        if api_key:
            headers['X-Api-Key'] = api_key

        params = {
            "sort": "postedDate,desc",
            "limit": 50,
            "postedDate": "7days",
        }

        # Use the crawler session (which has basic retry/backoff configured)
        try:
            resp = self.session.get(self.SAM_SEARCH_URL, params=params, headers=headers, timeout=20)
        except Exception as e:
            logging.warning("SAM.gov request failed: %s", e)
            return []

        if resp.status_code == 200:
            try:
                data = resp.json()
            except Exception as e:
                logging.warning("SAM.gov returned non-JSON payload: %s", e)
                return []
        else:
            # Log and return empty on 403 or other status codes
            logging.warning("SAM.gov returned %s: %s", resp.status_code, (resp.text or '')[:200])
            return []

        results: List[Dict[str, Any]] = []
        # The SAM.gov API wraps opportunities under 'opportunities' or similar keys
        opportunities = data.get("opportunities") or data.get("results") or data.get("opportunitiesList") or data.get("items") or []
        for item in opportunities:
            try:
                solicitation = item.get("solicitationNumber") or item.get("id") or item.get("solicitationId")
                title = item.get("title") or item.get("oppTitle") or item.get("opportunityTitle")
                agency = item.get("agency") or item.get("agencyName")
                naics = item.get("naicsCode") or item.get("naics")
                deadline = item.get("responseDeadline") or item.get("closeDate") or item.get("submissionDueDate")
                description = item.get("description") or item.get("oppDescription") or item.get("noticeDescription")

                source_url = f"https://sam.gov/opp/{solicitation}" if solicitation else None
                results.append({
                    "id": solicitation,
                    "title": title,
                    "source_url": source_url,
                    "agency": agency,
                    "naics_code": naics,
                    "deadline": deadline,
                    "description": description,
                })
            except Exception:
                continue

        return results

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
        """Parse content (JSON or HTML) into structured fields."""
        if not content:
            return {}
        try:
            # if content is JSON
            text = content.decode("utf-8")
            import json
            data = json.loads(text)
            # Try to extract main fields if present
            title = data.get("title") or data.get("opportunityTitle")
            description = data.get("description") or data.get("oppDescription")
            deadline = data.get("responseDeadline") or data.get("closeDate")
            return {
                "title": title,
                "description": description,
                "deadline": deadline,
                "raw_text": description or title or "",
                "metadata": {},
                "source_url": None,
            }
        except Exception:
            # fallback to HTML parsing
            try:
                html = content.decode("utf-8", errors="replace")
            except Exception:
                html = str(content)
            text = self._extract_text_from_html(html)
            # heuristics similar to KenyaCrawler.parse
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            title = lines[0] if lines else None
            description = "\n".join(lines[1:6]) if len(lines) > 1 else None
            return {
                "title": title,
                "description": description,
                "deadline": None,
                "raw_text": text,
                "metadata": {},
                "source_url": None,
            }

    def normalize(self, parsed: Dict[str, Any]) -> Any:
        if not parsed:
            return {}
        document_id = str(parsed.get("reference") or parsed.get("title") or "usa_tender")
        metadata = {
            "deadline": parsed.get("deadline"),
            "ministry": parsed.get("ministry"),
            "value": parsed.get("value"),
            **(parsed.get("metadata") or {}),
        }
        return GovernmentDocument(
            connector_name="us_crawler",
            country_code="USA",
            source_url=parsed.get("source_url") or "https://sam.gov",
            document_id=document_id,
            title=parsed.get("title"),
            publication_date=None,
            document_type=None,
            language=None,
            raw_content=parsed.get("raw_text") or "",
            metadata=metadata,
        )
