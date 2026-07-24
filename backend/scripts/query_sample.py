"""Retrieve and print information about the ingested sample document.

This script:
- Finds the most recently created document
- Prints Title, Government Source, Publication Date
- Prints document chunks (position and a short preview)
- Prints detected companies and bills (via RetrievalService)
- Calls AnalysisService and prints the mocked analysis response

No AI is used; AnalysisService is the existing placeholder.
"""
from textwrap import shorten

from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.entities import Document
from app.services.retrieval import RetrievalService
from app.services.analysis import AnalysisService


def main():
    db = SessionLocal()
    try:
        # Find the most recently created document
        stmt = select(Document).order_by(Document.created_at.desc()).limit(1)
        doc = db.execute(stmt).scalars().first()
        if not doc:
            print("No document found. Run ingest_sample.py first.")
            return

        retrieval = RetrievalService(db)
        analysis = AnalysisService()

        print(f"Title: {doc.title}")
        source_name = doc.source.name if doc.source else 'Unknown'
        print(f"Government Source: {source_name}")
        print(f"Publication Date: {doc.published_at}")

        chunks = retrieval.get_document_chunks(doc.id)
        print("\nDocument Chunks:")
        for c in chunks:
            preview = shorten(c.text.replace('\n',' '), width=200, placeholder='...')
            print(f"- position={c.position} start={c.start_char} end={c.end_char} preview={preview}")

        companies = retrieval.companies_mentioned_in_document(doc.id)
        print("\nDetected Companies:")
        if companies:
            for c in companies:
                print(f"- {c.name}")
        else:
            print("- None detected")

        bills = retrieval.bills_mentioned_in_document(doc.id)
        print("\nDetected Bills:")
        if bills:
            for b in bills:
                print(f"- {b.title} (identifier={b.identifier})")
        else:
            print("- None detected")

        # Call the AnalysisService placeholder and print its mocked response exactly
        analysis_result = analysis.analyze_document(doc.text)
        print("\nMocked Analysis Result:")
        print(analysis_result)

    finally:
        db.close()


if __name__ == "__main__":
    main()
