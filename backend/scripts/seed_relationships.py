from app.db.init import init_db
from app.db.database import SessionLocal
from app.repositories.evidence_repository import EvidenceRepository
from app.services.document_parser import EvidenceDocument
from app.services.evidence_builder import EvidenceIngestionService
from app.repositories.relationship_repository import RelationshipRepository


def main() -> None:
    init_db()
    document = EvidenceDocument(
        document_id="doc-graph-001",
        country_id="country_kenya",
        raw_text=(
            "The Ministry of Roads awarded a Government Tender to Bamburi Cement PLC for the Road Expansion Project. "
            "The Infrastructure Budget will fund the award and the public procurement notice references the contract award."
        ),
        source_reference="kenya.gov/documents/roads/2026/expansion",
        connector_name="kenya_gazette",
        title="Ministry of Roads Government Tender Announcement",
        page_number=1,
        section="Tender Summary",
    )

    with SessionLocal() as session:
        repository = EvidenceRepository(session)
        ingestion_service = EvidenceIngestionService(repository)
        evidence = ingestion_service.ingest(document)
        print(f"Created evidence id={evidence.id} document_hash={evidence.document_hash}")

        relationship_repo = RelationshipRepository(session)
        relationships = relationship_repo.find_by_entity("company", evidence.company_id or "")
        print("Created relationships:")
        for rel in relationships:
            print(
                f"{rel.source_entity_type}:{rel.source_entity_id} "
                f"{rel.relationship_type.value} {rel.target_entity_type}:{rel.target_entity_id} "
                f"(evidence_id={rel.evidence_id})"
            )


if __name__ == "__main__":
    main()
