from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.portfolio_service import PortfolioService
from app.schemas.portfolio import PortfolioCreateRequest, PortfolioResponse, AddCompanyRequest, PortfolioSummaryResponse

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.post("", response_model=PortfolioResponse)
def create_portfolio(req: PortfolioCreateRequest, db: Session = Depends(get_db)):
    svc = PortfolioService(db)
    p = svc.create_portfolio(req.name, req.description)
    return PortfolioResponse(uuid=p.uuid, name=p.name, description=p.description, created_at=p.created_at)


@router.get("", response_model=list[PortfolioResponse])
def list_portfolios(db: Session = Depends(get_db)):
    svc = PortfolioService(db)
    repos = svc.repo.list()
    return [PortfolioResponse(uuid=r.uuid, name=r.name, description=r.description, created_at=r.created_at) for r in repos]


@router.get("/{uuid}", response_model=PortfolioResponse)
def get_portfolio(uuid: str, db: Session = Depends(get_db)):
    svc = PortfolioService(db)
    p = svc.repo.get_by_uuid(uuid)
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioResponse(uuid=p.uuid, name=p.name, description=p.description, created_at=p.created_at)


@router.post("/{uuid}/company", response_model=dict)
def add_company(uuid: str, req: AddCompanyRequest, db: Session = Depends(get_db)):
    svc = PortfolioService(db)
    try:
        pos = svc.add_company(uuid, req.company_id, req.allocation_percent, req.notes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return {"company_id": pos.company_id, "allocation_percent": pos.allocation_percent}


@router.delete("/{uuid}/company/{company_id}")
def remove_company(uuid: str, company_id: str, db: Session = Depends(get_db)):
    svc = PortfolioService(db)
    try:
        svc.remove_company(uuid, company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return {"status": "ok"}


@router.get("/{uuid}/summary", response_model=PortfolioSummaryResponse)
def portfolio_summary(uuid: str, db: Session = Depends(get_db)):
    svc = PortfolioService(db)
    try:
        summary = svc.portfolio_summary(uuid)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return PortfolioSummaryResponse(**summary)
