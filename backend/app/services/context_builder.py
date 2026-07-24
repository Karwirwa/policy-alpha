"""Build structured context for a given company.

The context contains: company, relevant projects, relevant budgets, evidence,
and a short deterministic summary. This component does NOT call any AI.
"""
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.services.retrieval_service import RetrievalService


def build_context_for_company(db: Session, company_name: str) -> Dict[str, Any]:
    retrieval = RetrievalService(db)
    company = retrieval.get_company_by_name(company_name)
    if not company:
        return {"company": company_name, "error": "company_not_found"}

    projects = retrieval.projects_for_company(company.id)
    budgets = retrieval.budgets_for_company(company.id)

    # Build evidence entries
    evidence: List[Dict[str, Any]] = []
    for p in projects:
        evidence.append({
            "type": "project",
            "id": p.id,
            "project_id": p.project_id,
            "title": p.title,
            "amount": p.amount,
            "budget_id": p.budget_id,
        })
    for b in budgets:
        evidence.append({
            "type": "budget",
            "id": b.id,
            "program": b.program,
            "amount": b.amount,
            "year": b.year,
            "country": b.country,
        })

    summary_lines = []
    summary_lines.append(f"Company: {company.name}")
    if projects:
        summary_lines.append(f"Projects count: {len(projects)}")
    if budgets:
        summary_lines.append(f"Related budgets: {len(budgets)}")

    summary = " | ".join(summary_lines)

    context = {
        "company": {"id": company.id, "name": company.name},
        "projects": [
            {
                "id": p.id,
                "project_id": p.project_id,
                "title": p.title,
                "description": p.description,
                "amount": p.amount,
                "start_date": p.start_date,
                "end_date": p.end_date,
            }
            for p in projects
        ],
        "budgets": [
            {"id": b.id, "program": b.program, "amount": b.amount, "year": b.year, "country": b.country}
            for b in budgets
        ],
        "evidence": evidence,
        "summary": summary,
    }

    return context
