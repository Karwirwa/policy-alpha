"""API endpoints for analysis operations."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

from app.db.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.context_builder import build_context_for_company
from app.services.ai_service import analyze_company_with_context

router = APIRouter(prefix="/api/v1")


class CompanyRequest(BaseModel):
    company: str


@router.post("/analyze/company")
def analyze_company(req: CompanyRequest, db: Session = Depends(get_db)) -> Dict:
    context = build_context_for_company(db, req.company)
    if context.get("error"):
        raise HTTPException(status_code=404, detail="company not found")

    analysis = analyze_company_with_context(context)
    return analysis
