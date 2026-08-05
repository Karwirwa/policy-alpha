from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceDocument:
    document_id: str
    country_id: str
    raw_text: str
    source_reference: str
    connector_name: str | None = None
    title: str | None = None
    page_number: int | None = None
    section: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    document_id: str
    country_id: str
    raw_text: str
    source_reference: str
    connector_name: str | None
    title: str
    summary: str
    page_number: int | None = None
    section: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentParser:
    """Extract structured attributes from a raw government document."""

    @staticmethod
    def extract_title(raw_text: str) -> str:
        for line in raw_text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:512]
        return "Untitled Evidence"

    @staticmethod
    def extract_summary(raw_text: str) -> str:
        cleaned = " ".join(raw_text.split())
        if not cleaned:
            return ""

        sentence_end = ". "
        sentences = cleaned.split(sentence_end)
        if len(sentences) <= 1:
            return cleaned[:512]

        summary = sentence_end.join(sentences[:2]).strip()
        return summary[:512]

    def parse(self, document: EvidenceDocument) -> ParsedDocument:
        title = document.title or self.extract_title(document.raw_text)
        summary = self.extract_summary(document.raw_text)
        return ParsedDocument(
            document_id=document.document_id,
            country_id=document.country_id,
            raw_text=document.raw_text,
            source_reference=document.source_reference,
            connector_name=document.connector_name,
            title=title,
            summary=summary,
            page_number=document.page_number,
            section=document.section,
            metadata=document.metadata,
        )
