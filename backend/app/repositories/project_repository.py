"""Repository for Project access.

Simple methods: insert, update, get_by_id, list, find_by_company.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(self, payload: dict) -> Project:
        p = Project(
            project_id=payload.get("project_id"),
            title=payload.get("title"),
            description=payload.get("description"),
            amount=payload.get("amount"),
            start_date=payload.get("start_date"),
            end_date=payload.get("end_date"),
            lead_company_id=payload.get("lead_company_id"),
            budget_id=payload.get("budget_id"),
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def update(self, project_id: str, patch: dict) -> Optional[Project]:
        p = self.db.get(Project, project_id)
        if not p:
            return None
        for k, v in patch.items():
            setattr(p, k, v)
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    def get_by_id(self, project_id: str) -> Optional[Project]:
        return self.db.get(Project, project_id)

    def list(self, limit: int = 100, offset: int = 0) -> List[Project]:
        stmt = select(Project).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def find_by_company(self, company_id: str) -> List[Project]:
        stmt = select(Project).where(Project.lead_company_id == company_id)
        return list(self.db.execute(stmt).scalars().all())
