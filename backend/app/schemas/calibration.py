from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List


class FactorPerformanceItem(BaseModel):
    factor_name: str
    weight_used: float
    average_accuracy: float
    recommended_weight: float
    samples: int


class CalibrationReportResponse(BaseModel):
    calibration_run: Dict[str, Any]
    factor_recommendations: Dict[str, float]
    factor_stats: Dict[str, Any]


class CompanyCalibrationResponse(BaseModel):
    company_id: str
    evaluated: int
    accuracy: float


class PredictionRecordResponse(BaseModel):
    uuid: str
    company_id: str
    recommendation: str
    score: float
    prediction_date: datetime
    target_date: datetime | None
    actual_return: float | None
    prediction_correct: bool
    confidence: float

    class Config:
        from_attributes = True
