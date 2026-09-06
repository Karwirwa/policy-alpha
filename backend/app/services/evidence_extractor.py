import hashlib
import json
from datetime import datetime, timezone

from app.core.countries import normalize_country_id
from app.models.evidence import Evidence
from app.services.document_parser import ParsedDocument
from app.services.entity_resolution import EntityMatch


class EvidenceExtractor:
    """Convert parsed documents and resolved entities into Evidence objects."""

    @staticmethod
    def _normalize_for_hash(parsed: ParsedDocument) -> str:
        normalized_payload = {
            "country_id": normalize_country_id(parsed.country_id) if parsed.country_id else parsed.country_id,
            "connector_name": parsed.connector_name or "",
            "title": " ".join(parsed.title.split()) if parsed.title else "",
            "summary": " ".join(parsed.summary.split()),
            "raw_text": " ".join(parsed.raw_text.split()),
            "page_number": parsed.page_number,
            "section": " ".join(parsed.section.split()) if parsed.section else "",
            "source_reference": " ".join(parsed.source_reference.split()),
        }
        return json.dumps(normalized_payload, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def _compute_document_hash(parsed: ParsedDocument) -> str:
        normalized = EvidenceExtractor._normalize_for_hash(parsed)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def extract(
        self,
        parsed: ParsedDocument,
        linked_company: EntityMatch,
        linked_agency: EntityMatch,
        linked_project: EntityMatch,
        budget_match: EntityMatch,
        procurement_match: EntityMatch,
        extracted_keywords: list[str],
        normalized_keywords: list[str],
        detected_entities: list[str],
    ) -> Evidence:
        # Attempt to pull publication_date, language, government_level and last_verified from parsed.metadata
        pub_date = None
        try:
            pub_date = parsed.metadata.get("publication_date") if parsed.metadata else None
        except Exception:
            pub_date = None

        government_level = None
        language = None
        last_verified = None
        if parsed.metadata:
            government_level = parsed.metadata.get("government_level")
            language = parsed.metadata.get("language")
            last_verified = parsed.metadata.get("last_verified")

        canonical_country_id = normalize_country_id(parsed.country_id) if parsed.country_id else None

        return Evidence(
            document_id=parsed.document_id,
            country_id=canonical_country_id if canonical_country_id is not None else parsed.country_id,
            agency_id=linked_agency.entity_id,
            company_id=linked_company.entity_id,
            project_id=linked_project.entity_id,
            budget_id=budget_match.entity_id,
            procurement_id=procurement_match.entity_id,
            extracted_keywords=extracted_keywords,
            normalized_keywords=normalized_keywords,
            detected_entities=detected_entities,
            title=parsed.title,
            summary=parsed.summary,
            raw_text=parsed.raw_text,
            page_number=parsed.page_number,
            section=parsed.section,
            document_hash=self._compute_document_hash(parsed),
            connector_name=parsed.connector_name,
            government_level=government_level,
            language=language,
            publication_date=pub_date,
            last_verified=last_verified,
            evidence_strength=0.0,
            source_reference=parsed.source_reference,
            extracted_at=datetime.now(timezone.utc),
        )
