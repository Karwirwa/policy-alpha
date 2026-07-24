"""Placeholder analysis service for Milestone 2.

This module provides the interface where AI integration will later occur.
For the milestone it returns mocked responses and includes TODO comments to
indicate where LLM calls will be integrated in future milestones.
"""
from typing import Dict, List


class AnalysisService:
    """Interface for document/company analysis.

    Methods return mocked outputs in Milestone 2 but keep the shape the
    future AI-backed implementation should follow.
    """

    def analyze_document(self, document_text: str) -> Dict:
        """Return a mocked analysis for the provided document text.

        TODO: replace mock with LLM call that returns structured findings with
        evidence pointers (document chunk ids and character offsets).
        """
        # Very small deterministic mock for now
        return {
            "summary": (document_text[:500] + "...") if len(document_text) > 500 else document_text,
            "key_topics": ["policy", "regulation"],
            "evidence": [],  # TODO: list of {chunk_id, start_char, end_char}
        }

    def summarize_document(self, document_text: str) -> str:
        """Return a short mocked summary string.

        TODO: integrate LLM summarization and citation of chunks.
        """
        if not document_text:
            return ""
        return document_text[:300] + ("..." if len(document_text) > 300 else "")

    def explain_company(self, company_name: str, context_texts: List[str]) -> Dict:
        """Return a mocked explanation about a company given context texts.

        TODO: call LLM to produce explanation with evidence and confidence score.
        """
        return {
            "company": company_name,
            "explanation": f"{company_name} is mentioned in government documents. (mocked)",
            "mentions_count": len(context_texts),
            "evidence": [],
        }
