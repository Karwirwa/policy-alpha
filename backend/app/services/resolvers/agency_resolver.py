import re

from app.services.resolvers.base_resolver import BaseResolver, EntityMatch


class AgencyResolver(BaseResolver):
    entity_type = "agency"

    AGENCY_ALIASES = {
        "ministry of roads": {"id": "agency_roads", "name": "State Department for Roads"},
        "state department for roads": {"id": "agency_roads", "name": "State Department for Roads"},
        "department of roads": {"id": "agency_roads", "name": "State Department for Roads"},
        "ministry of health": {"id": "agency_health", "name": "Ministry of Health"},
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

        if normalized in self.AGENCY_ALIASES:
            entry = self.AGENCY_ALIASES[normalized]
            return EntityMatch(entity_id=entry["id"], canonical_name=entry["name"], match_score=1.0)

        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

    def _search_aliases(self, raw_text: str) -> EntityMatch:
        normalized_text = self.normalize_text(raw_text)
        for alias, entry in self.AGENCY_ALIASES.items():
            if alias in normalized_text:
                return EntityMatch(entity_id=entry["id"], canonical_name=entry["name"], match_score=0.9)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

    def resolve(self, text: str) -> EntityMatch:
        exact = self._resolve_name(text)
        if exact.entity_id:
            return exact
        return self._search_aliases(text)
