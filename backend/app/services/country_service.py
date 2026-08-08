from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.countries import list_countries, get_country_config
from app.repositories.country_repository import CountryRepository
from app.services.entity_resolution import EntityResolutionService


class CountryService:
    """High-level country intelligence service that composes repository queries and
    existing engines (evidence, opportunity, relationship) to produce a country profile.

    The service is configuration-driven: supported countries are defined in
    app.core.countries.COUNTRIES. Adding a country requires only adding its
    config entry — no code changes are necessary.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CountryRepository(db)
        self.resolver = EntityResolutionService()

    def list_countries(self) -> List[Dict[str, Any]]:
        # Merge configured countries with any persisted Country rows
        configured = list_countries()
        # Ensure the database contains Country entries: repository will return DB rows
        db_countries = self.repo.list_countries()
        db_map = {c.id: c for c in db_countries}
        merged = []
        for cfg in configured:
            entry = {"id": cfg["id"], "name": cfg["name"], "configured": True}
            if cfg["id"] in db_map:
                entry["db_name"] = db_map[cfg["id"]].name
            merged.append(entry)
        return merged

    def get_country_profile(self, country_name: str) -> Dict[str, Any]:
        # resolve the country via configuration first, then via entity resolver
        from app.core.countries import normalize_country_id

        cfg = get_country_config(country_name)
        resolved = self.resolver.resolve_country(country_name)
        country_id = None
        if resolved and resolved.entity_id:
            normalized = normalize_country_id(resolved.entity_id)
            if normalized:
                country_id = normalized
        if not country_id and cfg:
            country_id = cfg.get("id")
        if not country_id:
            # last effort: try repository by name
            country = self.repo.get_country(country_name)
            if not country:
                raise ValueError("Country not found")
            country_id = country.id

        # Core metrics
        evidence_count = self.repo.evidence_count(country_id)
        relationship_count = self.repo.relationship_count(country_id)
        avg_opportunity = self.repo.average_opportunity_score(country_id)

        ministries = self.repo.get_ministries(country_id, limit=10)
        projects = self.repo.get_projects(country_id, limit=10)
        budgets = self.repo.get_budgets(country_id, limit=10)
        companies = self.repo.get_companies(country_id, limit=10)
        tenders = self.repo.get_tenders(country_id, limit=10)

        cfg_entry = get_country_config(country_name) or {}

        profile = {
            "country": {"id": country_id, "name": cfg_entry.get("name") or country_name},
            "government_spending": [],  # derived from budgets; left for pipeline enrichment
            "top_ministries": [{"id": m.id, "name": getattr(m, "name", None)} for m in ministries],
            "largest_budgets": [{"id": b.id, "name": getattr(b, "name", None)} for b in budgets],
            "largest_projects": [{"id": p.id, "name": getattr(p, "name", None)} for p in projects],
            "most_active_companies": [{"id": c.id, "name": getattr(c, "name", None)} for c in companies],
            "tenders": [{"id": t.id, "name": getattr(t, "name", None)} for t in tenders],
            "opportunity_score": avg_opportunity,
            "risk_score": None,
            "evidence_count": evidence_count,
            "relationship_count": relationship_count,
            "official_sources": cfg_entry.get("sources", {}),
            "crawler_health": {},
        }
        return profile

    def ministries(self, country_name: str) -> List[Dict[str, Any]]:
        cfg = get_country_config(country_name)
        resolved = self.resolver.resolve_country(country_name)
        if resolved and resolved.entity_id:
            from app.core.countries import normalize_country_id

            normalized = normalize_country_id(resolved.entity_id)
            if normalized:
                country_id = normalized
            else:
                # fall back to configured id if resolver produced an unknown id
                if cfg:
                    country_id = cfg.get("id")
                else:
                    country = self.repo.get_country(country_name)
                    if not country:
                        raise ValueError("Country not found")
                    country_id = country.id
        elif cfg:
            country_id = cfg.get("id")
        else:
            country = self.repo.get_country(country_name)
            if not country:
                raise ValueError("Country not found")
            country_id = country.id
        ministries = self.repo.get_ministries(country_id)
        return [{"id": m.id, "name": getattr(m, "name", None)} for m in ministries]

    def tenders(self, country_name: str) -> List[Dict[str, Any]]:
        cfg = get_country_config(country_name)
        resolved = self.resolver.resolve_country(country_name)
        if resolved and resolved.entity_id:
            from app.core.countries import normalize_country_id

            normalized = normalize_country_id(resolved.entity_id)
            if normalized:
                country_id = normalized
            else:
                if cfg:
                    country_id = cfg.get("id")
                else:
                    country = self.repo.get_country(country_name)
                    if not country:
                        raise ValueError("Country not found")
                    country_id = country.id
        elif cfg:
            country_id = cfg.get("id")
        else:
            country = self.repo.get_country(country_name)
            if not country:
                raise ValueError("Country not found")
            country_id = country.id
        tenders = self.repo.get_tenders(country_id)
        return [{"id": t.id, "name": getattr(t, "name", None)} for t in tenders]

    def budgets(self, country_name: str) -> List[Dict[str, Any]]:
        cfg = get_country_config(country_name)
        resolved = self.resolver.resolve_country(country_name)
        if resolved and resolved.entity_id:
            from app.core.countries import normalize_country_id

            normalized = normalize_country_id(resolved.entity_id)
            if normalized:
                country_id = normalized
            else:
                if cfg:
                    country_id = cfg.get("id")
                else:
                    country = self.repo.get_country(country_name)
                    if not country:
                        raise ValueError("Country not found")
                    country_id = country.id
        elif cfg:
            country_id = cfg.get("id")
        else:
            country = self.repo.get_country(country_name)
            if not country:
                raise ValueError("Country not found")
            country_id = country.id
        budgets = self.repo.get_budgets(country_id)
        return [{"id": b.id, "name": getattr(b, "name", None)} for b in budgets]

    def projects(self, country_name: str) -> List[Dict[str, Any]]:
        cfg = get_country_config(country_name)
        resolved = self.resolver.resolve_country(country_name)
        if resolved and resolved.entity_id:
            from app.core.countries import normalize_country_id

            normalized = normalize_country_id(resolved.entity_id)
            if normalized:
                country_id = normalized
            else:
                if cfg:
                    country_id = cfg.get("id")
                else:
                    country = self.repo.get_country(country_name)
                    if not country:
                        raise ValueError("Country not found")
                    country_id = country.id
        elif cfg:
            country_id = cfg.get("id")
        else:
            country = self.repo.get_country(country_name)
            if not country:
                raise ValueError("Country not found")
            country_id = country.id
        projects = self.repo.get_projects(country_id)
        return [{"id": p.id, "name": getattr(p, "name", None)} for p in projects]

    def companies(self, country_name: str) -> List[Dict[str, Any]]:
        cfg = get_country_config(country_name)
        resolved = self.resolver.resolve_country(country_name)
        if resolved and resolved.entity_id:
            from app.core.countries import normalize_country_id

            normalized = normalize_country_id(resolved.entity_id)
            if normalized:
                country_id = normalized
            else:
                if cfg:
                    country_id = cfg.get("id")
                else:
                    country = self.repo.get_country(country_name)
                    if not country:
                        raise ValueError("Country not found")
                    country_id = country.id
        elif cfg:
            country_id = cfg.get("id")
        else:
            country = self.repo.get_country(country_name)
            if not country:
                raise ValueError("Country not found")
            country_id = country.id
        companies = self.repo.get_companies(country_id)
        return [{"id": c.id, "name": getattr(c, "name", None)} for c in companies]
