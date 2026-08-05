from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.pipeline_repository import PipelineRepository
from app.services.pipeline_service import ProcessingService

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


def get_repository(db: Session = Depends(get_db)) -> PipelineRepository:
    return PipelineRepository(db)


def _serialize_job(job) -> Dict[str, Any]:
    return {
        "id": job.id,
        "uuid": job.uuid,
        "document_id": job.document_id,
        "status": job.status,
        "stage": job.stage,
        "start_time": job.start_time.isoformat() if getattr(job, "start_time", None) else None,
        "end_time": job.end_time.isoformat() if getattr(job, "end_time", None) else None,
        "retries": job.retries,
        "error": job.error,
    }


@router.post("/process/{document_id}")
def process_document(document_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Trigger processing for the given document id and return a job summary."""
    svc = ProcessingService(db)
    try:
        job = svc.process_document(document_id)
    except ValueError as e:
        # document not found or no connector
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return _serialize_job(job)


@router.post("/retry/{job_id}")
def retry_job(job_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retry a failed job by id and return the new job summary."""
    svc = ProcessingService(db)
    try:
        job = svc.retry_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return _serialize_job(job)


@router.get("/jobs")
def list_jobs(limit: int = Query(100, ge=1, le=1000), repository: PipelineRepository = Depends(get_repository)) -> Dict[str, Any]:
    """Return recent pipeline jobs (most recent first)."""
    jobs = repository.list_jobs(limit=limit)
    return {"count": len(jobs), "jobs": [_serialize_job(j) for j in jobs]}


@router.get("/job/{job_id}")
def get_job(job_id: int, repository: PipelineRepository = Depends(get_repository)) -> Dict[str, Any]:
    """Return a single job summary by id."""
    job = repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _serialize_job(job)
