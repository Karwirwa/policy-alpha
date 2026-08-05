from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class GovernmentDocument:
    connector_name: str
    country_code: str
    source_url: str
    document_id: str
    title: str | None = None
    publication_date: date | None = None
    document_type: str | None = None
    language: str | None = None
    raw_content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
