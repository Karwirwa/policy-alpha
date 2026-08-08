from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.agency import Agency
from app.models.budget import Budget
from app.models.company import Company
from app.models.country import Country
from app.models.document import Document
from app.models.evidence import Evidence
from app.models.project import Project
from app.models.tender import Tender
from app.core.countries import get_country_config


class EvidenceRepository:
    """Repository for reading and storing evidence records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, evidence: Evidence) -> Evidence:
        existing = self.get_by_document_hash(evidence.document_hash)
        if existing:
            return existing

        self._ensure_document_exists(evidence)
        self._ensure_canonical_entities_exist(evidence)

        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def _ensure_entity_exists(self, entity_class, entity_id: str | None, name: str | None = None, **defaults):
        if not entity_id:
            return

        entity = self.db.get(entity_class, entity_id)
        if entity:
            return

        parameters = {"id": entity_id}
        if name is not None:
            parameters["name"] = name
        parameters.update(defaults)

        entity = entity_class(**parameters)
        self.db.add(entity)
        self.db.flush()

    def _ensure_document_exists(self, evidence: Evidence) -> None:
        existing = self.db.get(Document, evidence.document_id)
        if existing:
            return

        document = Document(
            id=evidence.document_id,
            name=evidence.title,
            source_reference=evidence.source_reference,
            connector_name=evidence.connector_name,
            description=f"Document created from evidence document {evidence.document_id}",
        )
        self.db.add(document)
        self.db.flush()

    def _ensure_canonical_entities_exist(self, evidence: Evidence) -> None:
        # Only create Country rows if the country is in the canonical configured list
        # Normalize country ids to canonical form before creating/validating
        from app.core.countries import normalize_country_id

        normalized = None
        if evidence.country_id:
            normalized = normalize_country_id(evidence.country_id)
        if normalized:
            cfg = get_country_config(normalized)
            self._ensure_entity_exists(Country, normalized, name=cfg.get("name") if cfg else normalized)
        else:
            # If an explicit country was provided but couldn't be normalized, treat as unsupported
            if evidence.country_id:
                raise ValueError(f"Unsupported country id: {evidence.country_id}")
            # if no country_id provided, skip creation
        self._ensure_entity_exists(Agency, evidence.agency_id, name=evidence.agency_id)
        self._ensure_entity_exists(Company, evidence.company_id, name=evidence.company_id)
        self._ensure_entity_exists(Project, evidence.project_id, name=evidence.project_id)
        self._ensure_entity_exists(Budget, evidence.budget_id, name=evidence.budget_id)
        self._ensure_entity_exists(Tender, evidence.procurement_id, name=evidence.procurement_id)

    def get_by_document_hash(self, document_hash: str) -> Evidence | None:
        return (
            self.db.query(Evidence)
            .filter(Evidence.document_hash == document_hash)
            .order_by(Evidence.id)
            .first()
        )

    def get_by_company(self, company_id: str) -> list[Evidence]:
        return (
            self.db.query(Evidence)
            .filter(Evidence.company_id == company_id)
            .order_by(Evidence.id)
            .all()
        )

    def get_by_agency(self, agency_id: str) -> list[Evidence]:
        return (
            self.db.query(Evidence)
            .filter(Evidence.agency_id == agency_id)
            .order_by(Evidence.id)
            .all()
        )

    def get_by_country(self, country_id: str) -> list[Evidence]:
        return (
            self.db.query(Evidence)
            .filter(Evidence.country_id == country_id)
            .order_by(Evidence.id)
            .all()
        )

    def get_by_document(self, document_id: str) -> list[Evidence]:
        return (
            self.db.query(Evidence)
            .filter(Evidence.document_id == document_id)
            .order_by(Evidence.id)
            .all()
        )

    def search_by_keyword(self, keyword: str) -> list[Evidence]:
        normalized_keyword = keyword.strip().lower()
        return (
            self.db.query(Evidence)
            .filter(
                or_(
                    func.lower(Evidence.raw_text).contains(normalized_keyword),
                    func.lower(Evidence.title).contains(normalized_keyword),
                    func.lower(Evidence.summary).contains(normalized_keyword),
                    Evidence.normalized_keywords.contains([normalized_keyword]),
                )
            )
            .order_by(Evidence.id)
            .all()
        )
