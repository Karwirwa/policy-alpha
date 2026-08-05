from datetime import datetime
from pydantic import BaseModel


class WatchlistItemCreate(BaseModel):
    company_id: str
    priority: int = 1
    reason: str | None = None


class WatchlistItemResponse(BaseModel):
    uuid: str
    company_id: str
    priority: int
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True
