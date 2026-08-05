from sqlalchemy.orm import Session
from typing import List

from app.models.portfolio import OpportunityScoreHistory


class OpportunityHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, history: OpportunityScoreHistory) -> OpportunityScoreHistory:
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_company_history(self, company_id: str) -> List[OpportunityScoreHistory]:
        return self.db.query(OpportunityScoreHistory).filter(OpportunityScoreHistory.company_id == company_id).order_by(OpportunityScoreHistory.generated_at.asc()).all()
