from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.opportunity_repository import OpportunityRepository
from app.services.opportunity_scoring import OpportunityScoringService
from app.schemas.opportunity import OpportunityResponse, BreakdownItem, TopOpportunityItem

router = APIRouter(prefix="/api/v1/opportunity", tags=["opportunity"])


def get_repo(db: Session = Depends(get_db)) -> OpportunityRepository:
    return OpportunityRepository(db)


@router.get("/company/{company_name}", response_model=OpportunityResponse)
def get_company_opportunity(company_name: str, db: Session = Depends(get_db)) -> OpportunityResponse:
    scorer = OpportunityScoringService(db)
    repo = OpportunityRepository(db)
    try:
        score_obj, breakdowns = scorer.score_company(company_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    # Save score
    saved = repo.save_score(score_obj, breakdowns)

    supporting = [b.evidence_id for b in []]

    response = OpportunityResponse(
        company_id=saved.company_id,
        total_score=saved.total_score,
        confidence=saved.confidence,
        recommendation=saved.recommendation,
        explanation=saved.explanation,
        breakdown=[BreakdownItem(factor=b.factor, weight=b.weight, score=b.score, explanation=b.explanation) for b in saved.breakdowns],
        supporting_evidence_ids=supporting,
    )
    return response


@router.get("/top", response_model=list[TopOpportunityItem])
def get_top_opportunities(limit: int = 10, db: Session = Depends(get_db)) -> list[TopOpportunityItem]:
    repo = OpportunityRepository(db)
    top = repo.get_top(limit)
    return [TopOpportunityItem(company_id=t.company_id, total_score=t.total_score, recommendation=t.recommendation, created_at=t.created_at) for t in top]
