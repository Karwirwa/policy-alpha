from sqlalchemy.orm import Session
from typing import Optional

from app.models.portfolio import Portfolio, PortfolioPosition


class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, portfolio: Portfolio) -> Portfolio:
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_by_uuid(self, uuid: str) -> Optional[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.uuid == uuid).first()

    def list(self) -> list[Portfolio]:
        return self.db.query(Portfolio).order_by(Portfolio.id).all()

    def add_position(self, position: PortfolioPosition) -> PortfolioPosition:
        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        return position

    def remove_position(self, portfolio_id: int, company_id: str) -> None:
        pos = (
            self.db.query(PortfolioPosition)
            .filter(PortfolioPosition.portfolio_id == portfolio_id, PortfolioPosition.company_id == company_id)
            .first()
        )
        if pos:
            self.db.delete(pos)
            self.db.commit()

    def get_positions(self, portfolio_id: int) -> list[PortfolioPosition]:
        return self.db.query(PortfolioPosition).filter(PortfolioPosition.portfolio_id == portfolio_id).all()
