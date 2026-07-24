"""Simple deterministic document parser for Milestone 2.

This service does NOT use AI. It accepts raw text and returns structured
information: a title (best-effort), basic metadata, and a list of text chunks.

Chunking strategy: split on paragraphs first, then combine until a target
maximum character size is reached. This is intentionally simple and
deterministic to validate the pipeline.

Placeholders are left for future entity extraction (companies, bills, etc.).
"""
from typing import Dict, List, Optional

MAX_CHARS = 1000


def extract_title(text: str) -> Optional[str]:
    """Best-effort title extraction: use first non-empty line up to a limit."""
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s[:200]
    return None


def chunk_text(text: str, max_chars: int = MAX_CHARS) -> List[Dict]:
    """Split text into chunks. Returns list of dicts with position, text, start/end chars."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = []
    current_len = 0
    position = 0
    cursor = 0

    def flush():
        nonlocal position, current, current_len, cursor
        if not current:
            return
        ctext = "\n\n".join(current)
        start = cursor
        end = start + len(ctext)
        chunks.append({"position": position, "text": ctext, "start_char": start, "end_char": end})
        position += 1
        cursor = end + 2  # account for split separator
        current = []
        current_len = 0

    for p in paragraphs:
        plen = len(p)
        if current_len + plen + (2 if current else 0) > max_chars:
            flush()
        current.append(p)
        current_len += plen + (2 if current else 0)

    if current:
        flush()

    return chunks


def parse_document(raw_text: str, source_url: Optional[str] = None) -> Dict:
    """Parse raw_text into structured document data.

    Returns a dict with keys: title, text, source_url, metadata, chunks.
    """
    title = extract_title(raw_text)
    chunks = chunk_text(raw_text)
    metadata = {
        "char_count": len(raw_text),
        "word_count": len(raw_text.split()),
        "source_url": source_url,
    }

    # Placeholder: entity extraction (companies, bills, dates) will go here in future.

    return {
        "title": title,
        "text": raw_text,
        "source_url": source_url,
        "metadata": metadata,
        "chunks": chunks,
    }
