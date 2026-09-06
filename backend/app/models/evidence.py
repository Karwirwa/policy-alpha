from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Evidence(Base, TimestampMixin):
    """Canonical evidence object for government document intelligence."""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(128), ForeignKey("document.id"), nullable=False, index=True)
    country_id: Mapped[str] = mapped_column(String(128), ForeignKey("country.id"), nullable=False, index=True)
    agency_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("agency.id"), nullable=True, index=True)
    company_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("company.id"), nullable=True, index=True)
    project_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("project.id"), nullable=True, index=True)
    budget_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("budget.id"), nullable=True, index=True)
    procurement_id: Mapped[str | None] = mapped_column(String(128), ForeignKey("tender.id"), nullable=True, index=True)
    extracted_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    normalized_keywords: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    detected_entities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section: Mapped[str | None] = mapped_column(String(128), nullable=True)
    document_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    connector_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    government_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    publication_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_verified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_reference: Mapped[str] = mapped_column(String(256), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    document: Mapped["Document"] = relationship("Document", back_populates="evidence")
    country: Mapped["Country"] = relationship("Country", back_populates="evidence")
    agency: Mapped["Agency"] = relationship("Agency", back_populates="evidence")
    company: Mapped["Company"] = relationship("Company", back_populates="evidence")
    project: Mapped["Project"] = relationship("Project", back_populates="evidence")
    budget: Mapped["Budget"] = relationship("Budget", back_populates="evidence")
    tender: Mapped["Tender"] = relationship("Tender", back_populates="evidence")
    relationships: Mapped[list["EntityRelationship"]] = relationship(
        "EntityRelationship",
        back_populates="evidence",
        cascade="all, delete-orphan",
    )
