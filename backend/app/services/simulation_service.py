from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.repositories.simulation_repository import SimulationRepository
from app.models.portfolio import InvestmentSimulation


class InvestmentSimulationService:
    def __init__(self, db: Session):
        self.repo = SimulationRepository(db)

    def simulate_buy(self, company_id: str, buy_date: datetime, buy_price: float, shares: int) -> InvestmentSimulation:
        sim = InvestmentSimulation(company_id=company_id, buy_date=buy_date, buy_price=buy_price, current_price=buy_price, shares=shares, profit_loss=0.0, percent_return=0.0, status="open")
        return self.repo.create(sim)

    def update_market_price(self, uuid: str, current_price: float) -> InvestmentSimulation:
        sim = self.repo.get(uuid)
        if not sim:
            raise ValueError("Simulation not found")
        sim.current_price = current_price
        sim.profit_loss = (sim.current_price - sim.buy_price) * sim.shares
        if sim.buy_price > 0:
            sim.percent_return = (sim.current_price / sim.buy_price - 1.0) * 100.0
        sim = self.repo.update(sim)
        return sim

    def calculate_return(self, uuid: str) -> float:
        sim = self.repo.get(uuid)
        if not sim:
            raise ValueError("Simulation not found")
        return sim.percent_return

    def portfolio_return(self) -> float:
        sims = self.repo.list()
        if not sims:
            return 0.0
        returns = [s.percent_return for s in sims]
        return sum(returns) / len(returns)
