from sqlalchemy.orm import Session

from app.repositories.watchlist_repository import WatchlistRepository
from app.models.portfolio import Watchlist


class WatchlistService:
    def __init__(self, db: Session):
        self.repo = WatchlistRepository(db)

    def add(self, company_id: str, priority: int = 1, reason: str | None = None) -> Watchlist:
        item = Watchlist(company_id=company_id, priority=priority, reason=reason)
        return self.repo.add(item)

    def remove(self, company_id: str) -> None:
        self.repo.remove(company_id)

    def list(self) -> list[Watchlist]:
        return self.repo.list()
