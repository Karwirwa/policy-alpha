from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.company import Company
from app.models.agency import Agency
from app.models.project import Project
from app.models.evidence import Evidence
from app.models.opportunity import OpportunityScore
from app.models.portfolio import InvestmentSimulation, OpportunityScoreHistory

router = APIRouter(prefix="/api/v1/stats", tags=["stats"]) 


@router.get("")
def get_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    # basic counts
    total_companies = db.query(func.count(Company.id)).scalar() or 0
    total_agencies = db.query(func.count(Agency.id)).scalar() or 0
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    total_evidence = db.query(func.count(Evidence.id)).scalar() or 0
    total_opportunities = db.query(func.count(OpportunityScore.id)).scalar() or 0

    # portfolio value: sum of current_price * shares
    portfolio_value = db.query(func.coalesce(func.sum(InvestmentSimulation.current_price * InvestmentSimulation.shares), 0.0)).scalar() or 0.0

    # active watchlist count (use watchlist table if present)
    try:
        from app.models.portfolio import Watchlist

        active_watchlist = db.query(func.count(Watchlist.id)).scalar() or 0
    except Exception:
        active_watchlist = 0

    # simple opportunity trend / evidence growth for last 6 months
    def monthly_counts(model, date_col_name: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        today = datetime.utcnow()
        for i in range(5, -1, -1):
            start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            month_str = start.strftime("%Y-%m")
            # filter using strftime for SQLite compatibility
            count = (
                db.query(func.count(getattr(model, date_col_name)))
                .filter(func.strftime("%Y-%m", getattr(model, date_col_name)) == month_str)
                .scalar()
            )
            results.append({"month": month_str, "count": count or 0})
        return results

    opportunity_trend = []
    evidence_growth = []
    try:
        opportunity_trend = monthly_counts(OpportunityScoreHistory, "generated_at")
    except Exception:
        opportunity_trend = []

    try:
        evidence_growth = monthly_counts(Evidence, "created_at")
    except Exception:
        try:
            evidence_growth = monthly_counts(Evidence, "extracted_at")
        except Exception:
            evidence_growth = []

    return {
        "total_companies": total_companies,
        "total_agencies": total_agencies,
        "total_projects": total_projects,
        "total_evidence": total_evidence,
        "total_opportunities": total_opportunities,
        "portfolio_value": float(portfolio_value),
        "active_watchlist": active_watchlist,
        "opportunity_trend": opportunity_trend,
        "evidence_growth": evidence_growth,
        "government_spending": [],
        "procurement_stages": [],
    }
