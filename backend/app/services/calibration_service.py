from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session

from app.repositories.prediction_repository import PredictionRepository
from app.repositories.opportunity_repository import OpportunityRepository
from app.repositories.prediction_repository import PredictionRepository
from app.models.prediction import CalibrationRun, FactorPerformance
from app.models.opportunity import ScoreBreakdown


class CalibrationService:
    """Generate deterministic calibration suggestions based on historical prediction accuracy."""

    def __init__(self, db: Session):
        self.db = db
        self.pred_repo = PredictionRepository(db)
        self.op_repo = OpportunityRepository(db)

    def calculate_accuracy(self) -> float:
        preds = self.pred_repo.list_all()
        if not preds:
            return 0.0
        total = 0
        correct = 0
        for p in preds:
            total += 1
            if p.prediction_correct:
                correct += 1
        return correct / total if total else 0.0

    def factor_accuracy(self) -> Dict[str, Dict[str, float]]:
        """
        For each factor name present in ScoreBreakdown, calculate the average accuracy where that factor appears in the latest opportunity score prior to a prediction.
        Returns a map: factor -> {average_accuracy, samples, average_weight}
        """
        factors: Dict[str, Dict[str, float]] = {}
        preds = self.pred_repo.list_all()
        for p in preds:
            # find latest opportunity score for company before prediction date
            score = self.op_repo.get_latest_score(p.company_id)
            if not score:
                continue
            breakdowns: List[ScoreBreakdown] = score.breakdowns
            for b in breakdowns:
                entry = factors.setdefault(b.factor, {"correct": 0, "total": 0, "weight_sum": 0.0})
                entry["total"] += 1
                entry["weight_sum"] += b.weight
                if p.prediction_correct:
                    entry["correct"] += 1

        result: Dict[str, Dict[str, float]] = {}
        for factor, data in factors.items():
            total = data["total"]
            correct = data["correct"]
            avg_weight = data["weight_sum"] / total if total else 0.0
            avg_acc = correct / total if total else 0.0
            result[factor] = {"average_accuracy": avg_acc, "samples": total, "average_weight": avg_weight}
        return result

    def recommend_new_weights(self) -> Dict[str, float]:
        """
        For each factor compute a recommended adjustment based on average accuracy.
        Formula (deterministic): recommended = current_avg_weight * (1 + (avg_accuracy - 0.5) * 0.2)
        Clamp to [0, 100]
        """
        fa = self.factor_accuracy()
        recommendations: Dict[str, float] = {}
        for factor, stats in fa.items():
            current = stats.get("average_weight", 0.0)
            avg_acc = stats.get("average_accuracy", 0.0)
            recommended = current * (1.0 + (avg_acc - 0.5) * 0.2)
            if recommended < 0:
                recommended = 0.0
            if recommended > 100:
                recommended = 100.0
            recommendations[factor] = round(recommended, 4)
        return recommendations

    def generate_report(self) -> Dict:
        fa = self.factor_accuracy()
        recs = self.recommend_new_weights()
        overall = self.calculate_accuracy()
        # save a calibration run record
        run = CalibrationRun(run_date=datetime.utcnow(), companies_analyzed=len(self.pred_repo.list_all()), average_accuracy=overall, recommendations_generated=recs)
        saved = self.pred_repo.save_calibration_run(run)

        # update factor performance table
        for factor, stats in fa.items():
            fp = FactorPerformance(factor_name=factor, weight_used=stats.get("average_weight", 0.0), average_accuracy=stats.get("average_accuracy", 0.0), recommended_weight=recs.get(factor, 0.0), samples=stats.get("samples", 0))
            self.pred_repo.save_factor_performance(fp)

        return {"calibration_run": {"id": saved.id, "uuid": saved.uuid, "run_date": saved.run_date, "companies_analyzed": saved.companies_analyzed, "average_accuracy": saved.average_accuracy}, "factor_recommendations": recs, "factor_stats": fa}
