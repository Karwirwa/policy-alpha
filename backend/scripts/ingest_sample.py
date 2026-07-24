"""Ingest the sample government document into the Milestone 2 pipeline.

This script:
1. Ensures a Country exists.
2. Ensures a GovernmentSource exists.
3. Parses sample-data/sample_infrastructure_bill.txt using the deterministic parser.
4. Stores the document and its chunks via DocumentIngestionService.
5. Creates Company and Bill records and Mention links for the sample.
6. Prints status messages.

This script purposefully avoids any AI or external services.
"""
from datetime import datetime
from pathlib import Path
import re

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.entities import Country, GovernmentSource, Company, Bill, Mention, Document
from app.services.document_parser import parse_document
from app.services.document_ingestion import DocumentIngestionService


SAMPLE_PATH = Path(__file__).parents[1].parents[0] / "sample-data" / "sample_infrastructure_bill.txt"


def get_or_create_country(db, name: str, code: str | None = None) -> Country:
    stmt = select(Country).where(Country.name == name)
    r = db.execute(stmt).scalars().first()
    if r:
        return r, False
    c = Country(name=name, code=code)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c, True


def get_or_create_source(db, name: str, url: str | None, country_id: str) -> GovernmentSource:
    stmt = select(GovernmentSource).where(GovernmentSource.name == name)
    r = db.execute(stmt).scalars().first()
    if r:
        return r, False
    gs = GovernmentSource(name=name, url=url, country_id=country_id)
    db.add(gs)
    db.commit()
    db.refresh(gs)
    return gs, True


def extract_header_fields(text: str) -> dict:
    """Extract basic header fields from the sample file (title, publication date, ministry).

    This is a simple deterministic extractor tailored for the sample format.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = lines[0] if lines else None
    pub_date = None
    ministry = None

    for line in lines[1:5]:
        if line.lower().startswith("publication date:"):
            pub_date = line.split("Publication Date:", 1)[1].strip()
        if line.lower().startswith("ministry:"):
            ministry = line.split("Ministry:", 1)[1].strip()

    # Attempt to parse date
    parsed_date = None
    if pub_date:
        try:
            parsed_date = datetime.fromisoformat(pub_date)
        except Exception:
            parsed_date = None

    return {"title": title, "publication_date": parsed_date, "ministry": ministry}


def create_companies_and_bill(db, document: Document, text: str):
    # Very small heuristic: look for the Affected Companies section and extract dash-listed names
    companies = []
    m = re.search(r"Affected Companies:\s*(?:- .+\n)+", text, re.IGNORECASE)
    if m:
        block = m.group(0)
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("-"):
                name = line[1:].strip()
                if name:
                    companies.append(name)

    created_companies = []
    for name in companies:
        stmt = select(Company).where(Company.name == name)
        existing = db.execute(stmt).scalars().first()
        if existing:
            created_companies.append(existing)
        else:
            c = Company(name=name)
            db.add(c)
            db.commit()
            db.refresh(c)
            created_companies.append(c)
            # Create mention linking document to company
            mention = Mention(document_id=document.id, company_id=c.id, snippet=name)
            db.add(mention)
            db.commit()

    # Bill detection: search for Draft Bill ID or Draft Bill
    bill = None
    bm = re.search(r"Draft Bill ID:\s*(\S+)", text)
    if bm:
        identifier = bm.group(1).strip()
        # create bill record with title from header or identifier
        stmt = select(Bill).where(Bill.identifier == identifier)
        existing = db.execute(stmt).scalars().first()
        if existing:
            bill = existing
        else:
            title = f"Bill {identifier}"
            b = Bill(title=title, identifier=identifier)
            db.add(b)
            db.commit()
            db.refresh(b)
            bill = b
            mention = Mention(document_id=document.id, bill_id=b.id, snippet=identifier)
            db.add(mention)
            db.commit()

    return created_companies, bill


def main():
    if not SAMPLE_PATH.exists():
        print(f"Sample file not found: {SAMPLE_PATH}")
        return

    raw_text = SAMPLE_PATH.read_text(encoding="utf-8")
    parsed = parse_document(raw_text, source_url=None)
    headers = extract_header_fields(raw_text)

    db = SessionLocal()
    try:
        country, created = get_or_create_country(db, name="Testland", code="TL")
        print("Country created" if created else "Country found")

        source_name = "Test Government Publications"
        source_url = "https://gov.example"
        source, screated = get_or_create_source(db, name=source_name, url=source_url, country_id=country.id)
        print("Source created" if screated else "Source found")

        ingestion = DocumentIngestionService(db)
        doc = ingestion.ingest(parsed, government_source_id=source.id)

        # If we extracted a publication date from the header, persist it to the document
        if headers.get("publication_date"):
            doc.published_at = headers["publication_date"]
            db.add(doc)
            db.commit()
            db.refresh(doc)

        companies, bill = create_companies_and_bill(db, doc, raw_text)

        print("Document stored")
        chunks = db.execute(select(Document).where(Document.id == doc.id)).scalars().first().chunks
        print(f"Number of chunks: {len(chunks)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()