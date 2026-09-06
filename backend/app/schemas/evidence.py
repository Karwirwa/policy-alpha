from datetime import datetime

from pydantic import BaseModel


class EvidenceSchema(BaseModel):
    id: int
    document_id: str
    country_id: str
    agency_id: str | None
    company_id: str | None
    project_id: str | None
    budget_id: str | None
    procurement_id: str | None
    extracted_keywords: list[str]
    normalized_keywords: list[str]
    detected_entities: list[str]
    title: str
    summary: str
    raw_text: str
    page_number: int | None
    section: str | None
    document_hash: str
    connector_name: str | None
    government_level: str | None = None
    language: str | None = None
    publication_date: datetime | None = None
    last_verified: datetime | None = None
    evidence_strength: float
    source_reference: str
    extracted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
