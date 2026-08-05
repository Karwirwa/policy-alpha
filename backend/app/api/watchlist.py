from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.watchlist_service import WatchlistService
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemResponse

router = APIRouter(prefix="/api/v1/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemResponse])
def list_watchlist(db: Session = Depends(get_db)):
    svc = WatchlistService(db)
    items = svc.list()
    return [WatchlistItemResponse(uuid=i.uuid, company_id=i.company_id, priority=i.priority, reason=i.reason, created_at=i.created_at) for i in items]


@router.post("", response_model=WatchlistItemResponse)
def add_to_watchlist(req: WatchlistItemCreate, db: Session = Depends(get_db)):
    svc = WatchlistService(db)
    item = svc.add(req.company_id, req.priority, req.reason)
    return WatchlistItemResponse(uuid=item.uuid, company_id=item.company_id, priority=item.priority, reason=item.reason, created_at=item.created_at)


@router.delete("/{company_id}")
def remove_from_watchlist(company_id: str, db: Session = Depends(get_db)):
    svc = WatchlistService(db)
    svc.remove(company_id)
    return {"status": "ok"}
