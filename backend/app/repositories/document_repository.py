"""Repository for Document-related DB operations.

Keep the interface intentionally small: create, get_by_id, list, simple_search.
"""
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.entities import Document


class DocumentRepository:
    """Simple repository for Document CRUD and searches."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, *, title: Optional[str], text: str, source_url: Optional[str] = None, government_source_id: Optional[str] = None) -> Document:
        doc = Document(title=title, text=text, source_url=source_url, government_source_id=government_source_id)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_by_id(self, doc_id: str) -> Optional[Document]:
        return self.db.get(Document, doc_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[Document]:
        stmt = select(Document).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def simple_search(self, query: str, limit: int = 50) -> List[Document]:
        # Very small, naive search using case-insensitive match on title and text
        stmt = select(Document).where(
            (Document.title.ilike(f"%{query}%")) | (Document.text.ilike(f"%{query}%"))
        ).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
