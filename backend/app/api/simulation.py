from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.simulation_service import InvestmentSimulationService
from app.schemas.simulation import BuyRequest, UpdatePriceRequest, SimulationResponse

router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


@router.post("/buy", response_model=SimulationResponse)
def buy(req: BuyRequest, db: Session = Depends(get_db)):
    svc = InvestmentSimulationService(db)
    sim = svc.simulate_buy(req.company_id, req.buy_date, req.buy_price, req.shares)
    return SimulationResponse(
        uuid=sim.uuid,
        company_id=sim.company_id,
        buy_date=sim.buy_date,
        buy_price=sim.buy_price,
        current_price=sim.current_price,
        shares=sim.shares,
        profit_loss=sim.profit_loss,
        percent_return=sim.percent_return,
        status=sim.status,
        created_at=sim.created_at,
    )


@router.patch("/update-price", response_model=SimulationResponse)
def update_price(req: UpdatePriceRequest, db: Session = Depends(get_db)):
    svc = InvestmentSimulationService(db)
    try:
        sim = svc.update_market_price(req.uuid, req.current_price)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return SimulationResponse(
        uuid=sim.uuid,
        company_id=sim.company_id,
        buy_date=sim.buy_date,
        buy_price=sim.buy_price,
        current_price=sim.current_price,
        shares=sim.shares,
        profit_loss=sim.profit_loss,
        percent_return=sim.percent_return,
        status=sim.status,
        created_at=sim.created_at,
    )


@router.get("/company/{company_id}", response_model=list[SimulationResponse])
def get_by_company(company_id: str, db: Session = Depends(get_db)):
    svc = InvestmentSimulationService(db)
    sims = svc.repo.get_by_company(company_id)
    return [SimulationResponse(
        uuid=s.uuid,
        company_id=s.company_id,
        buy_date=s.buy_date,
        buy_price=s.buy_price,
        current_price=s.current_price,
        shares=s.shares,
        profit_loss=s.profit_loss,
        percent_return=s.percent_return,
        status=s.status,
        created_at=s.created_at,
    ) for s in sims]


@router.get("/portfolio", response_model=list[SimulationResponse])
def get_portfolio_simulations(db: Session = Depends(get_db)):
    svc = InvestmentSimulationService(db)
    sims = svc.repo.list()
    return [SimulationResponse(
        uuid=s.uuid,
        company_id=s.company_id,
        buy_date=s.buy_date,
        buy_price=s.buy_price,
        current_price=s.current_price,
        shares=s.shares,
        profit_loss=s.profit_loss,
        percent_return=s.percent_return,
        status=s.status,
        created_at=s.created_at,
    ) for s in sims]
