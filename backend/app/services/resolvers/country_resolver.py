import re

from app.services.resolvers.base_resolver import BaseResolver, EntityMatch


class CountryResolver(BaseResolver):
    entity_type = "country"

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        normalized = re.sub(r"[^\w\s]", " ", text).strip().lower()
        return re.sub(r"\s+", " ", normalized)

    def resolve(self, text: str) -> EntityMatch:
        normalized = self.normalize_text(text)
        if "kenya" in normalized:
            return EntityMatch(entity_id="country_kenya", canonical_name="Kenya", match_score=1.0)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)
