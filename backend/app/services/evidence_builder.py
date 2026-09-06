from __future__ import annotations
from app.core.countries import normalize_country_id
from app.services.document_parser import DocumentParser, EvidenceDocument
from app.services.evidence_extractor import EvidenceExtractor
from app.services.evidence_strength import EvidenceStrengthCalculator
from app.services.entity_resolution import EntityResolutionService, EntityMatch
from app.services.metadata_extractor import MetadataExtractor
from app.services.relationship_builder import RelationshipBuilder
from app.repositories.relationship_repository import RelationshipRepository


class EvidenceBuilder:
    """Orchestrate evidence extraction from parsed government documents."""

    def __init__(self) -> None:
        self.parser = DocumentParser()
        self.resolver = EntityResolutionService()
        self.extractor = EvidenceExtractor()
        self.strength_calculator = EvidenceStrengthCalculator()
        self.metadata_extractor = MetadataExtractor()

    def _resolve_with_fallback(self, primary_text: str | None, fallback_text: str, resolver_callable):
        if primary_text:
            result = resolver_callable(primary_text)
            if result.entity_id:
                return result
        return resolver_callable(fallback_text)

    def build(self, document: EvidenceDocument) -> Evidence:
        parsed = self.parser.parse(document)
        normalized_country_id = normalize_country_id(parsed.country_id) if parsed.country_id else None

        linked_company = self._resolve_with_fallback(parsed.title, parsed.raw_text, lambda text: self.resolver.resolve_company(text, country_code=normalized_country_id))
        linked_agency = self._resolve_with_fallback(parsed.title, parsed.raw_text, lambda text: self.resolver.resolve_agency(text, country_code=normalized_country_id))
        linked_project = self._resolve_with_fallback(parsed.title, parsed.raw_text, lambda text: self.resolver.resolve_project(text, country_code=normalized_country_id))
        budget_match = self.resolver.resolve_budget(parsed.raw_text, country_code=normalized_country_id)
        procurement_match = self.resolver.resolve_procurement(parsed.raw_text, country_code=normalized_country_id)
        metadata = self.metadata_extractor.extract(
            raw_text=parsed.raw_text,
            entity_matches={
                "company": linked_company,
                "agency": linked_agency,
                "project": linked_project,
                "budget": budget_match,
                "tender": procurement_match,
            },
        )

        evidence = self.extractor.extract(
            parsed=parsed,
            linked_company=linked_company,
            linked_agency=linked_agency,
            linked_project=linked_project,
            budget_match=budget_match,
            procurement_match=procurement_match,
            extracted_keywords=metadata.extracted_keywords,
            normalized_keywords=metadata.normalized_keywords,
            detected_entities=metadata.detected_entities,
        )

        evidence.evidence_strength = self.strength_calculator.calculate(
            entity_matches=[linked_company, linked_agency, linked_project],
            raw_text=parsed.raw_text,
            source_reference=parsed.source_reference,
            supporting_references=parsed.metadata.get("supporting_references") if parsed.metadata else None,
            publication_date=parsed.metadata.get("publication_date") if parsed.metadata else None,
            country_code=normalized_country_id,
        )
        return evidence


class EvidenceIngestionService:
    """Ingest parsed document evidence into the repository."""

    def __init__(self, repository: EvidenceRepository) -> None:
        self.repository = repository
        self.builder = EvidenceBuilder()
        self.relationship_builder = RelationshipBuilder(
            RelationshipRepository(repository.db)
        )

    def ingest(self, document: EvidenceDocument) -> Evidence:
        evidence = self.builder.build(document)
        created_evidence = self.repository.create(evidence)
        self.relationship_builder.build(created_evidence)
        return created_evidence
