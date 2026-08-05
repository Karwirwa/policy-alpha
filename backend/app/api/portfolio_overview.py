from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio-overview"])


@router.get("/{uuid}/overview")
def portfolio_overview(uuid: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return a lightweight overview for frontend portfolio dashboard."""
    svc = PortfolioService(db)
    repo = svc.repo
    sim_repo = svc.sim_repo

    portfolio = repo.get_by_uuid(uuid)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    positions = repo.get_positions(portfolio.id)
    company_ids = [p.company_id for p in positions]

    # gather simulations for portfolio companies
    sims = sim_repo.list()
    portfolio_sims = [s for s in sims if s.company_id in company_ids]

    total_invested = sum((s.buy_price * s.shares) for s in portfolio_sims) if portfolio_sims else 0.0
    total_profit_loss = sum((s.profit_loss) for s in portfolio_sims) if portfolio_sims else 0.0
    projected_return = (total_profit_loss / total_invested * 100.0) if total_invested and total_profit_loss else (sum((s.percent_return) for s in portfolio_sims) / len(portfolio_sims) if portfolio_sims else 0.0)

    # government exposure: fraction of companies with procurement evidence
    from app.repositories.evidence_repository import EvidenceRepository

    evidence_repo = EvidenceRepository(db)
    gov_exposed = 0
    for cid in company_ids:
        evs = evidence_repo.get_by_company(cid)
        if any(getattr(e, 'procurement_id', None) for e in evs):
            gov_exposed += 1
    government_exposure = (gov_exposed / len(company_ids) * 100.0) if company_ids else 0.0

    # country allocation (counts by country)
    country_counts: dict = {}
    for cid in company_ids:
        evs = evidence_repo.get_by_company(cid)
        for e in evs:
            if getattr(e, 'country_id', None):
                country_counts[e.country_id] = country_counts.get(e.country_id, 0) + 1
    country_allocation = [{"country_id": k, "count": v} for k, v in country_counts.items()]

    # sector allocation placeholder
    sector_allocation: list = []

    # risk score derived from average opportunity score
    summary = svc.portfolio_summary(uuid)
    avg_opportunity = summary.get("average_opportunity_score", 0.0)
    risk_score = max(0.0, 100.0 - avg_opportunity)

    historical_simulations = [
        {
            "uuid": s.uuid,
            "company_id": s.company_id,
            "buy_date": s.buy_date.isoformat() if s.buy_date else None,
            "buy_price": s.buy_price,
            "current_price": s.current_price,
            "shares": s.shares,
            "profit_loss": s.profit_loss,
            "percent_return": s.percent_return,
            "status": s.status,
        }
        for s in portfolio_sims
    ]

    return {
        "portfolio_uuid": portfolio.uuid,
        "total_invested": float(total_invested),
        "projected_return": float(projected_return),
        "government_exposure": float(government_exposure),
        "country_allocation": country_allocation,
        "sector_allocation": sector_allocation,
        "risk_score": float(risk_score),
        "opportunity_score": float(avg_opportunity),
        "historical_simulations": historical_simulations,
    }
