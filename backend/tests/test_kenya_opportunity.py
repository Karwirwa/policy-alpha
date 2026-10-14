import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.init import Base
from app.db.database import get_db
from app.main import app
from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.services.kenya_opportunity import (
    classify_sector,
    derive_kenya_opportunities,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def _add_tender(
    db_session,
    *,
    title: str,
    document_id: str,
    verification_status: str = "unverified",
    published_days_ago: int = 10,
    close_days_from_now: int = 10,
    category_id: int = 2,
) -> Evidence:
    now = datetime.now(timezone.utc)
    summary = json.dumps(
        {
            "pe_name": "Kenya Ministry of Water",
            "published_at": (now - timedelta(days=published_days_ago)).isoformat(),
            "close_at": (now + timedelta(days=close_days_from_now)).isoformat(),
            "procurement_category_id": category_id,
        }
    )
    evidence = Evidence(
        document_id=document_id,
        country_id="kenya",
        title=title,
        summary=summary,
        raw_text=f"Illustrative tender text for {title}.",
        document_hash=f"hash-{document_id}",
        connector_name="kenya",
        verification_status=verification_status,
        source_reference=f"https://www.tenders.go.ke/api/tender/{document_id}",
        evidence_strength=0.5,
    )
    return EvidenceRepository(db_session).create(evidence)


def test_classify_sector_returns_expected_for_known_titles():
    assert classify_sector("PAGA WATER PROJECT PHASE 2") == "water"
    assert classify_sector("Bridge construction and highway works") == "roads"
    assert classify_sector("Provision of medical insurance cover") == "health"
    assert classify_sector("Renovation of school classrooms") == "education"
    assert classify_sector("ICT broadband network upgrade") == "ict"
    assert classify_sector("KETRACO solar power equipment") == "energy"
    assert classify_sector("Construction of office block") == "construction"
    assert classify_sector("Expression of Interest for audit study") == "consultancy"
    assert classify_sector("Supply of office stationery") == "other"


def test_derive_opportunities_returns_ranked_list(db_session):
    older = _add_tender(
        db_session,
        title="Office stationery supply",
        document_id="STATIONERY/001",
        published_days_ago=120,
        close_days_from_now=60,
        category_id=1,
    )
    newer = _add_tender(
        db_session,
        title="Kenya water pipeline project",
        document_id="KSMWENC/001",
        published_days_ago=5,
        close_days_from_now=10,
        category_id=2,
    )

    opportunities = derive_kenya_opportunities(db_session)

    assert len(opportunities) == 2
    assert opportunities[0]["evidence_id"] == newer.id
    assert opportunities[-1]["evidence_id"] == older.id
    assert opportunities[0]["ministry"] == "Kenya Ministry of Water"
    assert opportunities[0]["sector"] == "water"


def test_derive_opportunities_reads_metadata_from_full_raw_text(db_session):
    evidence = _add_tender(
        db_session,
        title="PAGA WATER PROJECT PHASE 2",
        document_id="KSMWENC/RAW",
    )
    raw_metadata = json.dumps(
        {
            "pe_name": "Kisumu Water Entity",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "close_at": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
            "procurement_category_id": 2,
        }
    )
    evidence.summary = raw_metadata[:100]
    evidence.raw_text = raw_metadata
    db_session.commit()

    opportunity = derive_kenya_opportunities(db_session)[0]

    assert opportunity["deadline"] is not None
    assert opportunity["ministry"] == "Kisumu Water Entity"
    assert opportunity["score"] == 100.0


def test_kenya_opportunities_endpoint_returns_200(client, db_session):
    _add_tender(
        db_session,
        title="PAGA WATER PROJECT PHASE 2",
        document_id="KSMWENC/1470",
    )

    response = client.get("/api/v1/kenya/opportunities?limit=5")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["opportunities"][0]["sector"] == "water"
    assert payload["opportunities"][0]["source_url"].startswith(
        "https://www.tenders.go.ke/"
    )


def test_kenya_sectors_endpoint_returns_counts(client, db_session):
    _add_tender(
        db_session,
        title="PAGA WATER PROJECT PHASE 2",
        document_id="KSMWENC/WATER",
    )
    _add_tender(
        db_session,
        title="Road maintenance works",
        document_id="KURA/ROAD",
    )

    response = client.get("/api/v1/kenya/sectors")

    assert response.status_code == 200
    sectors = {item["name"]: item for item in response.json()["sectors"]}
    assert sectors["water"]["count"] == 1
    assert sectors["roads"]["count"] == 1
    assert sectors["water"]["avg_score"] > 0


def test_kenya_ministries_endpoint_returns_counts(client, db_session):
    _add_tender(
        db_session,
        title="PAGA WATER PROJECT PHASE 2",
        document_id="KSMWENC/WATER",
    )
    _add_tender(
        db_session,
        title="Another water borehole project",
        document_id="KSMWENC/BOREHOLE",
    )

    response = client.get("/api/v1/kenya/ministries")

    assert response.status_code == 200
    ministry = response.json()["ministries"][0]
    assert ministry["name"] == "Kenya Ministry of Water"
    assert ministry["count"] == 2
    assert ministry["total_score"] > 0


def test_include_illustrative_false_excludes_illustrative(client, db_session):
    _add_tender(
        db_session,
        title="Verified water tender",
        document_id="WATER/REAL",
        verification_status="verified",
    )
    _add_tender(
        db_session,
        title="Illustrative road tender",
        document_id="ROAD/DEMO",
        verification_status="illustrative",
    )

    response = client.get(
        "/api/v1/kenya/opportunities?include_illustrative=false"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert [item["verification_status"] for item in payload["opportunities"]] == [
        "verified"
    ]
