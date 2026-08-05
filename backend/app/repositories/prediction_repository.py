from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.prediction import PredictionRecord, CalibrationRun, FactorPerformance


class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_prediction(self, pred: PredictionRecord) -> PredictionRecord:
        self.db.add(pred)
        self.db.commit()
        self.db.refresh(pred)
        return pred

    def list_by_company(self, company_id: str) -> List[PredictionRecord]:
        return self.db.query(PredictionRecord).filter(PredictionRecord.company_id == company_id).order_by(PredictionRecord.prediction_date.desc()).all()

    def list_all(self) -> List[PredictionRecord]:
        return self.db.query(PredictionRecord).order_by(PredictionRecord.prediction_date.desc()).all()

    def save_calibration_run(self, run: CalibrationRun) -> CalibrationRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def save_factor_performance(self, fp: FactorPerformance) -> FactorPerformance:
        existing = self.db.query(FactorPerformance).filter(FactorPerformance.factor_name == fp.factor_name).first()
        if existing:
            existing.weight_used = fp.weight_used
            existing.average_accuracy = fp.average_accuracy
            existing.recommended_weight = fp.recommended_weight
            existing.samples = fp.samples
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(fp)
        self.db.commit()
        self.db.refresh(fp)
        return fp

    def list_factors(self) -> List[FactorPerformance]:
        return self.db.query(FactorPerformance).order_by(FactorPerformance.factor_name).all()

    def get_latest_prediction_before(self, company_id: str, before_date: datetime):
        return (
            self.db.query(PredictionRecord)
            .filter(PredictionRecord.company_id == company_id, PredictionRecord.prediction_date <= before_date)
            .order_by(PredictionRecord.prediction_date.desc())
            .first()
        )
