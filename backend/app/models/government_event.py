import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class EventType(str, enum.Enum):
    BUDGET_APPROVED = "BUDGET_APPROVED"
    BUDGET_INCREASED = "BUDGET_INCREASED"
    BUDGET_REDUCED = "BUDGET_REDUCED"
    TENDER_PUBLISHED = "TENDER_PUBLISHED"
    TENDER_AWARDED = "TENDER_AWARDED"
    PROCUREMENT_STARTED = "PROCUREMENT_STARTED"
    PROCUREMENT_COMPLETED = "PROCUREMENT_COMPLETED"
    PROJECT_STARTED = "PROJECT_STARTED"
    PROJECT_DELAYED = "PROJECT_DELAYED"
    PROJECT_COMPLETED = "PROJECT_COMPLETED"
    CONTRACT_SIGNED = "CONTRACT_SIGNED"
    CONTRACT_EXTENDED = "CONTRACT_EXTENDED"
    COMPANY_MENTIONED = "COMPANY_MENTIONED"
    COMPANY_BLACKLISTED = "COMPANY_BLACKLISTED"
    POLICY_CREATED = "POLICY_CREATED"
    POLICY_UPDATED = "POLICY_UPDATED"
    POLICY_REPEALED = "POLICY_REPEALED"
    REGULATION_CREATED = "REGULATION_CREATED"


class GovernmentEvent(Base, TimestampMixin):
    __tablename__ = "government_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type", native_enum=False), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    detected_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_document_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("document.id"), nullable=True, index=True)
    evidence_id: Mapped[int | None] = mapped_column(ForeignKey("evidence.id"), nullable=True, index=True)
    country_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("country.id"), nullable=True, index=True)

    # relationships
    evidence = relationship("Evidence")
    document = relationship("Document")
