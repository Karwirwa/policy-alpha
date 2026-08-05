from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.entity_relationship import EntityRelationship, RelationshipType


class RelationshipRepository:
    """Repository for reading and storing entity relationships."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, relationship: EntityRelationship) -> EntityRelationship:
        existing = self._find_duplicate(relationship)
        if existing:
            return existing

        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def _find_duplicate(self, relationship: EntityRelationship) -> EntityRelationship | None:
        return (
            self.db.query(EntityRelationship)
            .filter(EntityRelationship.source_entity_type == relationship.source_entity_type)
            .filter(EntityRelationship.source_entity_id == relationship.source_entity_id)
            .filter(EntityRelationship.relationship_type == relationship.relationship_type)
            .filter(EntityRelationship.target_entity_type == relationship.target_entity_type)
            .filter(EntityRelationship.target_entity_id == relationship.target_entity_id)
            .filter(EntityRelationship.evidence_id == relationship.evidence_id)
            .first()
        )

    def find_by_entity(self, entity_type: str, entity_id: str) -> list[EntityRelationship]:
        return (
            self.db.query(EntityRelationship)
            .filter(
                or_(
                    (EntityRelationship.source_entity_type == entity_type) &
                    (EntityRelationship.source_entity_id == entity_id),
                    (EntityRelationship.target_entity_type == entity_type) &
                    (EntityRelationship.target_entity_id == entity_id),
                )
            )
            .order_by(EntityRelationship.id)
            .all()
        )

    def find_neighbors(self, entity_type: str, entity_id: str) -> list[EntityRelationship]:
        return self.find_by_entity(entity_type, entity_id)

    def find_by_type(self, relationship_type: RelationshipType | str) -> list[EntityRelationship]:
        if isinstance(relationship_type, str):
            relationship_type = RelationshipType(relationship_type)
        return (
            self.db.query(EntityRelationship)
            .filter(EntityRelationship.relationship_type == relationship_type)
            .order_by(EntityRelationship.id)
            .all()
        )

    def get_relationships(self) -> list[EntityRelationship]:
        return self.db.query(EntityRelationship).order_by(EntityRelationship.id).all()
