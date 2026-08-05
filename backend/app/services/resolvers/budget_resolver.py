import re

from app.services.resolvers.base_resolver import BaseResolver, EntityMatch


class BudgetResolver(BaseResolver):
    entity_type = "budget"

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        normalized = re.sub(r"[^\w\s]", " ", text).strip().lower()
        return re.sub(r"\s+", " ", normalized)

    def resolve(self, text: str) -> EntityMatch:
        normalized = self.normalize_text(text)
        if "infrastructure budget" in normalized:
            return EntityMatch(entity_id="budget_infrastructure", canonical_name="Infrastructure Budget", match_score=1.0)
        if "budget" in normalized:
            return EntityMatch(entity_id="budget_document", canonical_name="Budget Document", match_score=0.4)
        return EntityMatch(entity_id=None, canonical_name=None, match_score=0.0)
