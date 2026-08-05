from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.calibration_service import CalibrationService
from app.services.prediction_evaluation import PredictionEvaluationService
from app.services.score_audit_service import ScoreAuditService
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.calibration import CalibrationReportResponse, CompanyCalibrationResponse, PredictionRecordResponse

router = APIRouter(prefix="/api/v1", tags=["calibration"])


@router.get("/calibration/report", response_model=CalibrationReportResponse)
def get_report(db: Session = Depends(get_db)):
    svc = CalibrationService(db)
    report = svc.generate_report()
    return report


@router.get("/calibration/factors")
def get_factors(db: Session = Depends(get_db)):
    repo = PredictionRepository(db)
    return [
        {
            "factor_name": f.factor_name,
            "weight_used": f.weight_used,
            "average_accuracy": f.average_accuracy,
            "recommended_weight": f.recommended_weight,
            "samples": f.samples,
        }
        for f in repo.list_factors()
    ]


@router.get("/calibration/company/{company_id}", response_model=CompanyCalibrationResponse)
def get_company_calibration(company_id: str, db: Session = Depends(get_db)):
    evaluator = PredictionEvaluationService(db)
    result = evaluator.evaluate_company(company_id)
    return CompanyCalibrationResponse(company_id=result["company_id"], evaluated=result["evaluated"], accuracy=result["accuracy"])


@router.post("/calibration/run")
def run_calibration(db: Session = Depends(get_db)):
    svc = CalibrationService(db)
    report = svc.generate_report()
    return report


@router.get("/predictions/company/{company_id}", response_model=list[PredictionRecordResponse])
def get_predictions_for_company(company_id: str, db: Session = Depends(get_db)):
    repo = PredictionRepository(db)
    preds = repo.list_by_company(company_id)
    return [PredictionRecordResponse.from_orm(p) for p in preds]
