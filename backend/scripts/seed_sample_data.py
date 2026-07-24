"""Seed database from backend/data/sample/housing_budget_2026.json

This script uses parser_service to load the JSON and repository classes to
persist Budget, Company, and Project records. It creates tables if missing.
"""
from pathlib import Path
import json

from app.db.database import engine, SessionLocal
from app.db.base import Base
from app.services.parser_service import load_json, prepare_budget_payload
from app.repositories.budget_repository import BudgetRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.company_repository import CompanyRepository


DATA_PATH = Path(__file__).parents[1] / "data" / "sample" / "housing_budget_2026.json"


def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    raw = load_json(DATA_PATH)
    payload = prepare_budget_payload(raw)

    db = SessionLocal()
    try:
        budget_repo = BudgetRepository(db)
        project_repo = ProjectRepository(db)
        company_repo = CompanyRepository(db)

        # Insert or reuse companies
        company_map = {}
        for c in payload.get("companies", []):
            name = c.get("name")
            existing = None
            # naive exact name check
            for ex in company_repo.simple_search(name):
                if ex.name == name:
                    existing = ex
                    break
            if existing:
                company_map[name] = existing
            else:
                created = company_repo.create(name)
                company_map[name] = created

        # Insert budget
        budget = budget_repo.insert(payload)

        # Insert projects and link to companies and budget
        for p in payload.get("projects", []):
            lead = p.get("lead_company")
            lead_company = company_map.get(lead)
            proj_payload = {
                "project_id": p.get("project_id"),
                "title": p.get("title"),
                "description": p.get("description"),
                "amount": p.get("amount"),
                "start_date": p.get("start_date"),
                "end_date": p.get("end_date"),
                "lead_company_id": lead_company.id if lead_company else None,
                "budget_id": budget.id,
            }
            project_repo.insert(proj_payload)

        print("Seed completed: budget, companies, and projects inserted.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
