"""Repository for Bill-related DB operations.

Small API: create, get_by_id, list, simple_search.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Bill


class BillRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, identifier: Optional[str] = None) -> Bill:
        b = Bill(title=title, identifier=identifier)
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return b

    def get_by_id(self, bill_id: str) -> Optional[Bill]:
        return self.db.get(Bill, bill_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[Bill]:
        stmt = select(Bill).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def simple_search(self, query: str, limit: int = 50) -> List[Bill]:
        stmt = select(Bill).where((Bill.title.ilike(f"%{query}%")) | (Bill.identifier.ilike(f"%{query}%"))).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
