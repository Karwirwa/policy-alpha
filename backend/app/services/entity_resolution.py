from statistics import mean
from typing import Iterable

from app.services.resolvers import (
    AgencyResolver,
    BudgetResolver,
    CompanyResolver,
    CountryResolver,
    ProjectResolver,
    ResolverRegistry,
    TenderResolver,
)
from app.services.resolvers.base_resolver import EntityMatch


class EntityResolutionService:
    """Legacy wrapper for resolver plugins to preserve backward compatibility."""

    def __init__(self) -> None:
        self.registry = ResolverRegistry(
            [
                CompanyResolver(),
                AgencyResolver(),
                ProjectResolver(),
                BudgetResolver(),
                TenderResolver(),
                CountryResolver(),
            ]
        )

    def resolve_company(self, text: str) -> EntityMatch:
        return self.registry.resolve_company(text)

    def resolve_agency(self, text: str) -> EntityMatch:
        return self.registry.resolve_agency(text)

    def resolve_project(self, text: str) -> EntityMatch:
        return self.registry.resolve_project(text)

    def resolve_budget(self, text: str) -> EntityMatch:
        return self.registry.resolve_budget(text)

    def resolve_procurement(self, text: str) -> EntityMatch:
        return self.registry.resolve_tender(text)

    def resolve_country(self, text: str) -> EntityMatch:
        return self.registry.resolve_country(text)

    def resolve_ministry(self, text: str) -> EntityMatch:
        return self.registry.resolve_agency(text)

    def resolve_department(self, text: str) -> EntityMatch:
        return self.registry.resolve_agency(text)

    def average_quality(self, matches: Iterable[EntityMatch]) -> float:
        scores = [match.match_score for match in matches if match.entity_id]
        return mean(scores) if scores else 0.0
