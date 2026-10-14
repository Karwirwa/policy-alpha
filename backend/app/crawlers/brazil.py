from __future__ import annotations
from typing import List, Any, Dict, Optional
import json
import logging

from .base import BaseCrawler
try:
    from app.connectors.models import GovernmentDocument
except Exception:
    GovernmentDocument = dict


class BrazilCrawler(BaseCrawler):
    """Crawler for Brazilian procurement portals (PNCP / ComprasNet).

    Strategy:
    - Try an open-data JSON endpoint (best-effort guess: compras.dados.gov.br API) and parse returned tenders.
    - Fall back to fetching a portal HTML page and parse links/tender snippets.
    - Use Playwright rendering fallback when necessary.
    """

    ODATA_ENDPOINT = "https://compras.dados.gov.br/licitacoes"
    SEARCH_PAGE = "https://www.gov.br/compras/pt-br"

    def _parse_odata_results(self, data: dict) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        value = data.get('items') if isinstance(data, dict) else None
        if not value or not isinstance(value, list):
            # try common 'results' or 'value'
            value = data.get('results') or data.get('value') if isinstance(data, dict) else None
        if not value or not isinstance(value, list):
            return results
        for item in value:
            try:
                tender_id = item.get('id') or item.get('processo') or item.get('licitacao')
                title = item.get('title') or item.get('objeto') or item.get('descricao') or item.get('nome')
                link = item.get('url') or item.get('link') or None
                if not link and tender_id:
                    link = f"https://compras.dados.gov.br/licitacao/{tender_id}"
                results.append({'id': str(tender_id) if tender_id else (link or title), 'title': title or '', 'source_url': link or ''})
            except Exception:
                continue
        return results

    def discover(self) -> List[Dict[str, Any]]:
        # 1) Try JSON/open-data endpoint
        try:
            resp = self.session.get(self.ODATA_ENDPOINT, params={'limit': 20}, timeout=getattr(self, 'timeout', 15))
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    parsed = self._parse_odata_results(data)
                    if parsed:
                        return parsed
                except Exception:
                    logging.debug("PNCP OData response not JSON or parse failed")
        except Exception:
            pass

        # 2) Try portal HTML
        try:
            resp = self.session.get(self.SEARCH_PAGE, timeout=getattr(self, 'timeout', 15))
            if resp.status_code == 200:
                html = resp.content
            else:
                html = None
        except Exception:
            html = None

        if not html:
            # 3) Playwright fallback
            rendered = self._render_with_playwright(self.SEARCH_PAGE)
            if rendered:
                html = rendered

        if not html:
            return []

        results: List[Dict[str, Any]] = []
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a.get('href') or ''
                text = (a.get_text() or '').strip()
                if not href or not text:
                    continue
                if 'licitacao' in href.lower() or 'licitacao' in text.lower() or '/tender' in href.lower():
                    url = href if href.startswith('http') else f"https://www.gov.br{href}"
                    results.append({'id': url, 'title': text, 'source_url': url})
        except Exception:
            return []

        # dedupe
        seen = set()
        dedup: List[Dict[str, Any]] = []
        for r in results:
            k = r.get('source_url') or r.get('id') or r.get('title')
            if not k or k in seen:
                continue
            seen.add(k)
            dedup.append(r)
        return dedup[:25]

    def download(self, doc: Dict[str, Any]) -> bytes:
        url = doc.get('source_url') or doc.get('id')
        if not url:
            return b''
        try:
            resp = self._fetch_with_retry(url, max_retries=2)
            return resp.content
        except Exception:
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

        reference = None
        agency = None
        value = None
        cpv = None
        location = None
        import re

        # reference patterns (Licitacao/Processo numbers)
        ref_match = re.search(r"(Licitac(?:ã|a)o|Processo|Ref(?:erencia)?)[\s:\-]*#?\s*([A-Za-z0-9\-_/\.]+)", text, flags=re.I)
        if ref_match:
            reference = ref_match.group(2) if ref_match.lastindex and ref_match.lastindex >= 2 else ref_match.group(0)
        # fallback: look for typical BR patterns like LC-2026-001 or PNCP-2026-1234
        if not reference:
            mref = re.search(r"([A-Z]{1,3}[-\s]*\d{4}[-\d]+)", text)
            if mref:
                reference = mref.group(1).replace(' ', '-')

        # agency/contracting authority
        ag_match = re.search(r"(Contracting authority|Contracting entity|Contracting authority|Orgao|Entidade)[:\s\-]*(.+)", text, flags=re.I)
        if ag_match:
            agency = ag_match.group(2).split('\n')[0].strip()

        # value (BRL)
        val_match = re.search(r"(R\$|BRL)\s*([0-9\.\,]+)", text)
        if val_match:
            value = f"{val_match.group(1)} {val_match.group(2)}"

        # CPV-like codes (may vary in Brazil)
        cpv_match = re.search(r"(CPV|NCM)[:\s]*([0-9\-]+)", text, flags=re.I)
        if cpv_match:
            cpv = cpv_match.group(2).strip()

        # location
        loc_match = re.search(r"(Local|Place of performance|Local de entrega|Municipio|Cidade|Estado)[:\s]*(.+)", text, flags=re.I)
        if loc_match:
            location = loc_match.group(2).split('\n')[0].strip()

        # date
        m = re.search(r"(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})", text, flags=re.I)
        deadline = None
        if m:
            try:
                from datetime import datetime, timezone
                # `15 de agosto de 2026` format in Portuguese
                deadline = datetime.strptime(m.group(0), "%d de %B de %Y").replace(tzinfo=timezone.utc)
            except Exception:
                deadline = None

        return {
            'title': title,
            'reference': reference,
            'agency': agency,
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
        document_id = str(parsed.get('reference') or parsed.get('title') or 'brazil_tender')
        metadata = {
            'agency': parsed.get('agency'),
            'value': parsed.get('value'),
            'cpv': parsed.get('cpv'),
            'location': parsed.get('location'),
            'deadline': parsed.get('deadline'),
            **(parsed.get('metadata') or {}),
        }
        return GovernmentDocument(
            connector_name='brazil_crawler',
            country_code='BRA',
            source_url=parsed.get('source_url') or 'https://www.gov.br/compras',
            document_id=document_id,
            title=parsed.get('title'),
            publication_date=None,
            document_type=None,
            language='pt',
            raw_content=parsed.get('raw_text') or '',
            metadata=metadata,
        )