from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.company import Company
from app.models.evidence import Evidence
from app.models.entity_relationship import EntityRelationship, RelationshipType
from app.models.opportunity import OpportunityScore, ScoreBreakdown
from app.repositories.relationship_repository import RelationshipRepository


class OpportunityScoringService:
    """Deterministic scoring engine for company opportunities based on evidence graph."""

    FACTOR_WEIGHTS = {
        "government_mentions": 20.0,
        "supporting_documents": 15.0,
        "average_evidence_confidence": 15.0,
        "procurement_stage": 20.0,
        "budget_presence": 15.0,
        "evidence_freshness": 10.0,
        "country_reliability": 5.0,
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.relationship_repo = RelationshipRepository(db)

    def score_company(self, company_identifier: str) -> Tuple[OpportunityScore, List[ScoreBreakdown]]:
        """Compute an OpportunityScore and breakdowns for a company name or id.

        company_identifier can be a canonical id (e.g., company_bamburi) or a human name.
        """
        # Resolve company id
        company = self._resolve_company(company_identifier)
        if not company:
            raise ValueError(f"Unknown company '{company_identifier}'")

        company_id = company.id

        # Gather evidence related to company
        evidence_list = self.db.query(Evidence).filter(Evidence.company_id == company_id).all()

        # Factor: government_mentions -> count of unique projects/agencies/tenders that mention the company
        mentions = len(evidence_list)
        government_mentions_score = self._scale_linear(mentions, max_value=10) * 100

        # Factor: supporting_documents -> number of distinct documents
        distinct_docs = len(set(e.document_id for e in evidence_list))
        supporting_documents_score = self._scale_linear(distinct_docs, max_value=10) * 100

        # Factor: average_evidence_confidence -> average of evidence_strength (0..1 assumed)
        avg_confidence = 0.0
        if evidence_list:
            avg_confidence = sum(e.evidence_strength for e in evidence_list) / len(evidence_list)
        average_evidence_confidence_score = self._clamp(avg_confidence * 100)

        # Factor: procurement_stage -> inspect relationships for AWARDED or presence of tender
        rels = self.relationship_repo.find_by_entity("company", company_id)
        has_awarded = any(r.relationship_type == RelationshipType.AWARDED for r in rels)
        has_tender = any(r.target_entity_type == "tender" or r.source_entity_type == "tender" for r in rels)
        if has_awarded:
            procurement_stage_score = 100.0
            procurement_expl = "Company awarded a government tender"
        elif has_tender:
            procurement_stage_score = 70.0
            procurement_expl = "Company referenced in a procurement/tender"
        else:
            procurement_stage_score = 30.0
            procurement_expl = "No procurement evidence found"

        # Factor: budget_presence -> check for budgets linked
        has_budget = any(r.target_entity_type == "budget" or r.source_entity_type == "budget" for r in rels)
        budget_presence_score = 100.0 if has_budget else 30.0

        # Factor: evidence_freshness -> days since most recent evidence (compute safely)
        freshness_score = 0.0
        if evidence_list:
            try:
                latest = max(e.extracted_at for e in evidence_list)
                days = (datetime.now(timezone.utc) - latest).days
                # Freshness: 365 days -> score 0, 0 days -> 100
                freshness_score = max(0.0, 1.0 - (days / 365.0)) * 100.0
            except Exception:
                # fallback when datetimes have mismatched tzinfo
                freshness_score = 0.0
        else:
            freshness_score = 0.0

        # Factor: country_reliability -> simple deterministic mapping
        country_modifier = self._country_reliability_modifier(company_id)
        country_reliability_score = country_modifier * 100.0

        # Build breakdowns
        breakdowns: List[ScoreBreakdown] = []
        breakdowns.append(self._make_breakdown("government_mentions", "Government Mentions", self.FACTOR_WEIGHTS["government_mentions"], government_mentions_score, f"{mentions} evidence mentions"))
        breakdowns.append(self._make_breakdown("supporting_documents", "Supporting Documents", self.FACTOR_WEIGHTS["supporting_documents"], supporting_documents_score, f"{distinct_docs} distinct documents"))
        breakdowns.append(self._make_breakdown("average_evidence_confidence", "Avg Evidence Confidence", self.FACTOR_WEIGHTS["average_evidence_confidence"], average_evidence_confidence_score, f"Average evidence strength {avg_confidence:.2f}"))
        breakdowns.append(self._make_breakdown("procurement_stage", "Procurement Stage", self.FACTOR_WEIGHTS["procurement_stage"], procurement_stage_score, procurement_expl))
        breakdowns.append(self._make_breakdown("budget_presence", "Budget Presence", self.FACTOR_WEIGHTS["budget_presence"], budget_presence_score, "Budget linked to evidence" if has_budget else "No budget links"))
        # compute human-friendly days since latest evidence safely
        latest_days_str = "N/A"
        if evidence_list:
            try:
                latest_dt = max(e.extracted_at for e in evidence_list)
                latest_days = (datetime.now(timezone.utc) - latest_dt).days
                latest_days_str = str(latest_days)
            except Exception:
                # Fallback if there's a timezone mismatch or other issue
                latest_days_str = "unknown"

        breakdowns.append(self._make_breakdown("evidence_freshness", "Evidence Freshness", self.FACTOR_WEIGHTS["evidence_freshness"], freshness_score, f"Most recent evidence { latest_days_str } days ago"))
        breakdowns.append(self._make_breakdown("country_reliability", "Country Reliability", self.FACTOR_WEIGHTS["country_reliability"], country_reliability_score, "Deterministic country reliability modifier"))

        # Weighted total
        total_weight = sum(self.FACTOR_WEIGHTS.values())
        weighted_sum = sum((b.score * (b.weight / total_weight)) for b in breakdowns)
        total_score = self._clamp(weighted_sum)

        # Confidence explained as normalized average evidence confidence scaled by presence of documents
        confidence = (avg_confidence * 0.8 + (min(1.0, distinct_docs / 10.0) * 0.2))

        recommendation = self._recommendation_from_score(total_score)

        explanation = self._build_explanation(company.name, breakdowns, total_score, recommendation)

        # Create OpportunityScore object (not persisted here)
        opp = OpportunityScore(
            company_id=company_id,
            total_score=total_score,
            confidence=confidence,
            recommendation=recommendation,
            explanation=explanation,
            created_at=datetime.now(timezone.utc),
        )

        return opp, breakdowns

    def _resolve_company(self, identifier: str) -> Company | None:
        # Try direct id lookup
        company = self.db.get(Company, identifier)
        if company:
            return company
        # Try name lookup (case-insensitive)
        return self.db.query(Company).filter(func.lower(Company.name) == identifier.strip().lower()).first()

    def _scale_linear(self, value: int, max_value: int = 10) -> float:
        # Scale value linearly to 0..1 using max_value as a cap
        return min(1.0, float(value) / float(max_value))

    def _clamp(self, v: float) -> float:
        return max(0.0, min(100.0, float(v)))

    def _country_reliability_modifier(self, company_id: str) -> float:
        # Deterministic mapping based on company evidence country if available
        # For simplicity use company-related evidence country majority
        evidence_countries = (
            self.db.query(Evidence.country_id)
            .filter(Evidence.company_id == company_id)
            .distinct()
            .all()
        )
        if not evidence_countries:
            return 0.5
        # take first country's id and map
        country_id = evidence_countries[0][0]
        from app.core.countries import normalize_country_id

        normalized = normalize_country_id(country_id)
        mapping = {"kenya": 0.7, "united_states": 0.9, "united_kingdom": 0.85}
        return mapping.get(normalized, 0.6)

    def _make_breakdown(self, key: str, factor: str, weight: float, score: float, explanation: str) -> ScoreBreakdown:
        b = ScoreBreakdown(factor=factor, weight=weight, score=self._clamp(score), explanation=explanation)
        return b

    def _recommendation_from_score(self, score: float) -> str:
        if score >= 90:
            return "Strong Buy"
        if score >= 75:
            return "High Opportunity"
        if score >= 60:
            return "Watch Closely"
        if score >= 40:
            return "Neutral"
        return "Low Opportunity"

    def _build_explanation(self, company_name: str, breakdowns: List[ScoreBreakdown], total_score: float, recommendation: str) -> str:
        lines = [f"{company_name}", "", f"Opportunity Score: {total_score:.0f}", "", "Reasoning"]
        for b in breakdowns:
            lines.append(f"• {b.factor}: score {b.score:.0f} (weight {b.weight}) — {b.explanation}")
        lines.append("")
        lines.append(f"Recommendation: {recommendation}")
        return "\n".join(lines)
