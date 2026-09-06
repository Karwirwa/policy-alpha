from types import SimpleNamespace
from datetime import datetime, timezone

from app.services.evidence_builder import EvidenceBuilder
from app.services.document_parser import EvidenceDocument
from app.services.entity_resolution import EntityMatch


def test_builder_calls_resolvers_with_none_when_country_missing():
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

    document = EvidenceDocument(
        document_id="doc_builder_no_country",
        country_id=None,
        raw_text="Some text.",
        source_reference="http://example.com",
        connector_name="connector",
        title="Title",
        metadata=None,
    )

    evidence = builder.build(document)

    assert captured["company"] is None
    assert captured["agency"] is None
    assert captured["project"] is None
    assert captured["budget"] is None
    assert captured["procurement"] is None
    assert evidence.country_id is None
    assert evidence.publication_date is None
