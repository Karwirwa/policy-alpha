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

    def resolve(self, text: str, country_code: str | None = None) -> EntityMatch:
        normalized = self.normalize_text(text)
        if "kenya" in normalized:
            return EntityMatch(entity_id="country_kenya", canonical_name="Kenya", match_score=1.0)
        if "united states" in normalized or "united_states" in normalized or "usa" in normalized or normalized == "us":
            return EntityMatch(entity_id="country_united_states", canonical_name="United States", match_score=1.0)
        if "united kingdom" in normalized or "united_kingdom" in normalized or "uk" in normalized or "gbr" in normalized:
            return EntityMatch(entity_id="country_united_kingdom", canonical_name="United Kingdom", match_score=1.0)
        if "canada" in normalized:
            return EntityMatch(entity_id="country_canada", canonical_name="Canada", match_score=1.0)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)
