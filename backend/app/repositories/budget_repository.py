"""Repository for Budget access.

Simple methods: insert, update, get_by_id, list, find_by_year.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Budget


class BudgetRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, payload: dict) -> Budget:
        b = Budget(
            country=payload["country"],
            ministry=payload["ministry"],
            program=payload["program"],
            amount=payload["amount"],
            currency=payload.get("currency"),
            year=payload["year"],
            sector=payload.get("sector"),
            summary=payload.get("summary"),
            source_document_id=payload.get("source_document_id"),
            source_page=payload.get("source_page"),
            source_section=payload.get("source_section"),
            extraction_date=payload.get("extraction_date"),
        )
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return b

    def update(self, budget_id: str, patch: dict) -> Optional[Budget]:
        b = self.db.get(Budget, budget_id)
        if not b:
            return None
        for k, v in patch.items():
            setattr(b, k, v)
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return b

    def get_by_id(self, budget_id: str) -> Optional[Budget]:
        return self.db.get(Budget, budget_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[Budget]:
        stmt = select(Budget).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def find_by_year(self, year: int) -> List[Budget]:
        stmt = select(Budget).where(Budget.year == year)
        return list(self.db.execute(stmt).scalars().all())
