from __future__ import annotations

import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository

DEMO_CONNECTOR = "demo_kenya"
_KENYA_TENDER_TITLES = (
    "Construction of bridge",
    "Annex building works",
    "Road maintenance works",
    "Supply of hospital beds",
    "Supply of medical equipment",
)


def seed_kenya_demo(db: Session) -> int:
    """Create clearly marked illustrative Kenya evidence if no demo seed exists."""
    existing_demo = db.scalar(
        select(Evidence.id).where(Evidence.connector_name == DEMO_CONNECTOR).limit(1)
    )
    if existing_demo is not None:
        return 0

    repository = EvidenceRepository(db)
    inserted = 0
    for index, tender_title in enumerate(_KENYA_TENDER_TITLES, start=1):
        document_id = f"demo_kenya_tender_{index:03d}"
        title = f"DEMO - {tender_title} (illustrative)"
        raw_text = (
            "ILLUSTRATIVE DEMO ONLY. This is not a real Kenyan tender notice "
            f"or verified procurement record. Example title: {tender_title}."
        )
        evidence = Evidence(
            document_id=document_id,
            country_id="kenya",
            title=title,
            summary="Illustrative demonstration record; not an actual tender notice.",
            raw_text=raw_text,
            document_hash=hashlib.sha256(document_id.encode("utf-8")).hexdigest(),
            connector_name=DEMO_CONNECTOR,
            verification_status="illustrative",
            source_reference=f"demo://kenya/tender/{index:03d}",
            evidence_strength=0.0,
        )
        if repository.create(evidence) is evidence:
            inserted += 1

    return inserted
