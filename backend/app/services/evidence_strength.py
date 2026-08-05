from statistics import mean

from app.services.entity_resolution import EntityMatch


class EvidenceStrengthCalculator:
    """Compute deterministic evidence strength for extracted evidence."""

    def calculate(
        self,
        entity_matches: list[EntityMatch],
        raw_text: str,
        source_reference: str,
        supporting_references: list[str] | None = None,
    ) -> float:
        entity_scores = [match.match_score for match in entity_matches if match.entity_id]
        average_entity_quality = mean(entity_scores) if entity_scores else 0.0
        completeness_score = min(1.0, len(raw_text.strip()) / 1200)
        source_quality = 1.0 if source_reference.strip() else 0.5
        supporting_factor = 1.0

        if supporting_references:
            supporting_factor = min(1.2, 1.0 + len(supporting_references) * 0.05)

        score = (
            average_entity_quality * 0.4
            + completeness_score * 0.3
            + source_quality * 0.1
            + (len(entity_scores) / 3 if entity_scores else 0.0) * 0.2
        )
        score = score * supporting_factor
        return round(min(max(score, 0.0), 1.0), 3)
