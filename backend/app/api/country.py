from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.agency import Agency
from app.models.company import Company
from app.models.project import Project
from app.models.tender import Tender
from app.models.evidence import Evidence
from app.models.document import Document
from app.models.opportunity import OpportunityScore
from app.repositories.evidence_repository import EvidenceRepository
from app.services.entity_resolution import EntityResolutionService

router = APIRouter(prefix="/api/v1/country", tags=["country"])


def _monthly_counts(db: Session, model, date_col_name: str, months: int = 12) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    today = datetime.utcnow()
    for i in range(months - 1, -1, -1):
        start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_str = start.strftime("%Y-%m")
        try:
            count = (
                db.query(func.count(getattr(model, date_col_name)))
                .filter(func.strftime("%Y-%m", getattr(model, date_col_name)) == month_str)
                .scalar()
            )
        except Exception:
            # fallback to 0 when model/date not present
            count = 0
        results.append({"month": month_str, "count": count or 0})
    return results


@router.get("/{country_name}")
def get_country_overview(country_name: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    resolver = EntityResolutionService()
    match = resolver.resolve_country(country_name)
    if not match.entity_id:
        raise HTTPException(status_code=404, detail=f"Country '{country_name}' not found")

    country_id = match.entity_id

    # largest ministries (agencies) by evidence count in country
    agency_counts = (
        db.query(Agency.id, Agency.name, func.count(Evidence.id).label("evidence_count"))
        .join(Evidence, Evidence.agency_id == Agency.id)
        .filter(Evidence.country_id == country_id)
        .group_by(Agency.id)
        .order_by(func.count(Evidence.id).desc())
        .limit(8)
        .all()
    )

    # largest projects by evidence count
    project_counts = (
        db.query(Project.id, Project.name, func.count(Evidence.id).label("evidence_count"))
        .join(Evidence, Evidence.project_id == Project.id)
        .filter(Evidence.country_id == country_id)
        .group_by(Project.id)
        .order_by(func.count(Evidence.id).desc())
        .limit(8)
        .all()
    )

    # top companies: join opportunity_score and evidence by company where evidence.country_id
    top_companies = []
    try:
        subq = (
            db.query(Evidence.company_id)
            .filter(Evidence.country_id == country_id)
            .subquery()
        )
        top = (
            db.query(OpportunityScore.company_id, OpportunityScore.total_score)
            .filter(OpportunityScore.company_id.in_(subq))
            .order_by(OpportunityScore.total_score.desc())
            .limit(10)
            .all()
        )
        top_companies = [{"company_id": t.company_id, "score": float(t.total_score)} for t in top]
    except Exception:
        top_companies = []

    # recent tenders and procurement: use Tender and Evidence with procurement_id
    recent_tenders = (
        db.query(Tender.id, Tender.name)
        .join(Evidence, Evidence.procurement_id == Tender.id)
        .filter(Evidence.country_id == country_id)
        .order_by(Evidence.extracted_at.desc())
        .limit(10)
        .all()
    )
    recent_tenders_list = [{"tender_id": t.id, "name": t.name} for t in recent_tenders]

    # opportunity score aggregate: average of latest opportunity scores for companies with evidence in country
    avg_opportunity = None
    try:
        subq = (
            db.query(Evidence.company_id)
            .filter(Evidence.country_id == country_id)
            .distinct()
            .subquery()
        )
        avg_opportunity = db.query(func.avg(OpportunityScore.total_score)).filter(OpportunityScore.company_id.in_(subq)).scalar() or 0.0
        avg_opportunity = float(avg_opportunity)
    except Exception:
        avg_opportunity = 0.0

    # evidence timeline
    evidence_timeline = (
        db.query(func.strftime("%Y-%m", Evidence.extracted_at).label("month"), func.count(Evidence.id).label("count"))
        .filter(Evidence.country_id == country_id)
        .group_by("month")
        .order_by("month")
        .all()
    )
    evidence_timeline_list = [{"month": r[0], "count": int(r[1])} for r in evidence_timeline]

    # procurement timeline: evidence with procurement_id
    procurement_timeline = (
        db.query(func.strftime("%Y-%m", Evidence.extracted_at).label("month"), func.count(Evidence.id).label("count"))
        .filter(Evidence.country_id == country_id, Evidence.procurement_id != None)
        .group_by("month")
        .order_by("month")
        .all()
    )
    procurement_timeline_list = [{"month": r[0], "count": int(r[1])} for r in procurement_timeline]

    # recent government documents: distinct documents referenced by evidence in country
    docs = (
        db.query(Document.id, Document.name, Document.source_reference)
        .join(Evidence, Evidence.document_id == Document.id)
        .filter(Evidence.country_id == country_id)
        .order_by(Evidence.extracted_at.desc())
        .limit(12)
        .all()
    )
    recent_documents = [{"id": d.id, "name": d.name, "source_reference": d.source_reference} for d in docs]

    # basic map data: list of projects (names) — frontend map can be enriched later
    map_projects = [{"project_id": p.id, "name": p.name} for p in db.query(Project).all()][:20]

    response = {
        "country": {"id": country_id, "name": match.canonical_name or country_name},
        "government_spending": [],
        "largest_ministries": [{"agency_id": a.id, "name": a.name, "evidence_count": c} for (a_id, a_name, c) in [(r[0], r[1], r[2]) for r in agency_counts]],
        "largest_projects": [{"project_id": p.id, "name": p.name, "evidence_count": c} for (p_id, p_name, c) in [(r[0], r[1], r[2]) for r in project_counts]],
        "top_companies": top_companies,
        "recent_tenders": recent_tenders_list,
        "recent_procurement": [],
        "opportunity_score": avg_opportunity,
        "economic_indicators": [],
        "evidence_timeline": evidence_timeline_list,
        "procurement_timeline": procurement_timeline_list,
        "map_projects": map_projects,
        "recent_documents": recent_documents,
    }

    return response
