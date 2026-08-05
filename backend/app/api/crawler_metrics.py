from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.crawl import CrawlRun
from app.models.evidence import Evidence
from app.models.company import Company
from app.models.project import Project
from app.models.entity_relationship import EntityRelationship
from app.repositories.crawl_repository import CrawlRepository
from app.repositories.pipeline_repository import PipelineRepository

router = APIRouter(prefix="/api/v1/crawler", tags=["crawler-metrics"])


@router.get("/metrics")
def crawler_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    # documents discovered today (sum of new_documents for runs with start_time >= today_start)
    docs_today = db.query(func.coalesce(func.sum(CrawlRun.new_documents), 0)).filter(CrawlRun.start_time >= today_start).scalar() or 0

    # evidence extracted today
    try:
        evidence_today = db.query(func.count(Evidence.id)).filter(func.date(Evidence.extracted_at) == today_start.date()).scalar() or 0
    except Exception:
        # fallback for SQLite using strftime
        evidence_today = db.query(func.count(Evidence.id)).filter(func.strftime("%Y-%m-%d", Evidence.extracted_at) == today_start.strftime("%Y-%m-%d")).scalar() or 0

    # companies discovered today
    try:
        companies_today = db.query(func.count(Company.id)).filter(func.date(Company.created_at) == today_start.date()).scalar() or 0
    except Exception:
        companies_today = db.query(func.count(Company.id)).filter(func.strftime("%Y-%m-%d", Company.created_at) == today_start.strftime("%Y-%m-%d")).scalar() or 0

    # projects discovered today
    try:
        projects_today = db.query(func.count(Project.id)).filter(func.date(Project.created_at) == today_start.date()).scalar() or 0
    except Exception:
        projects_today = db.query(func.count(Project.id)).filter(func.strftime("%Y-%m-%d", Project.created_at) == today_start.strftime("%Y-%m-%d")).scalar() or 0

    # relationships created today
    try:
        rels_today = db.query(func.count(EntityRelationship.id)).filter(func.date(EntityRelationship.created_at) == today_start.date()).scalar() or 0
    except Exception:
        rels_today = db.query(func.count(EntityRelationship.id)).filter(func.strftime("%Y-%m-%d", EntityRelationship.created_at) == today_start.strftime("%Y-%m-%d")).scalar() or 0

    # pipeline health: recent jobs success rate (last 24h)
    pr = PipelineRepository(db)
    jobs = pr.list_jobs(limit=500)
    last_24 = []
    since = now - timedelta(hours=24)
    for j in jobs:
        if getattr(j, 'start_time', None) and j.start_time >= since:
            last_24.append(j)
    total_jobs = len(last_24)
    successes = len([j for j in last_24 if getattr(j, 'status', '') == 'completed'])
    failures = len([j for j in last_24 if getattr(j, 'status', '') == 'failed'])
    success_rate = (successes / total_jobs * 100.0) if total_jobs else 100.0

    # processing queue counts
    pending_jobs = len([j for j in jobs if getattr(j, 'status', '') in ('pending', 'running')])

    # recent errors from crawl runs and pipeline jobs
    cr = CrawlRepository(db)
    recent_runs = cr.list_history(limit=50)
    crawl_errors = [
        {"uuid": r.uuid, "country_code": r.country_code, "errors": r.errors, "start_time": r.start_time, "status": r.status}
        for r in recent_runs if r.errors
    ]
    pipeline_errors = [
        {"id": j.id, "error": getattr(j, 'error', None), "stage": getattr(j, 'stage', None), "start_time": getattr(j, 'start_time', None)}
        for j in jobs if getattr(j, 'error', None)
    ]

    # timeline: hourly documents found for today (last 24 hours)
    timeline_docs: List[Dict[str, Any]] = []
    for h in range(0, 24):
        start_h = now - timedelta(hours=23 - h)
        end_h = start_h + timedelta(hours=1)
        count = db.query(func.coalesce(func.sum(CrawlRun.new_documents), 0)).filter(CrawlRun.start_time >= start_h, CrawlRun.start_time < end_h).scalar() or 0
        timeline_docs.append({"hour": start_h.strftime("%Y-%m-%dT%H:00:00Z"), "count": int(count)})

    timeline_evidence: List[Dict[str, Any]] = []
    for h in range(0, 24):
        start_h = now - timedelta(hours=23 - h)
        end_h = start_h + timedelta(hours=1)
        try:
            cnt = db.query(func.count(Evidence.id)).filter(Evidence.extracted_at >= start_h, Evidence.extracted_at < end_h).scalar() or 0
        except Exception:
            cnt = db.query(func.count(Evidence.id)).filter(func.strftime("%Y-%m-%d %H", Evidence.extracted_at) >= start_h.strftime("%Y-%m-%d %H"), func.strftime("%Y-%m-%d %H", Evidence.extracted_at) < end_h.strftime("%Y-%m-%d %H")).scalar() or 0
        timeline_evidence.append({"hour": start_h.strftime("%Y-%m-%dT%H:00:00Z"), "count": int(cnt)})

    # current running crawl (if any)
    running = cr.list_running()
    current = None
    if running:
        r = running[0]
        current = {"uuid": r.uuid, "country_code": r.country_code, "start_time": r.start_time, "status": r.status, "documents_found": r.documents_found}

    return {
        "crawler_running": getattr(running, '__len__', lambda: 0)() > 0,
        "current_run": current,
        "documents_today": int(docs_today),
        "evidence_today": int(evidence_today),
        "companies_today": int(companies_today),
        "projects_today": int(projects_today),
        "relationships_today": int(rels_today),
        "pipeline": {"total_jobs_last24h": total_jobs, "successes": successes, "failures": failures, "success_rate": float(success_rate), "pending_jobs": pending_jobs},
        "errors": {"crawl_errors": crawl_errors, "pipeline_errors": pipeline_errors},
        "timeline_docs": timeline_docs,
        "timeline_evidence": timeline_evidence,
    }
