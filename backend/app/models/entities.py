"""Minimal domain models for Milestone 2 (vertical slice).

This module defines intentionally small SQLAlchemy models required for the
end-to-end pipeline proof-of-concept. Use UUID primary keys and TimestampMixin
for created/updated times.
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


def _uuid() -> str:
    return str(uuid4())


class Country(Base, TimestampMixin):
    """A country where government sources originate."""

    __tablename__ = "countries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(8), nullable=True)

    sources = relationship("GovernmentSource", back_populates="country", cascade="all, delete-orphan")


class GovernmentSource(Base, TimestampMixin):
    """A publisher of government documents (minimally represented)."""

    __tablename__ = "government_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=True)
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"), nullable=True)

    country = relationship("Country", back_populates="sources")
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")


class Document(Base, TimestampMixin):
    """A parsed government document. Text is stored here for the MVP."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(1000), nullable=True)
    source_url: Mapped[str] = mapped_column(String(2000), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    government_source_id: Mapped[str] = mapped_column(ForeignKey("government_sources.id"), nullable=True)

    source = relationship("GovernmentSource", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    mentions = relationship("Mention", back_populates="document", cascade="all, delete-orphan")
    analyses = relationship("AIAnalysis", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base, TimestampMixin):
    """A chunked portion of a document used for retrieval.

    The chunking strategy in Milestone 2 is simple and deterministic.
    """

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=True)
    end_char: Mapped[int] = mapped_column(Integer, nullable=True)

    document = relationship("Document", back_populates="chunks")


class Company(Base, TimestampMixin):
    """A minimal company entity that may be mentioned in documents."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(1000), nullable=False)

    mentions = relationship("Mention", back_populates="company", cascade="all, delete-orphan")


class Bill(Base, TimestampMixin):
    """A minimal bill/legislative instrument entity."""

    __tablename__ = "bills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    identifier: Mapped[str] = mapped_column(String(255), nullable=True)

    mentions = relationship("Mention", back_populates="bill", cascade="all, delete-orphan")


class Mention(Base, TimestampMixin):
    """A mention of a company or bill inside a document or chunk.

    Keep intentionally small: link to document and optionally to company or bill.
    """

    __tablename__ = "mentions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=True)
    bill_id: Mapped[str] = mapped_column(ForeignKey("bills.id"), nullable=True)
    snippet: Mapped[str] = mapped_column(Text, nullable=True)
    start_char: Mapped[int] = mapped_column(Integer, nullable=True)
    end_char: Mapped[int] = mapped_column(Integer, nullable=True)

    document = relationship("Document", back_populates="mentions")
    company = relationship("Company", back_populates="mentions")
    bill = relationship("Bill", back_populates="mentions")


class AIAnalysis(Base, TimestampMixin):
    """Placeholder for future AI analysis results linked to documents or companies.

    For Milestone 2 this stores mock summaries and structured placeholders.
    """

    __tablename__ = "ai_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)

    document = relationship("Document", back_populates="analyses")
    # company relationship intentionally omitted; can be added later if needed


class Budget(Base, TimestampMixin):
    """A simplified budget entity representing a programme-level allocation."""

    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    ministry: Mapped[str] = mapped_column(String(255), nullable=False)
    program: Mapped[str] = mapped_column(String(1000), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    sector: Mapped[str] = mapped_column(String(255), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)

    projects = relationship("Project", back_populates="budget", cascade="all, delete-orphan")


class Project(Base, TimestampMixin):
    """A project funded under a budget/programme."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    project_id: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=True)
    start_date: Mapped[str] = mapped_column(String(50), nullable=True)
    end_date: Mapped[str] = mapped_column(String(50), nullable=True)
    lead_company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=True)
    budget_id: Mapped[str] = mapped_column(ForeignKey("budgets.id"), nullable=True)

    lead_company = relationship("Company")
    budget = relationship("Budget", back_populates="projects")
