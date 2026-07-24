"""Retrieval service for budgets, projects, and companies.

Provides structured retrieval methods used by the context builder.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Company, Project, Budget


class RetrievalService:
    def __init__(self, db: Session):
        self.db = db

    def get_company_by_name(self, name: str) -> Optional[Company]:
        stmt = select(Company).where(Company.name == name)
        return self.db.execute(stmt).scalars().first()

    def list_companies(self, limit: int = 100) -> List[Company]:
        stmt = select(Company).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_project(self, project_id: str) -> Optional[Project]:
        return self.db.get(Project, project_id)

    def list_projects(self, limit: int = 100) -> List[Project]:
        stmt = select(Project).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_budget(self, budget_id: str) -> Optional[Budget]:
        return self.db.get(Budget, budget_id)

    def list_budgets(self, limit: int = 100) -> List[Budget]:
        stmt = select(Budget).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def projects_for_company(self, company_id: str) -> List[Project]:
        stmt = select(Project).where(Project.lead_company_id == company_id)
        return list(self.db.execute(stmt).scalars().all())

    def budgets_for_company(self, company_id: str) -> List[Budget]:
        # budgets related to company via projects
        stmt = (
            select(Budget)
            .join(Project, Budget.id == Project.budget_id)
            .where(Project.lead_company_id == company_id)
        )
        return list(self.db.execute(stmt).scalars().all())
