from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.evidence import Evidence

_SECTOR_KEYWORDS = {
    "water": ("water", "borehole", "sewer", "sanitation"),
    "roads": ("road", "highway", "bridge", "samatar wajir", "kenha", "kura"),
    "health": ("medical", "hospital", "health"),
    "education": ("school", "classroom", "education", "university"),
    "ict": ("ict", "broadband", "software", "network", "cbk", "communication"),
    "energy": ("energy", "power", "solar", "ketraco", "electricity"),
    "construction": ("construction", "building", "renovation", "office block"),
    "consultancy": ("consultancy", "rfp", "expression of interest", "audit", "study"),
}
_SECTOR_WEIGHTS = {"water": 20, "roads": 20, "energy": 20, "health": 20, "ict": 15}
_CATEGORY_SCORES = {2: 20, 1: 15, 3: 10, 4: 12}
_MINISTRY_PREFIXES = {
    "KSMWENC": "Kisumu Water & Environment",
    "KENHA": "Kenya National Highways Authority",
    "KETRACO": "Kenya Electricity Transmission",
    "KPA": "Kenya Ports Authority",
    "NACOSTI": "National Commission for Science, Technology & Innovation",
    "CBK": "Central Bank of Kenya",
    "NKCC": "Nairobi City County",
    "KURA": "Kenya Urban Roads Authority",
    "KAA": "Kenya Airports Authority",
    "KPLC": "Kenya Power",
}


def _summary_values(summary_json: str | None) -> dict[str, Any]:
    if not summary_json:
        return {}
    try:
        value = json.loads(summary_json)
    except (TypeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _evidence_metadata(evidence: Evidence) -> dict[str, Any]:
    metadata = _summary_values(evidence.raw_text)
    metadata.update(_summary_values(evidence.summary))
    return metadata


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, time.min)
    elif isinstance(value, str) and value.strip():
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                parsed = datetime.combine(date.fromisoformat(normalized), time.min)
            except ValueError:
                return None
    else:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _has_keyword(text: str, keyword: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text) is not None


def classify_sector(title: str) -> str:
    """Classify a tender title into a deterministic investment sector."""
    normalized = re.sub(r"[-_/]+", " ", title.casefold())
    for sector, keywords in _SECTOR_KEYWORDS.items():
        if any(_has_keyword(normalized, keyword) for keyword in keywords):
            return sector
        if sector == "health" and "insurance" in normalized and "medical" in normalized:
            return sector
    return "other"


def _procuring_entity_name(metadata: dict[str, Any]) -> str | None:
    name = metadata.get("pe_name")
    if name is None and isinstance(metadata.get("pe"), dict):
        name = metadata["pe"].get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def extract_ministry_from_ref(
    document_id: str, summary_json: str, raw_text: str = ""
) -> str:
    """Derive an entity name from full tender JSON, summary, or known reference."""
    raw_metadata = _summary_values(raw_text)
    raw_name = _procuring_entity_name(raw_metadata)
    if raw_name:
        return raw_name

    summary = _summary_values(summary_json)
    summary_name = _procuring_entity_name(summary)
    if summary_name:
        return summary_name

    prefix = re.split(r"[/\s]", document_id.strip(), maxsplit=1)[0]
    normalized_prefix = re.sub(r"[^A-Z0-9]", "", prefix.upper())
    if normalized_prefix in _MINISTRY_PREFIXES:
        return _MINISTRY_PREFIXES[normalized_prefix]

    for metadata in (raw_metadata, summary):
        pe_id = metadata.get("pe_id")
        if pe_id is not None and str(pe_id).strip():
            return str(pe_id).strip()
    return "Unspecified"


def extract_deadline(summary_json: str) -> datetime | None:
    """Extract the tender closing time from its JSON summary."""
    return _parse_datetime(_summary_values(summary_json).get("close_at"))


def _published_at(evidence: Evidence, summary: dict[str, Any]) -> datetime | None:
    return _parse_datetime(summary.get("published_at")) or _parse_datetime(
        evidence.publication_date
    )


def _category_score(summary: dict[str, Any]) -> int:
    try:
        category_id = int(summary.get("procurement_category_id"))
    except (TypeError, ValueError):
        return 0
    return _CATEGORY_SCORES.get(category_id, 0)


def compute_kenya_opportunity_score(evidence: Evidence, sector: str) -> float:
    """Score a Kenya tender using recency, verification, sector, and category."""
    summary = _evidence_metadata(evidence)
    score = 0

    published_at = _published_at(evidence, summary)
    if published_at is not None:
        days_old = (datetime.now(timezone.utc) - published_at).days
        if days_old <= 30:
            score += 30
        elif days_old <= 90:
            score += 20
        else:
            score += 10

    verification_points = {"verified": 20, "unverified": 10, "illustrative": 0}
    score += verification_points.get(evidence.verification_status, 0)
    score += _SECTOR_WEIGHTS.get(sector, 10)

    deadline = _parse_datetime(summary.get("close_at"))
    now = datetime.now(timezone.utc)
    if deadline is not None and now <= deadline <= now + timedelta(days=30):
        score += 20

    score += _category_score(summary)
    return float(min(score, 100))


def derive_kenya_opportunities(
    db: Session,
    limit: int | None = 20,
    include_illustrative: bool = False,
) -> list[dict[str, Any]]:
    """Return Kenya evidence ranked as tender opportunities."""
    query = db.query(Evidence).filter(Evidence.country_id == "kenya")
    if not include_illustrative:
        query = query.filter(Evidence.verification_status != "illustrative")

    opportunities: list[dict[str, Any]] = []
    for evidence in query.all():
        summary = evidence.summary or ""
        metadata = _evidence_metadata(evidence)
        deadline = _parse_datetime(metadata.get("close_at"))
        sector = classify_sector(evidence.title)
        opportunities.append(
            {
                "evidence_id": evidence.id,
                "document_id": evidence.document_id,
                "title": evidence.title,
                "sector": sector,
                "ministry": extract_ministry_from_ref(
                    evidence.document_id, summary, evidence.raw_text or ""
                ),
                "deadline": deadline.isoformat() if deadline else None,
                "score": compute_kenya_opportunity_score(evidence, sector),
                "source_url": evidence.source_reference,
                "verification_status": evidence.verification_status,
                "summary_excerpt": summary[:200],
            }
        )

    opportunities.sort(key=lambda item: (-item["score"], item["evidence_id"]))
    return opportunities if limit is None else opportunities[: max(0, limit)]
