import enum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, TimestampMixin


class RelationshipType(str, enum.Enum):
    AWARDED = "AWARDED"
    FUNDED_BY = "FUNDED_BY"
    MANAGED_BY = "MANAGED_BY"
    LOCATED_IN = "LOCATED_IN"
    MENTIONS = "MENTIONS"
    SUPPLIES = "SUPPLIES"


class EntityRelationship(Base, TimestampMixin):
    __tablename__ = "entity_relationship"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType, name="relationship_type", native_enum=False), nullable=False
    )
    target_entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    evidence_id: Mapped[int | None] = mapped_column(ForeignKey("evidence.id"), nullable=True, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    evidence: Mapped[Optional["Evidence"]] = relationship("Evidence", back_populates="relationships")
