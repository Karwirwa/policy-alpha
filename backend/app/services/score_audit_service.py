from typing import List
from sqlalchemy.orm import Session

from app.repositories.prediction_repository import PredictionRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.models.prediction import PredictionRecord


class ScoreAuditService:
    def __init__(self, db: Session):
        self.db = db
        self.pred_repo = PredictionRepository(db)
        self.op_repo = OpportunityRepository(db)

    def company_history(self, company_id: str) -> List[dict]:
        preds = self.pred_repo.list_by_company(company_id)
        out = []
        for p in preds:
            out.append({
                "uuid": p.uuid,
                "prediction_date": p.prediction_date,
                "score": p.score,
                "recommendation": p.recommendation,
                "actual_return": p.actual_return,
                "prediction_correct": p.prediction_correct,
                "confidence": p.confidence,
            })
        return out

    def prediction_history(self) -> List[dict]:
        preds = self.pred_repo.list_all()
        return [
            {
                "uuid": p.uuid,
                "company_id": p.company_id,
                "prediction_date": p.prediction_date,
                "score": p.score,
                "recommendation": p.recommendation,
                "actual_return": p.actual_return,
                "prediction_correct": p.prediction_correct,
            }
            for p in preds
        ]

    def factor_history(self, factor_name: str):
        # read factor performance
        fps = self.pred_repo.list_factors()
        for f in fps:
            if f.factor_name == factor_name:
                return {
                    "factor_name": f.factor_name,
                    "weight_used": f.weight_used,
                    "average_accuracy": f.average_accuracy,
                    "recommended_weight": f.recommended_weight,
                    "samples": f.samples,
                }
        return None
