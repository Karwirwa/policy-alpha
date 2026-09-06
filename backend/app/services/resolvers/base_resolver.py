from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class EntityMatch:
    entity_id: str | None
    canonical_name: str | None
    match_score: float


class BaseResolver(ABC):
    """Base class for entity resolver plugins."""

    entity_type: str

    @abstractmethod
    def resolve(self, text: str, country_code: str | None = None) -> EntityMatch:
        raise NotImplementedError


class ResolverRegistry:
    """Registry for resolver plugins and backward-compatible resolution methods."""

    def __init__(self, resolvers: list[BaseResolver] | None = None) -> None:
        self.resolvers: list[BaseResolver] = []
        self._resolver_map: dict[str, BaseResolver] = {}
        if resolvers:
            for resolver in resolvers:
                self.register(resolver)

    def register(self, resolver: BaseResolver) -> None:
        self.resolvers.append(resolver)
        self._resolver_map[resolver.entity_type] = resolver

    def resolve_all(self, text: str, country_code: str | None = None) -> dict[str, EntityMatch]:
        return {resolver.entity_type: resolver.resolve(text, country_code=country_code) for resolver in self.resolvers}

    def resolve_company(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self._resolver_map["company"].resolve(text, country_code=country_code)


    def resolve_agency(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self._resolver_map["agency"].resolve(text, country_code=country_code)


    def resolve_project(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self._resolver_map["project"].resolve(text, country_code=country_code)


    def resolve_budget(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self._resolver_map["budget"].resolve(text, country_code=country_code)


    def resolve_tender(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self._resolver_map["tender"].resolve(text, country_code=country_code)


    def resolve_country(self, text: str, country_code: str | None = None) -> EntityMatch:
        return self._resolver_map["country"].resolve(text, country_code=country_code)