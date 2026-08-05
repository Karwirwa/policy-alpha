from app.connectors.government_connector import GovernmentConnector, ConnectorMetadata
from app.connectors.models import GovernmentDocument


class CanadaConnector(GovernmentConnector):
    """Placeholder connector for Canadian government document sources."""

    def __init__(self) -> None:
        super().__init__(country_code="CAN", connector_name="canada_parliament")

    def discover(self) -> list[GovernmentDocument]:
        return [
            GovernmentDocument(
                connector_name=self.connector_name,
                country_code=self.country_code,
                source_url="https://parliament.ca/documents/placeholder",
                document_id="canada_doc_001",
                title="Placeholder Canada Government Document",
                publication_date=None,
                document_type="government_notice",
                language="en",
            )
        ]

    def download(self, document: GovernmentDocument) -> GovernmentDocument:
        return self._download_helper(
            document,
            (
                "Placeholder raw text retrieved from the Canadian connector. "
                "This document would normally be downloaded from a national data source."
            ),
        )

    def parse(self, document: GovernmentDocument) -> GovernmentDocument:
        document.metadata["parsed_metadata"] = ConnectorMetadata(
            extracted_keywords=[],
            normalized_keywords=[],
            detected_entities=[],
            provider=self.connector_name,
            raw_metadata={
                "source_url": document.source_url,
                "text_length": len(document.raw_content or ""),
            },
        )
        return document

    def normalize(self, document: GovernmentDocument) -> GovernmentDocument:
        return super().normalize(document)
