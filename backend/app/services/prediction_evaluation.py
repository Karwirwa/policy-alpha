from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.repositories.prediction_repository import PredictionRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.models.prediction import PredictionRecord


class PredictionEvaluationService:
    """Evaluate past predictions against actual outcomes deterministically."""

    # Deterministic thresholds for recommendation correctness
    RECOMMENDATION_THRESHOLDS = {
        "Strong Buy": 10.0,  # expect >=10% return
        "High Opportunity": 5.0,  # expect >=5% return
        "Buy": 5.0,
        "Watch Closely": 0.0,  # expect non-negative return
        "Neutral": -2.0,  # consider within -2%..2% as acceptable
        "Low Opportunity": -1.0,  # expect non-positive return
    }

    def __init__(self, db: Session):
        self.db = db
        self.repo = PredictionRepository(db)
        self.op_repo = OpportunityRepository(db)

    def evaluate_prediction(self, pred: PredictionRecord) -> PredictionRecord:
        # If there's no actual return recorded, cannot evaluate conclusively
        if pred.actual_return is None:
            pred.prediction_correct = False
            self.repo.save_prediction(pred)
            return pred

        thresh = self.RECOMMENDATION_THRESHOLDS.get(pred.recommendation, 0.0)
        actual = pred.actual_return
        correct = False
        explanation = ""
        if pred.recommendation in ("Strong Buy", "High Opportunity", "Buy"):
            correct = actual >= thresh
            explanation = f"Expected at least {thresh}%, actual {actual}% -> {'correct' if correct else 'incorrect'}"
        elif pred.recommendation == "Watch Closely":
            correct = actual >= 0.0
            explanation = f"Expected non-negative return, actual {actual}% -> {'correct' if correct else 'incorrect'}"
        elif pred.recommendation == "Neutral":
            correct = abs(actual) <= abs(thresh)
            explanation = f"Expected near-zero change within {thresh}%, actual {actual}% -> {'correct' if correct else 'incorrect'}"
        elif pred.recommendation == "Low Opportunity":
            correct = actual <= 0.0
            explanation = f"Expected non-positive return, actual {actual}% -> {'correct' if correct else 'incorrect'}"
        else:
            # default fallback: positive return considered success
            correct = actual >= 0.0
            explanation = f"Default check: actual {actual}% -> {'correct' if correct else 'incorrect'}"

        pred.prediction_correct = bool(correct)
        pred.confidence = float(pred.confidence or 0.0)
        self.repo.save_prediction(pred)
        return pred

    def evaluate_company(self, company_id: str) -> dict:
        preds = self.repo.list_by_company(company_id)
        if not preds:
            return {"company_id": company_id, "evaluated": 0, "accuracy": 0.0}
        evaluated = 0
        correct = 0
        for p in preds:
            evaluated += 1
            self.evaluate_prediction(p)
            if p.prediction_correct:
                correct += 1
        accuracy = correct / evaluated if evaluated else 0.0
        return {"company_id": company_id, "evaluated": evaluated, "accuracy": accuracy}

    def evaluate_all(self) -> dict:
        preds = self.repo.list_all()
        if not preds:
            return {"evaluated": 0, "accuracy": 0.0}
        evaluated = 0
        correct = 0
        for p in preds:
            evaluated += 1
            self.evaluate_prediction(p)
            if p.prediction_correct:
                correct += 1
        accuracy = correct / evaluated if evaluated else 0.0
        return {"evaluated": evaluated, "accuracy": accuracy}
