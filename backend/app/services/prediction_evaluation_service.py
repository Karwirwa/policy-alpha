from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.repositories.prediction_repository import PredictionRepository
from app.models.prediction import PredictionRecord


class PredictionEvaluationService:
    """Service to evaluate predictions deterministically.

    Deterministic rules used:
    - A prediction's correctness is determined by comparing the stored actual_return to zero.
      If recommendation == 'buy' then correct iff actual_return > 0.0.
      If recommendation == 'sell' then correct iff actual_return < 0.0.
      For any other recommendation string, correctness is determined by sign agreement:
        - positive recommendation strings (contain 'buy' or 'long') => actual_return > 0
        - negative recommendation strings (contain 'sell' or 'short') => actual_return < 0
      If actual_return is None the prediction is not evaluated and skipped.

    The service intentionally avoids probabilistic decisions and external data dependencies.
    """

    def __init__(self, db: Session):
        self.repo = PredictionRepository(db)

    def evaluate_prediction(self, pred: PredictionRecord) -> PredictionRecord:
        """Evaluate a single PredictionRecord in-place and return it.

        Sets pred.prediction_correct to True/False if actual_return is present.
        Leaves it False if actual_return is None.
        """
        if pred.actual_return is None:
            # No ground truth yet; cannot evaluate
            return pred

        ret = float(pred.actual_return)
        rec = (pred.recommendation or "").lower()

        if rec == "buy":
            pred.prediction_correct = ret > 0.0
        elif rec == "sell":
            pred.prediction_correct = ret < 0.0
        else:
            # fallback deterministic rule: check keyword hints
            if "buy" in rec or "long" in rec or "positive" in rec:
                pred.prediction_correct = ret > 0.0
            elif "sell" in rec or "short" in rec or "negative" in rec:
                pred.prediction_correct = ret < 0.0
            else:
                # unknown recommendation type: consider prediction correct when abs(return) >= 0.0
                # this is intentionally deterministic: treat non-zero returns as signal
                pred.prediction_correct = ret != 0.0

        return pred

    def evaluate_company(self, company_id: str) -> Dict[str, Any]:
        """Evaluate all stored predictions for a single company.

        Returns a deterministic summary dict with:
        - company_id
        - total_predictions
        - evaluated (count with actual_return)
        - correct_count
        - accuracy (correct / evaluated) or None when no evaluated
        - explanations: short description of evaluation rule used
        """
        preds: List[PredictionRecord] = self.repo.list_by_company(company_id)
        evaluated = 0
        correct = 0
        for p in preds:
            if p.actual_return is None:
                continue
            evaluated += 1
            evaluated_pred = self.evaluate_prediction(p)
            if evaluated_pred.prediction_correct:
                correct += 1

        accuracy = (correct / evaluated) if evaluated > 0 else None

        return {
            "company_id": company_id,
            "total_predictions": len(preds),
            "evaluated": evaluated,
            "correct_count": correct,
            "accuracy": accuracy,
            "explanation": "Deterministic sign-based evaluation: 'buy' -> positive returns, 'sell' -> negative returns."
        }

    def evaluate_all(self) -> Dict[str, Any]:
        """Evaluate all predictions across all companies and return an overall summary.

        Also returns a per-company breakdown.
        """
        preds: List[PredictionRecord] = self.repo.list_all()
        company_map: Dict[str, Dict[str, int]] = {}
        for p in preds:
            if p.company_id not in company_map:
                company_map[p.company_id] = {"total": 0, "evaluated": 0, "correct": 0}
            company_map[p.company_id]["total"] += 1
            if p.actual_return is not None:
                company_map[p.company_id]["evaluated"] += 1
                if self.evaluate_prediction(p).prediction_correct:
                    company_map[p.company_id]["correct"] += 1

        results: Dict[str, Any] = {
            "total_companies": len(company_map),
            "total_predictions": len(preds),
            "companies": {},
        }

        total_evaluated = 0
        total_correct = 0
        for cid, stats in company_map.items():
            acc = (stats["correct"] / stats["evaluated"]) if stats["evaluated"] > 0 else None
            results["companies"][cid] = {
                "total": stats["total"],
                "evaluated": stats["evaluated"],
                "correct": stats["correct"],
                "accuracy": acc,
            }
            if stats["evaluated"] > 0:
                total_evaluated += stats["evaluated"]
                total_correct += stats["correct"]

        results["overall_accuracy"] = (total_correct / total_evaluated) if total_evaluated > 0 else None
        results["explanation"] = "Overall accuracy aggregated deterministically from per-prediction sign checks."
        return results

    def calculate_accuracy(self, predictions: List[PredictionRecord]) -> float:
        """Calculate accuracy deterministically for a list of predictions.

        Ignores predictions where actual_return is None.
        Returns 0.0 when no evaluated predictions.
        """
        evaluated = 0
        correct = 0
        for p in predictions:
            if p.actual_return is None:
                continue
            evaluated += 1
            if self.evaluate_prediction(p).prediction_correct:
                correct += 1
        if evaluated == 0:
            return 0.0
        return correct / evaluated
