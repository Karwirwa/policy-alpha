from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence import EvidenceSchema
from app.services.entity_resolution import EntityResolutionService
from app.models.evidence import Evidence
from sqlalchemy import func

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


@router.get("/project/{project_name}", response_model=list[EvidenceSchema])
def get_by_project(
    project_name: str,
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    resolver = EntityResolutionService()
    project_match = resolver.resolve_project(project_name)
    if not project_match.entity_id:
        return []
    return repository.get_by_project(project_match.entity_id)


@router.get("/latest", response_model=list[EvidenceSchema])
def get_latest(
    limit: int = 20,
    repository: EvidenceRepository = Depends(get_repository),
) -> list[EvidenceSchema]:
    return repository.get_latest(limit)


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
    from app.core.countries import normalize_country_id

    normalized = normalize_country_id(country_match.entity_id)
    if not normalized:
        # treat as not found
        return []
    return repository.get_by_country(normalized)


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


@router.get("/list", response_model=list[EvidenceSchema])
def list_evidence(
    country: str | None = None,
    agency: str | None = None,
    company: str | None = None,
    project: str | None = None,
    tender: str | None = None,
    confidence_min: float | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    keyword: str | None = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[EvidenceSchema]:
    """List evidence with optional filters. This endpoint supports frontend explorer queries.

    Date filters expect ISO date strings (YYYY-MM-DD) and filter publication_date.
    """
    q = db.query(Evidence)

    if country:
        # resolve country name to id if necessary
        from app.services.entity_resolution import EntityResolutionService

        resolver = EntityResolutionService()
        match = resolver.resolve_country(country)
        if match.entity_id:
            from app.core.countries import normalize_country_id

            normalized = normalize_country_id(match.entity_id)
            if normalized:
                q = q.filter(Evidence.country_id == normalized)
            else:
                # fallback to using the raw parameter if resolver matched but normalization failed
                q = q.filter(Evidence.country_id == country)
        else:
            # allow passing country id directly
            q = q.filter(Evidence.country_id == country)

    if agency:
        match = EntityResolutionService().resolve_agency(agency)
        if match.entity_id:
            q = q.filter(Evidence.agency_id == match.entity_id)
        else:
            q = q.filter(Evidence.agency_id == agency)

    if company:
        match = EntityResolutionService().resolve_company(company)
        if match.entity_id:
            q = q.filter(Evidence.company_id == match.entity_id)
        else:
            q = q.filter(Evidence.company_id == company)

    if project:
        match = EntityResolutionService().resolve_project(project)
        if match.entity_id:
            q = q.filter(Evidence.project_id == match.entity_id)
        else:
            q = q.filter(Evidence.project_id == project)

    if tender:
        # tender id or name
        q = q.filter(Evidence.procurement_id == tender)

    if confidence_min is not None:
        q = q.filter(Evidence.evidence_strength >= confidence_min)

    if start_date:
        try:
            from datetime import datetime

            sd = datetime.fromisoformat(start_date)
            q = q.filter(Evidence.publication_date >= sd)
        except Exception:
            pass

    if end_date:
        try:
            from datetime import datetime

            ed = datetime.fromisoformat(end_date)
            q = q.filter(Evidence.publication_date <= ed)
        except Exception:
            pass

    if keyword:
        normalized = keyword.strip().lower()
        q = q.filter(
            (func.lower(Evidence.title).contains(normalized))
            | (func.lower(Evidence.summary).contains(normalized))
            | (func.lower(Evidence.raw_text).contains(normalized))
            # JSON contains for normalized keywords (may not be supported in all DBs)
            | Evidence.normalized_keywords.contains([normalized])
        )

    q = q.order_by(Evidence.extracted_at.desc()).limit(limit).offset(offset)

    results = q.all()
    return results
