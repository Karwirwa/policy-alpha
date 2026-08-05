from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.graph_service import GraphService

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


def get_graph_service(db: Session = Depends(get_db)) -> GraphService:
    return GraphService(db)


@router.get("/company/{company_name}")
def get_company_network(
    company_name: str,
    service: GraphService = Depends(get_graph_service),
) -> dict:
    try:
        return service.get_company_network(company_name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/agency/{agency_name}")
def get_agency_network(
    agency_name: str,
    service: GraphService = Depends(get_graph_service),
) -> dict:
    try:
        return service.get_agency_network(agency_name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/project/{project_name}")
def get_project_network(
    project_name: str,
    service: GraphService = Depends(get_graph_service),
) -> dict:
    try:
        return service.get_project_network(project_name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/budget/{budget_name}")
def get_budget_network(
    budget_name: str,
    service: GraphService = Depends(get_graph_service),
) -> dict:
    try:
        return service.get_budget_network(budget_name)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
