import re

from app.services.resolvers.base_resolver import BaseResolver, EntityMatch


class ProjectResolver(BaseResolver):
    entity_type = "project"

    PROJECT_ALIASES = {
        "tana river irrigation project": {"id": "project_tana_river", "name": "Tana River Irrigation Project"},
        "road expansion project": {"id": "project_road_expansion", "name": "Road Expansion Project"},
        "nairobi expressway": {"id": "project_nairobi_expressway", "name": "Nairobi Expressway"},
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

        if normalized in self.PROJECT_ALIASES:
            entry = self.PROJECT_ALIASES[normalized]
            return EntityMatch(entity_id=entry["id"], canonical_name=entry["name"], match_score=1.0)

        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

    def _search_aliases(self, raw_text: str) -> EntityMatch:
        normalized_text = self.normalize_text(raw_text)
        for alias, entry in self.PROJECT_ALIASES.items():
            if alias in normalized_text:
                return EntityMatch(entity_id=entry["id"], canonical_name=entry["name"], match_score=0.9)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)

    def resolve(self, text: str, country_code: str | None = None) -> EntityMatch:
        # Cross-country normalization: detect generic infrastructure-related terms and map to a canonical infrastructure project
        normalized = self.normalize_text(text)
        infra_keywords = ["infrastructure project", "road project", "road expansion", "highway expansion", "bridge project", "transport project"]
        for kw in infra_keywords:
            if kw in normalized:
                return EntityMatch(entity_id="project_infrastructure", canonical_name="Infrastructure Project", match_score=0.8)

        exact = self._resolve_name(text)
        if exact.entity_id:
            return exact
        return self._search_aliases(text)
