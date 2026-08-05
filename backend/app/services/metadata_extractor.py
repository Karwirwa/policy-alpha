import re

from app.services.resolvers.base_resolver import EntityMatch


class DocumentMetadata:
    extracted_keywords: list[str]
    normalized_keywords: list[str]
    detected_entities: list[str]

    def __init__(
        self,
        extracted_keywords: list[str],
        normalized_keywords: list[str],
        detected_entities: list[str],
    ) -> None:
        self.extracted_keywords = extracted_keywords
        self.normalized_keywords = normalized_keywords
        self.detected_entities = detected_entities


class MetadataExtractor:
    """Extract normalized metadata from document text."""

    KEYWORDS = [
        "cement",
        "roads",
        "procurement",
        "budget",
        "project",
        "tender",
        "contract",
        "infrastructure",
        "investment",
        "ministry",
    ]

    @classmethod
    def tokenize(cls, raw_text: str) -> list[str]:
        return re.findall(r"\w+", raw_text)

    @classmethod
    def normalize_token(cls, token: str) -> str:
        return token.strip().lower()

    @classmethod
    def _normalize_keywords(cls, keywords: list[str]) -> list[str]:
        return sorted({cls.normalize_token(keyword) for keyword in keywords})

    @classmethod
    def _unique_preserve_order(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                unique.append(value)
        return unique

    def extract(
        self,
        raw_text: str,
        entity_matches: dict[str, EntityMatch] | None = None,
    ) -> DocumentMetadata:
        tokens = self.tokenize(raw_text)
        extracted_keywords: list[str] = []
        normalized_keywords: list[str] = []

        keyword_set = {keyword.lower() for keyword in self.KEYWORDS}
        for token in tokens:
            normalized = self.normalize_token(token)
            if normalized in keyword_set:
                extracted_keywords.append(token)
                normalized_keywords.append(normalized)

        extracted_keywords = self._unique_preserve_order(extracted_keywords)
        normalized_keywords = self._unique_preserve_order(normalized_keywords)
        detected_entities = self.detect_entities(entity_matches or {})

        return DocumentMetadata(
            extracted_keywords=extracted_keywords,
            normalized_keywords=normalized_keywords,
            detected_entities=detected_entities,
        )

    def detect_entities(self, entity_matches: dict[str, EntityMatch]) -> list[str]:
        detected: list[str] = []
        for entity_type, match in entity_matches.items():
            if not match.entity_id:
                continue
            name = match.canonical_name or match.entity_id
            detected.append(f"{entity_type}:{name}")
        return detected
