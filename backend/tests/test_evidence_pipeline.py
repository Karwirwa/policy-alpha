import pytest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.models.evidence import Evidence
from app.services.document_parser import EvidenceDocument, ParsedDocument
from app.services.evidence_extractor import EvidenceExtractor
from app.services.evidence_strength import EvidenceStrengthCalculator
from app.services.evidence_builder import EvidenceBuilder
from app.services.entity_resolution import EntityResolutionService, EntityMatch


def test_evidence_extractor_preserves_metadata_and_normalizes_country_id():
    publication_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    last_verified = datetime(2025, 1, 2, tzinfo=timezone.utc)
    parsed = ParsedDocument(
        document_id="doc1",
        country_id="country_kenya",
        raw_text="Sample evidence text.",
        source_reference="http://example.com",
        connector_name="connector",
        title="Evidence Title",
        summary="Evidence summary.",
        page_number=1,
        section="Section A",
        metadata={
            "publication_date": publication_date,
            "language": "en",
            "government_level": "national",
            "last_verified": last_verified,
        },
    )

    evidence = EvidenceExtractor().extract(
        parsed=parsed,
        linked_company=EntityMatch(entity_id="company_bamburi", canonical_name="Bamburi Cement PLC", match_score=1.0),
        linked_agency=EntityMatch(entity_id="agency_finance", canonical_name="Ministry of Finance", match_score=1.0),
        linked_project=EntityMatch(entity_id="project_infrastructure", canonical_name="Infrastructure Project", match_score=1.0),
        budget_match=EntityMatch(entity_id="budget_kenya", canonical_name="Budget", match_score=0.8),
        procurement_match=EntityMatch(entity_id="tender_kenya", canonical_name="Tender", match_score=0.8),
        extracted_keywords=["sample"],
        normalized_keywords=["sample"],
        detected_entities=["Bamburi"],
    )

    assert evidence.publication_date == publication_date
    assert evidence.language == "en"
    assert evidence.government_level == "national"
    assert evidence.last_verified == last_verified
    assert evidence.country_id == "kenya"


def test_evidence_strength_handles_fresh_stale_and_country_modifiers():
    calculator = EvidenceStrengthCalculator()
    entity_matches = [EntityMatch(entity_id="company_bamburi", canonical_name="Bamburi Cement PLC", match_score=1.0)]

    fresh_date = datetime.now(timezone.utc) - timedelta(days=30)
    stale_date = datetime.now(timezone.utc) - timedelta(days=400)

    fresh_score = calculator.calculate(
        entity_matches=entity_matches,
        raw_text="Sample text.",
        source_reference="http://example.com",
        supporting_references=["ref1"],
        publication_date=fresh_date,
        country_code="country_kenya",
    )
    stale_score = calculator.calculate(
        entity_matches=entity_matches,
        raw_text="Sample text.",
        source_reference="http://example.com",
        supporting_references=["ref1"],
        publication_date=stale_date,
        country_code="usa",
    )
    missing_date_score = calculator.calculate(
        entity_matches=entity_matches,
        raw_text="Sample text.",
        source_reference="http://example.com",
        supporting_references=None,
        publication_date=None,
        country_code="CAN",
    )

    assert fresh_score > stale_score
    assert stale_score == 0.0
    assert missing_date_score > 0.0

    usa_score = calculator.calculate(
        entity_matches=entity_matches,
        raw_text="Sample text.",
        source_reference="http://example.com",
        supporting_references=None,
        publication_date=fresh_date,
        country_code="usa",
    )
    kenya_score = calculator.calculate(
        entity_matches=entity_matches,
        raw_text="Sample text.",
        source_reference="http://example.com",
        supporting_references=None,
        publication_date=fresh_date,
        country_code="kenya",
    )
    assert usa_score > kenya_score


def test_evidence_builder_forwards_normalized_country_code_and_preserves_metadata(monkeypatch):
    builder = EvidenceBuilder()
    captured = {}

    def make_resolver(key):
        def _resolve(text, country_code=None):
            captured[key] = country_code
            return EntityMatch(entity_id=f"{key}_id", canonical_name=key.title(), match_score=1.0)

        return _resolve

    builder.resolver.resolve_company = make_resolver("company")
    builder.resolver.resolve_agency = make_resolver("agency")
    builder.resolver.resolve_project = make_resolver("project")
    builder.resolver.resolve_budget = make_resolver("budget")
    builder.resolver.resolve_procurement = make_resolver("procurement")

    builder.metadata_extractor.extract = lambda raw_text, entity_matches: SimpleNamespace(
        extracted_keywords=[], normalized_keywords=[], detected_entities=[]
    )
    builder.strength_calculator.calculate = lambda **kwargs: 0.5

    publication_date = datetime(2025, 2, 1, tzinfo=timezone.utc)
    document = EvidenceDocument(
        document_id="doc_builder",
        country_id="country_kenya",
        raw_text="Bamburi Cement PLC issued a statement.",
        source_reference="http://example.com",
        connector_name="connector",
        title="Bamburi Cement Statement",
        metadata={"publication_date": publication_date},
    )

    evidence = builder.build(document)

    assert captured["company"] == "kenya"
    assert captured["agency"] == "kenya"
    assert captured["project"] == "kenya"
    assert captured["budget"] == "kenya"
    assert captured["procurement"] == "kenya"
    assert evidence.country_id == "kenya"
    assert evidence.publication_date == publication_date


def test_entity_resolution_service_forwards_country_code(monkeypatch):
    service = EntityResolutionService()
    captured = {}

    def record(text, country_code=None):
        captured["country_code"] = country_code
        return EntityMatch(entity_id="resolved", canonical_name="Resolved", match_score=1.0)

    service.registry._resolver_map["company"].resolve = record
    service.resolve_company("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.registry._resolver_map["agency"].resolve = record
    service.resolve_agency("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.registry._resolver_map["project"].resolve = record
    service.resolve_project("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.registry._resolver_map["budget"].resolve = record
    service.resolve_budget("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.registry._resolver_map["tender"].resolve = record
    service.resolve_procurement("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.registry._resolver_map["country"].resolve = record
    service.resolve_country("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.registry._resolver_map["agency"].resolve = record
    service.resolve_ministry("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"

    service.resolve_department("text", country_code="country_kenya")
    assert captured["country_code"] == "country_kenya"
