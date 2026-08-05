from app.db.init import init_db
from app.db.database import SessionLocal
from app.repositories.evidence_repository import EvidenceRepository
from app.services.document_parser import EvidenceDocument
from app.services.evidence_builder import EvidenceIngestionService


def main() -> None:
    init_db()
    document = EvidenceDocument(
        document_id="doc-001",
        country_id="country_kenya",
        raw_text=(
            "Ministry of Roads has approved a procurement contract for the Tana River irrigation project. "
            "The document references Bamburi Cement PLC as a preferred supplier for concrete and infrastructure works. "
            "This budget report expects contract awards before the next quarter."
        ),
        source_reference="kenya.gov/documents/roads/2026",
        connector_name="kenya_gazette",
        title="Ministry of Roads Procurement Notice",
        page_number=1,
        section="Procurement Summary",
    )

    with SessionLocal() as session:
        repository = EvidenceRepository(session)
        ingest_service = EvidenceIngestionService(repository)
        evidence = ingest_service.ingest(document)
        print(f"Created evidence with id={evidence.id} and evidence_strength={evidence.evidence_strength}")


if __name__ == "__main__":
    main()
