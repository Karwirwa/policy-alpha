import logging

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.init import Base
from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.services.demo_seed import DEMO_CONNECTOR, seed_kenya_demo


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield sessionmaker(bind=engine)
    engine.dispose()


def test_demo_seed_is_off_by_default(monkeypatch, caplog):
    from app import main

    settings = Settings(_env_file=None)
    assert settings.demo_seed_enabled is False

    monkeypatch.setattr(main, "init_db", lambda: None)
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(
        main,
        "seed_kenya_demo",
        lambda _session: pytest.fail("seed should be disabled by default"),
    )

    with caplog.at_level(logging.INFO):
        main.on_startup()

    assert "Demo seed skipped (DEMO_SEED_ENABLED=false)" in caplog.text


def test_demo_seed_creates_records_when_enabled(monkeypatch, session_factory):
    from app import main

    monkeypatch.setenv("DEMO_SEED_ENABLED", "true")
    settings = Settings(_env_file=None)
    assert settings.demo_seed_enabled is True

    monkeypatch.setattr(main, "init_db", lambda: None)
    monkeypatch.setattr(main, "get_settings", lambda: settings)
    monkeypatch.setattr(main, "SessionLocal", session_factory)

    main.on_startup()

    with session_factory() as session:
        records = session.scalars(
            select(Evidence).where(Evidence.connector_name == DEMO_CONNECTOR)
        ).all()
    assert len(records) == 5
    assert all(record.country_id == "kenya" for record in records)
    assert all(record.verification_status == "illustrative" for record in records)
    assert all(record.title.startswith("DEMO - ") for record in records)


def test_demo_seed_is_idempotent(session_factory):
    with session_factory() as session:
        assert seed_kenya_demo(session) == 5
        assert seed_kenya_demo(session) == 0
        count = session.scalar(
            select(func.count(Evidence.id)).where(
                Evidence.connector_name == DEMO_CONNECTOR
            )
        )
        assert count == 5

    with session_factory() as session:
        assert len(
            session.scalars(
                select(Evidence).where(Evidence.connector_name == DEMO_CONNECTOR)
            ).all()
        ) == 5


def test_evidence_filter_excludes_illustrative(session_factory):
    from app.api.evidence import list_evidence

    with session_factory() as session:
        assert seed_kenya_demo(session) == 5
        EvidenceRepository(session).create(
            Evidence(
                document_id="crawled_kenya_notice",
                country_id="kenya",
                title="Crawled Kenya notice",
                summary="A notice ingested by the crawler.",
                raw_text="Crawler-ingested evidence.",
                document_hash="crawled-kenya-notice-hash",
                connector_name="kenya",
                verification_status="unverified",
                source_reference="https://example.invalid/kenya/notice",
                evidence_strength=0.5,
            )
        )

        visible = list_evidence(
            include_illustrative=False, limit=50, offset=0, db=session
        )
        all_records = list_evidence(include_illustrative=True, limit=50, offset=0, db=session)

    assert [record.title for record in visible] == ["Crawled Kenya notice"]
    assert len(all_records) == 6
