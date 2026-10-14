from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.evidence import Evidence
from app.services.kenya_opportunity import derive_kenya_opportunities

router = APIRouter(prefix="/api/v1/kenya", tags=["kenya-opportunities"])


@router.get("/opportunities")
def list_kenya_opportunities(
    limit: int = Query(20, ge=1, le=1000),
    include_illustrative: bool = False,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    opportunities = derive_kenya_opportunities(
        db, limit=limit, include_illustrative=include_illustrative
    )
    query = db.query(func.count(Evidence.id)).filter(Evidence.country_id == "kenya")
    if not include_illustrative:
        query = query.filter(Evidence.verification_status != "illustrative")
    return {"opportunities": opportunities, "total": int(query.scalar() or 0)}


@router.get("/sectors")
def list_kenya_sectors(db: Session = Depends(get_db)) -> dict[str, Any]:
    opportunities = derive_kenya_opportunities(db, limit=None)
    sectors: dict[str, list[float]] = defaultdict(list)
    for opportunity in opportunities:
        sectors[opportunity["sector"]].append(opportunity["score"])

    return {
        "sectors": [
            {
                "name": name,
                "count": len(scores),
                "avg_score": round(sum(scores) / len(scores), 2),
            }
            for name, scores in sorted(sectors.items())
        ]
    }


@router.get("/ministries")
def list_kenya_ministries(db: Session = Depends(get_db)) -> dict[str, Any]:
    opportunities = derive_kenya_opportunities(db, limit=None)
    ministries: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"count": 0, "total_score": 0.0}
    )
    for opportunity in opportunities:
        ministry = ministries[opportunity["ministry"]]
        ministry["count"] += 1
        ministry["total_score"] += opportunity["score"]

    rows = [
        {
            "name": name,
            "count": int(values["count"]),
            "total_score": round(float(values["total_score"]), 2),
        }
        for name, values in ministries.items()
    ]
    rows.sort(key=lambda item: (-item["total_score"], item["name"]))
    return {"ministries": rows}


@router.get("/upcoming")
def list_upcoming_kenya_opportunities(
    days: int = Query(30, ge=0, le=3650),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=days)
    upcoming = [
        opportunity
        for opportunity in derive_kenya_opportunities(db, limit=None)
        if opportunity["deadline"] is not None
        and now
        <= datetime.fromisoformat(opportunity["deadline"])
        <= cutoff
    ]
    upcoming.sort(
        key=lambda item: (item["deadline"], -item["score"], item["evidence_id"])
    )
    return {"upcoming": upcoming}
