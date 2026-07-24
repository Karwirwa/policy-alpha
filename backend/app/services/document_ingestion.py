"""Document ingestion service for Milestone 2.

Responsibilities:
- Receive parsed document data (from document_parser)
- Persist Document and DocumentChunk records
- Link documents to an existing GovernmentSource when provided

This service intentionally does NOT use AI, embeddings, or external APIs.
"""
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models.entities import Document, DocumentChunk, GovernmentSource


class DocumentIngestionService:
    """Simple ingestion service that persists parsed document information."""

    def __init__(self, db: Session):
        self.db = db

    def ingest(self, parsed: Dict, government_source_id: Optional[str] = None) -> Document:
        """Persist document and its chunks.

        parsed: output of document_parser.parse_document
        government_source_id: optional ID to link the document to an existing source
        """
        # Verify government source exists if provided
        gs = None
        if government_source_id:
            gs = self.db.get(GovernmentSource, government_source_id)
            if gs is None:
                raise ValueError("government_source_id not found")

        doc = Document(
            title=parsed.get("title"),
            text=parsed.get("text", ""),
            source_url=parsed.get("source_url"),
            government_source_id=government_source_id,
        )
        self.db.add(doc)
        self.db.flush()

        # Persist chunks
        for c in parsed.get("chunks", []):
            chunk = DocumentChunk(
                document_id=doc.id,
                position=c.get("position", 0),
                text=c.get("text", ""),
                start_char=c.get("start_char"),
                end_char=c.get("end_char"),
            )
            self.db.add(chunk)

        self.db.commit()
        self.db.refresh(doc)
        return doc
