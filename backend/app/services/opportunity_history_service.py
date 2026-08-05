from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.opportunity_history_repository import OpportunityHistoryRepository
from app.models.portfolio import OpportunityScoreHistory


class OpportunityHistoryService:
    def __init__(self, db: Session):
        self.repo = OpportunityHistoryRepository(db)

    def save_score(self, company_id: str, score: float, recommendation: str, generated_at: datetime | None = None) -> OpportunityScoreHistory:
        generated_at = generated_at or datetime.utcnow()
        hist = OpportunityScoreHistory(company_id=company_id, score=score, recommendation=recommendation, generated_at=generated_at)
        return self.repo.save(hist)

    def company_history(self, company_id: str):
        return self.repo.get_company_history(company_id)

    def score_timeline(self, company_id: str):
        histories = self.repo.get_company_history(company_id)
        return [{"score": h.score, "recommendation": h.recommendation, "generated_at": h.generated_at} for h in histories]
