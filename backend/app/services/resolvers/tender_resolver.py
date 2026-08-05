import re

from app.services.resolvers.base_resolver import BaseResolver, EntityMatch


class TenderResolver(BaseResolver):
    entity_type = "tender"

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        normalized = re.sub(r"[^\w\s]", " ", text).strip().lower()
        return re.sub(r"\s+", " ", normalized)

    def resolve(self, text: str) -> EntityMatch:
        normalized = self.normalize_text(text)
        if "government tender" in normalized:
            return EntityMatch(entity_id="tender_government", canonical_name="Government Tender", match_score=1.0)
        if "procurement" in normalized or "tender" in normalized:
            return EntityMatch(entity_id="procurement_notice", canonical_name="Procurement Notice", match_score=0.4)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)
