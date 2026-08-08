import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.document import Document
from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.core.countries import normalize_country_id


def test_normalize_cases():
    assert normalize_country_id("kenya") == "kenya"
    assert normalize_country_id("country_kenya") == "kenya"
    assert normalize_country_id("KENYA") == "kenya"
    assert normalize_country_id("united states") == "united_states"
    assert normalize_country_id("country_united_states") == "united_states"
    assert normalize_country_id("not_a_country") is None


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_repository_accepts_legacy_country(session):
    repo = EvidenceRepository(session)
    # create a document and evidence with legacy country id
    doc = Document(id="doc1", name="Doc 1", source_reference="http://example")
    session.add(doc)
    # evidence with legacy country id should be normalized to canonical 'kenya'
    ev = Evidence(
        document_id="doc1",
        country_id="country_kenya",
        title="Test Legacy",
        summary="s",
        raw_text="r",
        document_hash="hash-legacy",
        source_reference="http://example",
        evidence_strength=0.5,
        extracted_at=None,
    )
    # ensure create works and Country row is created with canonical id
    session.commit()

    created = repo.create(ev)
    assert created is not None
    # Check that the country row exists with canonical id
    from app.models.country import Country

    country = session.get(Country, "kenya")
    assert country is not None
    assert country.name == "Kenya"
