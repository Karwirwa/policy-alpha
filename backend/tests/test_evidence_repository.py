import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.country import Country
from app.models.document import Document
from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_get_by_document_hash(session):
    repo = EvidenceRepository(session)
    # create a document and evidence with a specific hash
    doc = Document(id="doc1", name="Doc 1", source_reference="http://example")
    session.add(doc)
    ev = Evidence(
        document_id="doc1",
        country_id="kenya",
        title="Test",
        summary="s",
        raw_text="r",
        document_hash="hash123",
        source_reference="http://example",
        evidence_strength=0.5,
        extracted_at=datetime.now(timezone.utc),
    )
    # ensure country exists so FK is satisfied
    from app.models.country import Country
    session.add(Country(id="kenya", name="Kenya"))
    session.commit()

    session.add(ev)
    session.commit()

    found = repo.get_by_document_hash("hash123")
    assert found is not None
    assert found.document_hash == "hash123"

    not_found = repo.get_by_document_hash("nope")
    assert not_found is None


def test_duplicate_by_title_company_publication_date(session):
    repo = EvidenceRepository(session)
    doc1 = Document(id="doc1", name="Doc 1", source_reference="http://example")
    doc2 = Document(id="doc2", name="Doc 2", source_reference="http://example")
    session.add_all([doc1, doc2])
    session.add(Country(id="kenya", name="Kenya"))
    session.commit()

    publication_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ev1 = Evidence(
        document_id="doc1",
        country_id="kenya",
        title="Test Duplicate",
        summary="s",
        raw_text="r",
        document_hash="hash123",
        company_id="company_bamburi",
        publication_date=publication_date,
        source_reference="http://example",
        evidence_strength=0.5,
        extracted_at=datetime.now(timezone.utc),
    )
    created1 = repo.create(ev1)

    ev2 = Evidence(
        document_id="doc2",
        country_id="kenya",
        title="Test Duplicate",
        summary="s2",
        raw_text="r2",
        document_hash="different_hash",
        company_id="company_bamburi",
        publication_date=publication_date,
        source_reference="http://example",
        evidence_strength=0.4,
        extracted_at=datetime.now(timezone.utc),
    )
    created2 = repo.create(ev2)

    assert created1.id == created2.id
    assert session.query(Evidence).count() == 1


def test_get_by_project(session):
    repo = EvidenceRepository(session)
    doc = Document(id="doc_project", name="Doc Project", source_reference="http://example")
    session.add(doc)
    session.add(Country(id="kenya", name="Kenya"))
    session.commit()

    evidence = Evidence(
        document_id="doc_project",
        country_id="kenya",
        project_id="project_road_expansion",
        title="Project Evidence",
        summary="s",
        raw_text="r",
        document_hash="hash_proj",
        source_reference="http://example",
        evidence_strength=0.3,
        extracted_at=datetime.now(timezone.utc),
    )
    repo.create(evidence)

    results = repo.get_by_project("project_road_expansion")
    assert len(results) == 1
    assert results[0].project_id == "project_road_expansion"


def test_get_latest(session):
    repo = EvidenceRepository(session)
    doc1 = Document(id="doc_latest_1", name="Doc Latest 1", source_reference="http://example")
    doc2 = Document(id="doc_latest_2", name="Doc Latest 2", source_reference="http://example")
    session.add_all([doc1, doc2])
    session.add(Country(id="kenya", name="Kenya"))
    session.commit()

    evidence1 = Evidence(
        document_id="doc_latest_1",
        country_id="kenya",
        title="Latest 1",
        summary="s1",
        raw_text="r1",
        document_hash="hash_latest_1",
        source_reference="http://example",
        evidence_strength=0.3,
        extracted_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    evidence2 = Evidence(
        document_id="doc_latest_2",
        country_id="kenya",
        title="Latest 2",
        summary="s2",
        raw_text="r2",
        document_hash="hash_latest_2",
        source_reference="http://example",
        evidence_strength=0.4,
        extracted_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    repo.create(evidence1)
    repo.create(evidence2)

    latest = repo.get_latest(limit=2)
    assert len(latest) == 2
    assert latest[0].document_id == "doc_latest_2"
    assert latest[1].document_id == "doc_latest_1"


def test_canonical_country_id_normalization_on_create(session):
    repo = EvidenceRepository(session)
    doc = Document(id="doc3", name="Doc 3", source_reference="http://example")
    session.add(doc)
    session.commit()

    ev = Evidence(
        document_id="doc3",
        country_id="country_kenya",
        title="Canonical Country",
        summary="s",
        raw_text="r",
        document_hash="hash_kenya",
        source_reference="http://example",
        evidence_strength=0.2,
        extracted_at=datetime.now(timezone.utc),
    )
    created = repo.create(ev)

    assert created.country_id == "kenya"
    assert session.get(Country, "kenya") is not None


def test_unsupported_country_prevents_creation(session):
    repo = EvidenceRepository(session)
    # create document
    doc = Document(id="doc2", name="Doc 2", source_reference="http://example")
    session.add(doc)
    session.commit()

    ev = Evidence(
        document_id="doc2",
        country_id="unsupported_country",
        title="Test2",
        summary="s",
        raw_text="r",
        document_hash="hash456",
        source_reference="http://example",
        evidence_strength=0.2,
        extracted_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError):
        repo.create(ev)
