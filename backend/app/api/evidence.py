from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence import EvidenceSchema
from app.services.entity_resolution import EntityResolutionService

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])


def get_repository(db: Session = Depends(get_db)) -> EvidenceRepository:
    return EvidenceRepository(db)


@router.get("/company/{company_name}", response_model=list[EvidenceSchema])
def get_by_company(
    company_name: str,
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    resolver = EntityResolutionService()
    company_match = resolver.resolve_company(company_name)
    if not company_match.entity_id:
        return []
    return repository.get_by_company(company_match.entity_id)


@router.get("/agency/{agency_name}", response_model=list[EvidenceSchema])
def get_by_agency(
    agency_name: str,
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    resolver = EntityResolutionService()
    agency_match = resolver.resolve_agency(agency_name)
    if not agency_match.entity_id:
        return []
    return repository.get_by_agency(agency_match.entity_id)


@router.get("/country/{country_name}", response_model=list[EvidenceSchema])
def get_by_country(
    country_name: str,
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    resolver = EntityResolutionService()
    country_match = resolver.resolve_country(country_name)
    if not country_match.entity_id:
        return []
    return repository.get_by_country(country_match.entity_id)


@router.get("/document/{document_id}", response_model=list[EvidenceSchema])
def get_by_document(
    document_id: str,
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    results = repository.get_by_document(document_id)
    if not results:
        raise HTTPException(status_code=404, detail="Document evidence not found")
    return results


@router.get("/search", response_model=list[EvidenceSchema])
def search_by_keyword(
    keyword: str = Query(..., min_length=1),
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    return repository.search_by_keyword(keyword)
