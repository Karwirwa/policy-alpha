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

    def resolve_company(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_company(text, country_code=country_code)

    def resolve_agency(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_agency(text, country_code=country_code)

    def resolve_project(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_project(text, country_code=country_code)

    def resolve_budget(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_budget(text, country_code=country_code)

    def resolve_procurement(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_tender(text, country_code=country_code)

    def resolve_country(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_country(text, country_code=country_code)

    def resolve_ministry(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_agency(text, country_code=country_code)

    def resolve_department(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self.registry.resolve_agency(text, country_code=country_code)

    def average_quality(self, matches: Iterable[EntityMatch]) -> float:
        scores = [match.match_score for match in matches if match.entity_id]
        return mean(scores) if scores else 0.0
