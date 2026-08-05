from sqlalchemy.orm import Session
from typing import Optional

from app.models.portfolio import InvestmentSimulation


class SimulationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, sim: InvestmentSimulation) -> InvestmentSimulation:
        self.db.add(sim)
        self.db.commit()
        self.db.refresh(sim)
        return sim

    def update(self, sim: InvestmentSimulation) -> InvestmentSimulation:
        self.db.add(sim)
        self.db.commit()
        self.db.refresh(sim)
        return sim

    def get_by_company(self, company_id: str) -> list[InvestmentSimulation]:
        return self.db.query(InvestmentSimulation).filter(InvestmentSimulation.company_id == company_id).all()

    def list(self) -> list[InvestmentSimulation]:
        return self.db.query(InvestmentSimulation).order_by(InvestmentSimulation.created_at.desc()).all()

    def get(self, uuid: str) -> Optional[InvestmentSimulation]:
        return self.db.query(InvestmentSimulation).filter(InvestmentSimulation.uuid == uuid).first()
