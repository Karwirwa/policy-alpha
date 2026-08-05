from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.connectors.models import GovernmentDocument


@dataclass
class ConnectorMetadata:
    extracted_keywords: list[str]
    normalized_keywords: list[str]
    detected_entities: list[str]
    provider: str
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Base interface for country connector implementations."""

    country_code: str
    connector_name: str

    def __init__(self, country_code: str, connector_name: str) -> None:
        self.country_code = country_code
        self.connector_name = connector_name

    @abstractmethod
    def discover(self) -> list[GovernmentDocument]:
        """Identify available government documents."""
        raise NotImplementedError

    @abstractmethod
    def download(self, document: GovernmentDocument) -> GovernmentDocument:
        """Retrieve raw document contents for a discovered document."""
        raise NotImplementedError

    @abstractmethod
    def parse(self, document: GovernmentDocument) -> GovernmentDocument:
        """Extract raw structured information from downloaded document contents."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, document: GovernmentDocument) -> GovernmentDocument:
        """Convert parsed information into the platform's canonical document format."""
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Return the connector health report without performing external requests."""
        raise NotImplementedError
