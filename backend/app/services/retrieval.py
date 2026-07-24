"""Simple retrieval service for Milestone 2.

Provides basic SQL retrieval for documents, chunks, companies, and bills.
This intentionally uses plain SQLAlchemy queries (no vector search).
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Document, DocumentChunk, Company, Bill, Mention


class RetrievalService:
    """Deterministic retrieval of stored entities for downstream reasoning."""

    def __init__(self, db: Session):
        self.db = db

    def get_document(self, document_id: str) -> Optional[Document]:
        return self.db.get(Document, document_id)

    def get_document_chunks(self, document_id: str, limit: int = 100) -> List[DocumentChunk]:
        stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.position).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def list_documents(self, limit: int = 100, offset: int = 0) -> List[Document]:
        stmt = select(Document).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def companies_mentioned_in_document(self, document_id: str) -> List[Company]:
        stmt = select(Company).join(Mention).where(Mention.document_id == document_id).limit(100)
        return list(self.db.execute(stmt).scalars().all())

    def bills_mentioned_in_document(self, document_id: str) -> List[Bill]:
        stmt = select(Bill).join(Mention).where(Mention.document_id == document_id).limit(100)
        return list(self.db.execute(stmt).scalars().all())
