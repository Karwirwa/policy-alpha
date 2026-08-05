from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.crawl_repository import CrawlRepository
from app.services.crawler import CrawlerScheduler, CrawlerManager

router = APIRouter(prefix="/api/v1/crawler", tags=["crawler"])

# module-level scheduler singleton so status and manual runs reference the same scheduler
_scheduler_instance: Optional[CrawlerScheduler] = None


def _get_scheduler(db: Session) -> CrawlerScheduler:
    """Return a singleton CrawlerScheduler for the app lifetime.

    The scheduler is created on first use and reuses the provided DB session.
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = CrawlerScheduler(db)
    return _scheduler_instance


@router.post("/run")
def run_full(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Trigger a full crawl across all registered countries and return a summary."""
    scheduler = _get_scheduler(db)

    # run_once executes a full crawl synchronously and returns per-country results
    try:
        results: List[Dict[str, Any]] = scheduler.run_once()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    total_countries = len(results)
    total_documents_found = sum(r.get("documents_found", 0) if isinstance(r, dict) else 0 for r in results)
    total_new_documents = sum(r.get("new_documents", 0) if isinstance(r, dict) else 0 for r in results)
    errors = [r.get("errors") for r in results if isinstance(r, dict) and r.get("errors")]

    summary = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "total_countries": total_countries,
        "total_documents_found": total_documents_found,
        "total_new_documents": total_new_documents,
        "errors": errors,
        "results": results,
    }
    return summary


@router.post("/run/{country_code}")
def run_country(country_code: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Trigger a crawl for a single country and return a summary for that country."""
    scheduler = _get_scheduler(db)
    try:
        result = scheduler.run_single_country_now(country_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if isinstance(result, dict) and result.get("error"):
        # mirror existing behavior: not found connector => 404
        raise HTTPException(status_code=404, detail=result.get("error"))

    return {"run_at": datetime.utcnow().isoformat() + "Z", "country_result": result}


@router.get("/status")
def crawler_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return scheduler status and currently running crawl records from the DB."""
    scheduler = _get_scheduler(db)

    # determine if scheduler thread is alive
    running = False
    try:
        thread = getattr(scheduler, "_thread", None)
        if thread is not None:
            running = getattr(thread, "is_alive", lambda: False)()
    except Exception:
        running = False

    repo = CrawlRepository(db)
    running_runs = repo.list_running()

    running_summary = [
        {
            "uuid": r.uuid,
            "country_code": r.country_code,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "status": r.status,
        }
        for r in running_runs
    ]

    return {
        "scheduler_running": running,
        "interval_seconds": getattr(scheduler, "interval_seconds", None),
        "db_running_jobs": running_summary,
    }


@router.get("/history")
def crawler_history(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return recent crawl runs from the database.

    The `limit` query parameter controls how many runs to return (default 100).
    """
    repo = CrawlRepository(db)
    runs = repo.list_history(limit=limit)

    def _serialize_run(r) -> Dict[str, Any]:
        return {
            "uuid": r.uuid,
            "country_code": r.country_code,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "end_time": r.end_time.isoformat() if r.end_time else None,
            "duration_seconds": r.duration_seconds,
            "documents_found": r.documents_found,
            "new_documents": r.new_documents,
            "errors": r.errors,
            "status": r.status,
        }

    return {"count": len(runs), "runs": [_serialize_run(r) for r in runs]}
