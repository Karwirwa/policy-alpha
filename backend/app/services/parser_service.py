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


# New helper: prepare payloads from extracted PDF structure
def prepare_from_extracted_pdf(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """Convert extracted PDF structure into a single budget-like payload.

    This function makes deterministic choices:
    - program/ministry inferred from headings or first page lines
    - budget amount searched via regex for currency/number patterns
    - projects are extracted from sections that look like project entries

    Each project and the top-level payload will include evidence fields with
    page/section/paragraph references.
    """
    pages = extracted.get("pages", [])
    # Flatten raw text for simple heuristics
    full_text = "\n\n".join(p.get("raw_text", "") for p in pages)

    # Heuristics
    program = None
    ministry = None
    country = None
    year = None
    currency = None
    amount = None
    sector = None
    summary = None

    # Try to infer program/ministry from first page headings
    if pages:
        first_page = pages[0]
        # look for a heading-like first section
        sections = first_page.get("sections", [])
        if sections:
            heading = sections[0].get("heading")
            if heading:
                program = heading
            # detect ministry in first paragraphs
            paras = sections[0].get("paragraphs", [])
            for p in paras[:5]:
                if "ministry" in p.lower():
                    ministry = p
                    break

    # Detect budget amount using simple regex for numbers with commas or digits
    import re

    m = re.search(r"(KES|USD|EUR|KES\s)?\s?([0-9\,]{5,})", full_text)
    if m:
        currency = m.group(1) or None
        amt = m.group(2).replace(",", "")
        try:
            amount = int(amt)
        except Exception:
            amount = None

    # Year detection
    my = re.search(r"(20[2-9][0-9])", full_text)
    if my:
        year = int(my.group(1))

    # sector inference: look for lines containing 'housing' or 'infrastructure'
    if re.search(r"housing", full_text, re.IGNORECASE):
        sector = "Housing"
    elif re.search(r"infrastructure", full_text, re.IGNORECASE):
        sector = "Infrastructure"

    # Summary: first 500 chars of full_text
    summary = full_text[:500]

    # Extract projects by scanning pages and sections for entries that look like project ids
    projects = []
    for p in pages:
        page_no = p.get("page_number")
        for s_idx, s in enumerate(p.get("sections", [])):
            heading = s.get("heading")
            for para_idx, para in enumerate(s.get("paragraphs", [])):
                # simple project id heuristic
                pid_match = re.search(r"([A-Z]{2,}-\d{3})", para)
                if pid_match:
                    proj = {
                        "project_id": pid_match.group(1),
                        "title": heading or (para[:100]),
                        "description": para,
                        "amount": None,
                        "start_date": None,
                        "end_date": None,
                        "lead_company": None,
                        "evidence": {"page": page_no, "section": s_idx, "paragraph": para_idx},
                    }
                    # Try to find an amount in the paragraph
                    amt_m = re.search(r"(KES|USD|EUR|KES\s)?\s?([0-9\,]{5,})", para)
                    if amt_m:
                        a = amt_m.group(2).replace(",", "")
                        try:
                            proj["amount"] = int(a)
                        except Exception:
                            proj["amount"] = None
                    # Try to detect company names (very naive: look for known proper nouns uppercase)
                    comp_m = re.search(r"([A-Z][A-Za-z0-9\.&\s]{2,50} (Ltd\.|Inc\.|PLC))", para)
                    if comp_m:
                        proj["lead_company"] = comp_m.group(1).strip()
                    projects.append(proj)

    payload = {
        "country": country or "",
        "ministry": ministry or "",
        "program": program or "",
        "budget": amount or 0,
        "currency": currency,
        "year": year or 0,
        "sector": sector,
        "summary": summary,
        "projects": projects,
        "companies": [],
    }

    return payload
