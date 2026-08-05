from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.models.budget import Budget
from app.models.company import Company
from app.models.country import Country
from app.models.document import Document
from app.models.entity_relationship import EntityRelationship
from app.models.project import Project
from app.models.tender import Tender
from app.repositories.relationship_repository import RelationshipRepository
from app.services.entity_resolution import EntityResolutionService


class GraphService:
    ENTITY_MODEL_MAP = {
        "company": Company,
        "agency": Agency,
        "project": Project,
        "budget": Budget,
        "tender": Tender,
        "country": Country,
        "document": Document,
    }

    ENTITY_RESOLVER_MAP = {
        "company": EntityResolutionService().resolve_company,
        "agency": EntityResolutionService().resolve_agency,
        "project": EntityResolutionService().resolve_project,
        "budget": EntityResolutionService().resolve_budget,
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = RelationshipRepository(db)
        self.resolver = EntityResolutionService()

    def get_company_network(self, company_name: str) -> dict[str, Any]:
        return self._build_network("company", company_name)

    def get_agency_network(self, agency_name: str) -> dict[str, Any]:
        return self._build_network("agency", agency_name)

    def get_project_network(self, project_name: str) -> dict[str, Any]:
        return self._build_network("project", project_name)

    def get_budget_network(self, budget_name: str) -> dict[str, Any]:
        return self._build_network("budget", budget_name)

    def _build_network(self, entity_type: str, entity_name: str) -> dict[str, Any]:
        entity_id, canonical_name = self._resolve_entity(entity_type, entity_name)
        entity_record = self._load_entity(entity_type, entity_id)
        relationships = self.repository.find_by_entity(entity_type, entity_id)

        return {
            "entity": {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_name": canonical_name or (entity_record.name if entity_record else entity_id),
            },
            "connections": [self._format_relationship(rel, entity_type, entity_id) for rel in relationships],
        }

    def _resolve_entity(self, entity_type: str, name: str) -> tuple[str, str | None]:
        if entity_type in self.ENTITY_RESOLVER_MAP:
            resolver = self.ENTITY_RESOLVER_MAP[entity_type]
            match = resolver(name)
            if match.entity_id:
                return match.entity_id, match.canonical_name

        record = self._query_entity_by_name(entity_type, name)
        if record:
            return record.id, record.name

        raise ValueError(f"Unknown {entity_type} '{name}'")

    def _query_entity_by_name(self, entity_type: str, name: str) -> Any | None:
        entity_class = self.ENTITY_MODEL_MAP.get(entity_type)
        if not entity_class:
            return None
        return self.db.query(entity_class).filter(func.lower(entity_class.name) == name.strip().lower()).first()

    def _load_entity(self, entity_type: str, entity_id: str) -> Any | None:
        entity_class = self.ENTITY_MODEL_MAP.get(entity_type)
        if not entity_class:
            return None
        return self.db.get(entity_class, entity_id)

    def _format_relationship(self, relationship: EntityRelationship, focus_type: str, focus_id: str) -> dict[str, Any]:
        if relationship.source_entity_type == focus_type and relationship.source_entity_id == focus_id:
            direction = "outbound"
            other_type = relationship.target_entity_type
            other_id = relationship.target_entity_id
        else:
            direction = "inbound"
            other_type = relationship.source_entity_type
            other_id = relationship.source_entity_id

        other_record = self._load_entity(other_type, other_id)
        evidence_summary = None
        if relationship.evidence is not None:
            evidence_summary = {
                "id": relationship.evidence.id,
                "title": relationship.evidence.title,
                "source_reference": relationship.evidence.source_reference,
            }

        return {
            "direction": direction,
            "relationship_type": relationship.relationship_type.value,
            "other_entity_type": other_type,
            "other_entity_id": other_id,
            "other_entity_name": other_record.name if other_record else other_id,
            "confidence": relationship.confidence,
            "evidence": evidence_summary,
        }
