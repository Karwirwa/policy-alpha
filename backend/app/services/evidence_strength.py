from statistics import mean
from datetime import datetime, timezone

from app.core.countries import normalize_country_id
from app.services.entity_resolution import EntityMatch


class EvidenceStrengthCalculator:
    """Compute deterministic evidence strength for extracted evidence.

    Enhancements: considers publication_date freshness and country modifier for cross-country normalization.
    """

    def calculate(
        self,
        entity_matches: list[EntityMatch],
        raw_text: str,
        source_reference: str,
        supporting_references: list[str] | None = None,
        publication_date: datetime | None = None,
        country_code: str | None = None,
    ) -> float:
        entity_scores = [match.match_score for match in entity_matches if match.entity_id]
        average_entity_quality = mean(entity_scores) if entity_scores else 0.0
        completeness_score = min(1.0, len(raw_text.strip()) / 1200)
        source_quality = 1.0 if source_reference.strip() else 0.5
        supporting_factor = 1.0

        if supporting_references:
            supporting_factor = min(1.2, 1.0 + len(supporting_references) * 0.05)

        # Freshness factor: newer publications are stronger.
        freshness = 1.0
        if publication_date:
            try:
                days = (datetime.now(timezone.utc) - publication_date).days
                freshness = max(0.0, 1.0 - (days / 365.0))
            except Exception:
                freshness = 0.5

        # Country modifier: conservative default 0.6
        country_mods = {
            "KENYA": 0.7,
            "UNITED_STATES": 0.9,
            "UNITED_KINGDOM": 0.85,
            "CANADA": 0.88,
            "KE": 0.7,
            "US": 0.9,
            "GB": 0.85,
            "CA": 0.88,
            "KEN": 0.7,
            "USA": 0.9,
            "GBR": 0.85,
            "CAN": 0.88,
        }
        normalized_country_id = normalize_country_id(country_code) if country_code else None
        country_modifier = 0.6
        if normalized_country_id:
            country_modifier = country_mods.get(normalized_country_id.upper(), 0.6)
        else:
            country_modifier = country_mods.get((country_code or "").upper(), 0.6)

        base_score = (
            average_entity_quality * 0.4
            + completeness_score * 0.3
            + source_quality * 0.1
            + (len(entity_scores) / 3 if entity_scores else 0.0) * 0.2
        )

        score = base_score * supporting_factor * freshness * country_modifier
        return round(min(max(score, 0.0), 1.0), 3)
