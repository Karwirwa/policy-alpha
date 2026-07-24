"""Ingest a PDF budget document into the database.

This script:
- Ensures database has evidence columns (adds them if missing for SQLite)
- Extracts PDF structure using document_extractor
- Converts extracted structure into payload via parser_service
- Creates a Document record pointing to the PDF file
- Persists Budget and Project records with evidence fields linking back to the document

No AI is used.
"""
from pathlib import Path
import sys
from datetime import datetime

from sqlalchemy import text

from app.db.database import engine, SessionLocal
from app.db.base import Base
from app.models.entities import Document
from app.services.document_extractor import extract_pdf
from app.services.parser_service import prepare_from_extracted_pdf
from app.repositories.budget_repository import BudgetRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.company_repository import CompanyRepository


DEFAULT_PDF = Path(__file__).parents[1] / "data" / "sample" / "budget.pdf"


def _ensure_evidence_columns():
    # For SQLite, add columns if they don't exist. This is a pragmatic approach
    # for the milestone; in production use Alembic migrations.
    with engine.connect() as conn:
        # budgets: source_document_id, source_page, source_section, extraction_date
        res = conn.execute(text("PRAGMA table_info(budgets);"))
        cols = [r[1] for r in res.fetchall()]
        if "source_document_id" not in cols:
            conn.execute(text("ALTER TABLE budgets ADD COLUMN source_document_id VARCHAR(36);"))
        if "source_page" not in cols:
            conn.execute(text("ALTER TABLE budgets ADD COLUMN source_page INTEGER;"))
        if "source_section" not in cols:
            conn.execute(text("ALTER TABLE budgets ADD COLUMN source_section INTEGER;"))
        if "extraction_date" not in cols:
            conn.execute(text("ALTER TABLE budgets ADD COLUMN extraction_date DATETIME;"))

        # projects: source_page, source_section, source_paragraph
        res = conn.execute(text("PRAGMA table_info(projects);"))
        cols = [r[1] for r in res.fetchall()]
        if "source_page" not in cols:
            conn.execute(text("ALTER TABLE projects ADD COLUMN source_page INTEGER;"))
        if "source_section" not in cols:
            conn.execute(text("ALTER TABLE projects ADD COLUMN source_section INTEGER;"))
        if "source_paragraph" not in cols:
            conn.execute(text("ALTER TABLE projects ADD COLUMN source_paragraph INTEGER;"))


def concatenate_pages_text(extracted: dict) -> str:
    return "\n\n".join(p.get("raw_text", "") for p in extracted.get("pages", []))


def main(pdf_path: Path | None = None):
    if pdf_path is None:
        pdf_path = DEFAULT_PDF

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return

    # Ensure evidence columns exist in DB tables
    _ensure_evidence_columns()

    extracted = extract_pdf(pdf_path)
    payload = prepare_from_extracted_pdf(extracted)

    # Persist a Document record for source tracing
    db = SessionLocal()
    try:
        # create document with concatenated text
        text_content = concatenate_pages_text(extracted)
        doc = Document(title=pdf_path.name, source_url=str(pdf_path), text=text_content, published_at=None)
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # prepare repository instances
        budget_repo = BudgetRepository(db)
        project_repo = ProjectRepository(db)
        company_repo = CompanyRepository(db)

        # companies
        company_map = {}
        for c in payload.get("companies", []):
            name = c.get("name")
            existing = None
            for ex in company_repo.simple_search(name):
                if ex.name == name:
                    existing = ex
                    break
            if existing:
                company_map[name] = existing
            else:
                created = company_repo.create(name)
                company_map[name] = created

        # budget payload augmentation with source evidence
        budget_payload = {
            "country": payload.get("country"),
            "ministry": payload.get("ministry"),
            "program": payload.get("program"),
            "amount": payload.get("budget"),
            "currency": payload.get("currency"),
            "year": payload.get("year"),
            "sector": payload.get("sector"),
            "summary": payload.get("summary"),
            "source_document_id": doc.id,
            # top-level source location not always available; leave page/section None
            "source_page": None,
            "source_section": None,
            "extraction_date": extracted.get("extracted_at"),
        }

        # insert budget (avoid duplicates by program+year)
        existing_budgets = budget_repo.find_by_year(budget_payload["year"]) if budget_payload.get("year") else []
        budget = None
        for eb in existing_budgets:
            if eb.program == budget_payload["program"] and eb.country == budget_payload["country"]:
                budget = eb
                break
        if not budget:
            budget = budget_repo.insert(budget_payload)

        # insert projects with evidence
        for p in payload.get("projects", []):
            evidence = p.get("evidence", {})
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
                "source_page": evidence.get("page"),
                "source_section": evidence.get("section"),
                "source_paragraph": evidence.get("paragraph"),
            }
            # skip if exists
            existing = None
            if proj_payload.get("project_id"):
                for ex in project_repo.list(limit=1000):
                    if ex.project_id == proj_payload.get("project_id"):
                        existing = ex
                        break
            if existing:
                continue
            project_repo.insert(proj_payload)

        print(f"Ingested PDF {pdf_path} -> Document ID: {doc.id}")
    finally:
        db.close()


if __name__ == "__main__":
    arg = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(arg)
