from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.models.portfolio import Portfolio, PortfolioPosition
from app.repositories.opportunity_history_repository import OpportunityHistoryRepository
from app.repositories.simulation_repository import SimulationRepository
from app.repositories.watchlist_repository import WatchlistRepository


class PortfolioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PortfolioRepository(db)
        self.sim_repo = SimulationRepository(db)
        self.watch_repo = WatchlistRepository(db)
        self.history_repo = OpportunityHistoryRepository(db)

    def create_portfolio(self, name: str, description: str | None = None) -> Portfolio:
        p = Portfolio(name=name, description=description)
        return self.repo.create(p)

    def add_company(self, portfolio_uuid: str, company_id: str, allocation_percent: float = 0.0, notes: str | None = None) -> PortfolioPosition:
        portfolio = self.repo.get_by_uuid(portfolio_uuid)
        if not portfolio:
            raise ValueError("Portfolio not found")
        pos = PortfolioPosition(portfolio_id=portfolio.id, company_id=company_id, allocation_percent=allocation_percent, notes=notes)
        return self.repo.add_position(pos)

    def remove_company(self, portfolio_uuid: str, company_id: str) -> None:
        portfolio = self.repo.get_by_uuid(portfolio_uuid)
        if not portfolio:
            raise ValueError("Portfolio not found")
        self.repo.remove_position(portfolio.id, company_id)

    def portfolio_summary(self, portfolio_uuid: str) -> dict:
        portfolio = self.repo.get_by_uuid(portfolio_uuid)
        if not portfolio:
            raise ValueError("Portfolio not found")
        positions = self.repo.get_positions(portfolio.id)
        total_companies = len(positions)
        # Average opportunity score pulled from OpportunityScoreHistory latest per company
        avg_scores = []
        returns = []
        for p in positions:
            histories = self.history_repo.get_company_history(p.company_id)
            if histories:
                avg_scores.append(histories[-1].score)
            sims = self.sim_repo.get_by_company(p.company_id)
            for s in sims:
                returns.append(s.percent_return)
        avg_score = sum(avg_scores) / len(avg_scores) if avg_scores else 0.0
        avg_return = sum(returns) / len(returns) if returns else 0.0
        highest = None
        lowest = None
        if returns:
            highest_ret = max(returns)
            lowest_ret = min(returns)
            highest = highest_ret
            lowest = lowest_ret
        # current recommendations: latest recommendation for each company
        recommendations = {p.company_id: (self.history_repo.get_company_history(p.company_id)[-1].recommendation if self.history_repo.get_company_history(p.company_id) else None) for p in positions}
        return {
            "portfolio_uuid": portfolio.uuid,
            "name": portfolio.name,
            "total_companies": total_companies,
            "average_opportunity_score": avg_score,
            "average_return": avg_return,
            "highest_performing": highest,
            "worst_performing": lowest,
            "current_recommendations": recommendations,
        }
