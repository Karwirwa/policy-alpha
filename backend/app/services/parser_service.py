"""Parser service for budget JSON sample files.

Responsible for loading a JSON file, validating expected structure, and
converting into Python dictionaries suitable for repository insertion.
This service does NOT use AI.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json


REQUIRED_TOP_LEVEL = ["country", "ministry", "program", "budget", "year"]


def load_json(path: Path) -> Dict[str, Any]:
    """Load and parse JSON from the given path.

    Raises ValueError on invalid JSON or missing required fields.
    """
    if not path.exists():
        raise ValueError(f"File not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    # Basic validation
    for key in REQUIRED_TOP_LEVEL:
        if key not in raw:
            raise ValueError(f"Missing required field: {key}")

    # Ensure optional lists are present
    raw.setdefault("projects", [])
    raw.setdefault("companies", [])

    return raw


def prepare_budget_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize raw JSON into a budget payload dict for repository insertion."""
    return {
        "country": raw["country"],
        "ministry": raw["ministry"],
        "program": raw["program"],
        "amount": int(raw["budget"]),
        "currency": raw.get("currency"),
        "year": int(raw["year"]),
        "sector": raw.get("sector"),
        "summary": raw.get("summary"),
        "projects": raw.get("projects", []),
        "companies": raw.get("companies", []),
    }
