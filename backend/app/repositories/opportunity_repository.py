from sqlalchemy.orm import Session

from app.models.opportunity import OpportunityScore, ScoreBreakdown


class OpportunityRepository:
    """Repository for storing and retrieving opportunity scores."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_score(self, score: OpportunityScore, breakdowns: list[ScoreBreakdown]) -> OpportunityScore:
        # Attach breakdowns and persist
        self.db.add(score)
        self.db.flush()
        for b in breakdowns:
            b.opportunity_score_id = score.id
            self.db.add(b)
        self.db.commit()
        self.db.refresh(score)
        return score

    def get_latest_score(self, company_id: str) -> OpportunityScore | None:
        return (
            self.db.query(OpportunityScore)
            .filter(OpportunityScore.company_id == company_id)
            .order_by(OpportunityScore.created_at.desc())
            .first()
        )

    def get_company_history(self, company_id: str) -> list[OpportunityScore]:
        return (
            self.db.query(OpportunityScore)
            .filter(OpportunityScore.company_id == company_id)
            .order_by(OpportunityScore.created_at.desc())
            .all()
        )

    def get_top(self, limit: int = 10) -> list[OpportunityScore]:
        return (
            self.db.query(OpportunityScore)
            .order_by(OpportunityScore.total_score.desc())
            .limit(limit)
            .all()
        )
