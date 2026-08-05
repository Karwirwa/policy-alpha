import logging
from typing import Any

from app.connectors.base_connector import BaseConnector, ConnectorMetadata
from app.connectors.models import GovernmentDocument


class GovernmentConnector(BaseConnector):
    """Shared base class for government country connectors."""

    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRY_COUNT = 3
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_CONNECTOR_VERSION = "0.1.0"

    def __init__(
        self,
        country_code: str,
        connector_name: str,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRY_COUNT,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        connector_version: str = DEFAULT_CONNECTOR_VERSION,
    ) -> None:
        super().__init__(country_code=country_code, connector_name=connector_name)
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.connector_version = connector_version
        self.logger = logging.getLogger(self.__class__.__name__)
        self.http_client = self._initialize_http_client()

    def _initialize_http_client(self) -> dict[str, Any]:
        self.logger.debug(
            "Initializing HTTP client for %s with timeout=%s, retries=%s",
            self.connector_name,
            self.timeout,
            self.retries,
        )
        # Placeholder HTTP client configuration.
        return {
            "timeout": self.timeout,
            "retries": self.retries,
            "retry_delay": self.retry_delay,
        }

    def _log_request(self, url: str) -> None:
        self.logger.info("Connector %s requesting URL: %s", self.connector_name, url)

    def _log_response(self, url: str, status: str) -> None:
        self.logger.info(
            "Connector %s received response for URL %s: %s",
            self.connector_name,
            url,
            status,
        )

    def _download_helper(self, document: GovernmentDocument, raw_text: str) -> GovernmentDocument:
        self.logger.debug(
            "Downloading document %s using helper for connector %s",
            document.document_id,
            self.connector_name,
        )
        document.raw_content = raw_text
        return document

    def download(self, document: GovernmentDocument) -> GovernmentDocument:
        return self._download_helper(
            document,
            document.raw_content or "",
        )

    def _normalize_document(self, document: GovernmentDocument) -> GovernmentDocument:
        parsed_metadata = document.metadata.get("parsed_metadata")
        if isinstance(parsed_metadata, ConnectorMetadata):
            normalized_metadata = self._normalize_metadata(parsed_metadata)
            document.metadata["normalized_metadata"] = normalized_metadata
        else:
            document.metadata["normalized_metadata"] = ConnectorMetadata(
                extracted_keywords=[],
                normalized_keywords=[],
                detected_entities=[],
                provider=self.connector_name,
                raw_metadata={"source_url": document.source_url},
            )
        return document

    def normalize(self, document: GovernmentDocument) -> GovernmentDocument:
        self.logger.debug(
            "Normalizing document %s for connector %s",
            document.document_id,
            self.connector_name,
        )
        document.metadata["normalized_document"] = True
        document.metadata["connector_name"] = self.connector_name
        document.metadata["country_code"] = self.country_code
        return self._normalize_document(document)

    def _normalize_metadata(self, metadata: ConnectorMetadata) -> ConnectorMetadata:
        normalized_keywords = []
        seen_keywords: set[str] = set()
        for keyword in metadata.normalized_keywords:
            normalized = keyword.strip().lower()
            if normalized and normalized not in seen_keywords:
                seen_keywords.add(normalized)
                normalized_keywords.append(normalized)

        detected_entities = []
        seen_entities: set[str] = set()
        for entity in metadata.detected_entities:
            normalized = entity.strip()
            if normalized and normalized not in seen_entities:
                seen_entities.add(normalized)
                detected_entities.append(normalized)

        return ConnectorMetadata(
            extracted_keywords=list(dict.fromkeys(metadata.extracted_keywords)),
            normalized_keywords=normalized_keywords,
            detected_entities=detected_entities,
            provider=metadata.provider,
            raw_metadata=metadata.raw_metadata,
        )

    def health(self) -> dict[str, Any]:
        return {
            "connector_name": self.connector_name,
            "supported_country": self.country_code,
            "connector_version": self.connector_version,
            "status": "READY",
            "last_successful_discovery": "never",
            "last_successful_download": "never",
            "capabilities": [
                "discover",
                "download",
                "parse",
                "normalize",
                "health",
            ],
        }

    def health_status(self) -> dict[str, Any]:
        return self.health()
