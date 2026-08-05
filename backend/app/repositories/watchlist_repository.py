from sqlalchemy.orm import Session

from app.models.portfolio import Watchlist


class WatchlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, item: Watchlist) -> Watchlist:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove(self, company_id: str) -> None:
        item = self.db.query(Watchlist).filter(Watchlist.company_id == company_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()

    def list(self) -> list[Watchlist]:
        return self.db.query(Watchlist).order_by(Watchlist.priority.desc(), Watchlist.id).all()
