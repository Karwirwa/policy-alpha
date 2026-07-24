"""PDF document extractor service using pdfplumber.

Responsibilities:
- Read a PDF file from disk
- Extract text per page
- Heuristically detect headings and section breaks
- Return a structured representation preserving page numbers, sections and paragraphs

This service does NOT use AI.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import re

try:
    import pdfplumber
except Exception:  # pdfplumber may not be installed in all environments
    pdfplumber = None


def _split_into_sections(page_text: str) -> List[Dict[str, Any]]:
    """Heuristic section splitter: treats lines in ALL CAPS or lines ending with ':' as headings."""
    lines = [l.rstrip() for l in page_text.splitlines()]
    sections = []
    current_section = {"heading": None, "paragraphs": []}
    current_para_lines: List[str] = []

    def flush_paragraph():
        nonlocal current_para_lines
        if current_para_lines:
            para = " ".join([l.strip() for l in current_para_lines if l.strip()])
            if para:
                current_section["paragraphs"].append(para)
            current_para_lines = []

    for line in lines:
        if not line.strip():
            flush_paragraph()
            continue
        # Heading heuristic: line in ALL CAPS or ends with ':' and shorter than 200 chars
        stripped = line.strip()
        if (stripped.isupper() and len(stripped) < 200) or stripped.endswith(":"):
            # flush previous paragraph & section
            flush_paragraph()
            if current_section["heading"] or current_section["paragraphs"]:
                sections.append(current_section)
            current_section = {"heading": stripped.rstrip(':'), "paragraphs": []}
            continue
        # Otherwise accumulate into paragraph
        current_para_lines.append(line)

    flush_paragraph()
    if current_section["heading"] or current_section["paragraphs"]:
        sections.append(current_section)

    # If document lacks clear sections, return a single section with all text as one paragraph
    if not sections:
        full_text = "\n".join(lines).strip()
        if full_text:
            return [{"heading": None, "paragraphs": [full_text]}]
        return []

    return sections


def extract_pdf(path: Path) -> Dict[str, Any]:
    """Extract structured content from the PDF at path.

    Returns a dict with keys: path, extracted_at, pages where pages is a list of
    {page_number, sections:[{heading, paragraphs:[str]}]}.
    """
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is not available. Install pdfplumber in the environment.")

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            sections = _split_into_sections(text)
            pages.append({"page_number": i, "sections": sections, "raw_text": text})

    return {"path": str(path), "extracted_at": datetime.utcnow(), "pages": pages}
