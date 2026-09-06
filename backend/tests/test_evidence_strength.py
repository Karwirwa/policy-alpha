from datetime import datetime, timedelta, timezone

from app.services.evidence_strength import EvidenceStrengthCalculator
from app.services.entity_resolution import EntityMatch


def test_supporting_references_increases_score_and_score_bounds():
    calc = EvidenceStrengthCalculator()
    matches = [EntityMatch(entity_id="company_a", canonical_name="A", match_score=1.0)]
    fresh = datetime.now(timezone.utc) - timedelta(days=30)

    score_no_support = calc.calculate(
        entity_matches=matches,
        raw_text="text",
        source_reference="http://example",
        supporting_references=None,
        publication_date=fresh,
        country_code="kenya",
    )

    score_with_support = calc.calculate(
        entity_matches=matches,
        raw_text="text",
        source_reference="http://example",
        supporting_references=["r1", "r2", "r3"],
        publication_date=fresh,
        country_code="kenya",
    )

    assert 0.0 <= score_no_support <= 1.0
    assert 0.0 <= score_with_support <= 1.0
    assert score_with_support >= score_no_support


def test_fresh_vs_stale_and_country_modifier_variants():
    calc = EvidenceStrengthCalculator()
    matches = [EntityMatch(entity_id="company_a", canonical_name="A", match_score=1.0)]
    fresh = datetime.now(timezone.utc) - timedelta(days=30)
    stale = datetime.now(timezone.utc) - timedelta(days=400)

    fresh_score = calc.calculate(
        entity_matches=matches,
        raw_text="text",
        source_reference="http://example",
        supporting_references=None,
        publication_date=fresh,
        country_code="usa",
    )
    stale_score = calc.calculate(
        entity_matches=matches,
        raw_text="text",
        source_reference="http://example",
        supporting_references=None,
        publication_date=stale,
        country_code="usa",
    )

    # fresh should be greater than stale; stale can be 0.0 per implementation
    assert fresh_score > stale_score
    assert 0.0 <= stale_score <= 1.0

    # country modifier variants: US vs usa should behave consistently
    score_us_upper = calc.calculate(
        entity_matches=matches,
        raw_text="text",
        source_reference="http://example",
        supporting_references=None,
        publication_date=fresh,
        country_code="US",
    )
    score_us_lower = calc.calculate(
        entity_matches=matches,
        raw_text="text",
        source_reference="http://example",
        supporting_references=None,
        publication_date=fresh,
        country_code="usa",
    )
    assert abs(score_us_upper - score_us_lower) < 1e-6


def test_entity_match_edge_cases_and_score_bounds():
    calc = EvidenceStrengthCalculator()

    # No entity matches
    no_entities_score = calc.calculate(
        entity_matches=[],
        raw_text="short",
        source_reference="",
        supporting_references=None,
        publication_date=None,
        country_code=None,
    )
    assert 0.0 <= no_entities_score <= 1.0

    # Multiple entity matches
    many_matches = [
        EntityMatch(entity_id="a", canonical_name="A", match_score=1.0),
        EntityMatch(entity_id="b", canonical_name="B", match_score=0.8),
        EntityMatch(entity_id=None, canonical_name=None, match_score=0.0),
    ]
    score_many = calc.calculate(
        entity_matches=many_matches,
        raw_text="long text " * 200,
        source_reference="http://example",
        supporting_references=None,
        publication_date=None,
        country_code="kenya",
    )
    assert 0.0 <= score_many <= 1.0
