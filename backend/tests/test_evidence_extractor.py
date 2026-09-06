import pytest
from datetime import datetime, timezone

from app.services.document_parser import ParsedDocument
from app.services.evidence_extractor import EvidenceExtractor
from app.services.entity_resolution import EntityMatch


def make_parsed(**overrides):
    base = dict(
        document_id="doc_hash",
        country_id="country_kenya",
        raw_text="Sample    text with   irregular   whitespace.",
        source_reference="http://example.com",
        connector_name="connector",
        title="  Title with  extra   spaces  ",
        summary="Summary",
        page_number=1,
        section="Section A",
        metadata={
            "publication_date": datetime(2025, 1, 1, tzinfo=timezone.utc),
            "language": "en",
            "government_level": "national",
            "last_verified": datetime(2025, 1, 2, tzinfo=timezone.utc),
        },
    )
    base.update(overrides)
    return ParsedDocument(**base)


def test_hash_is_deterministic_for_equivalent_inputs():
    p1 = make_parsed()
    p2 = make_parsed()
    # normalize whitespace differences
    p2.title = "Title with extra spaces"
    p2.raw_text = "Sample text with irregular whitespace."

    h1 = EvidenceExtractor._compute_document_hash(p1)
    h2 = EvidenceExtractor._compute_document_hash(p2)
    assert h1 == h2, "Hashes should be equal for semantically-equivalent inputs"


def test_hash_differs_for_material_changes():
    p1 = make_parsed()
    p2 = make_parsed()
    p2.title = "A materially different title"

    h1 = EvidenceExtractor._compute_document_hash(p1)
    h2 = EvidenceExtractor._compute_document_hash(p2)
    assert h1 != h2


def test_extract_handles_missing_metadata_gracefully():
    parsed = make_parsed(metadata=None)

    ev = EvidenceExtractor().extract(
        parsed=parsed,
        linked_company=EntityMatch(entity_id=None, canonical_name=None, match_score=0.0),
        linked_agency=EntityMatch(entity_id=None, canonical_name=None, match_score=0.0),
        linked_project=EntityMatch(entity_id=None, canonical_name=None, match_score=0.0),
        budget_match=EntityMatch(entity_id=None, canonical_name=None, match_score=0.0),
        procurement_match=EntityMatch(entity_id=None, canonical_name=None, match_score=0.0),
        extracted_keywords=[],
        normalized_keywords=[],
        detected_entities=[],
    )

    # Should not raise and optional metadata fields should be None
    assert ev.publication_date is None
    assert ev.language is None
    assert ev.government_level is None
    assert ev.last_verified is None
    assert isinstance(ev.document_hash, str) and len(ev.document_hash) > 0
