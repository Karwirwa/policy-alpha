from app.models.evidence import Evidence
from app.models.entity_relationship import EntityRelationship, RelationshipType
from app.repositories.relationship_repository import RelationshipRepository


class RelationshipBuilder:
    """Build deterministic relationships from evidence records."""

    RELATIONSHIP_RULES = [
        ("company", RelationshipType.AWARDED, "tender"),
        ("tender", RelationshipType.FUNDED_BY, "budget"),
        ("budget", RelationshipType.MANAGED_BY, "agency"),
        ("agency", RelationshipType.LOCATED_IN, "country"),
        ("project", RelationshipType.MENTIONS, "company"),
        ("company", RelationshipType.SUPPLIES, "project"),
    ]

    ENTITY_FIELD_MAP = {
        "company": "company_id",
        "agency": "agency_id",
        "project": "project_id",
        "budget": "budget_id",
        "tender": "procurement_id",
        "country": "country_id",
    }

    def __init__(self, repository: RelationshipRepository) -> None:
        self.repository = repository

    def build(self, evidence: Evidence) -> list[EntityRelationship]:
        relationships: list[EntityRelationship] = []
        for source_type, relationship_type, target_type in self.RELATIONSHIP_RULES:
            source_id = self._get_entity_id(evidence, source_type)
            target_id = self._get_entity_id(evidence, target_type)
            if source_id and target_id:
                relationship = EntityRelationship(
                    source_entity_type=source_type,
                    source_entity_id=source_id,
                    relationship_type=relationship_type,
                    target_entity_type=target_type,
                    target_entity_id=target_id,
                    evidence_id=evidence.id,
                    confidence=evidence.evidence_strength,
                )
                created = self.repository.create(relationship)
                relationships.append(created)
        return relationships

    def _get_entity_id(self, evidence: Evidence, entity_type: str) -> str | None:
        field_name = self.ENTITY_FIELD_MAP.get(entity_type)
        if not field_name:
            return None
        return getattr(evidence, field_name, None)
