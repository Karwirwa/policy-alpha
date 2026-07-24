"""Repository for Company-related DB operations.

Intentionally small API: create, get_by_id, list, simple_search.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Company


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Company:
        c = Company(name=name)
        self.db.add(c)
        self.db.commit()
        self.db.refresh(c)
        return c

    def get_by_id(self, company_id: str) -> Optional[Company]:
        return self.db.get(Company, company_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[Company]:
        stmt = select(Company).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def simple_search(self, query: str, limit: int = 50) -> List[Company]:
        stmt = select(Company).where(Company.name.ilike(f"%{query}%")).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
