import re

from app.services.resolvers.base_resolver import BaseResolver, EntityMatch


class CompanyResolver(BaseResolver):
    entity_type = "company"

    COMPANY_ALIASES = {
        "bamburi": {"id": "company_bamburi", "name": "Bamburi Cement PLC"},
        "bamburi cement": {"id": "company_bamburi", "name": "Bamburi Cement PLC"},
        "bamburi cement plc": {"id": "company_bamburi", "name": "Bamburi Cement PLC"},
        "safaricom": {"id": "company_safaricom", "name": "Safaricom PLC"},
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        normalized = re.sub(r"[^\w\s]", " ", text).strip().lower()
        return re.sub(r"\s+", " ", normalized)

    def _resolve_name(self, candidate: str) -> EntityMatch:
        normalized = self.normalize_text(candidate)
        if not normalized:
            return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

        if normalized in self.COMPANY_ALIASES:
            entry = self.COMPANY_ALIASES[normalized]
            return EntityMatch(entity_id=entry["id"], canonical_name=entry["name"], match_score=1.0)

        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

    def _search_aliases(self, raw_text: str) -> EntityMatch:
        normalized_text = self.normalize_text(raw_text)
        for alias, entry in self.COMPANY_ALIASES.items():
            if alias in normalized_text:
                return EntityMatch(entity_id=entry["id"], canonical_name=entry["name"], match_score=0.9)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

    def resolve(self, text: str, country_code: str | None = None) -> EntityMatch:
        # country_code may be used in the future to prefer local matches
        exact = self._resolve_name(text)
        if exact.entity_id:
            return exact
        return self._search_aliases(text)
