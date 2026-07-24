"""AI Service interface for Milestone 3.

This module provides an interface that accepts a previously-built context and
produces a grounded analysis. It does NOT call any LLM here; instead it
constructs a deterministic, evidence-citing response using only the supplied
context. This keeps the contract stable for future LLM integration.
"""
from typing import Dict, Any


def analyze_company_with_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a grounded analysis using only the provided context.

    Rules enforced:
    - Only use information supplied in context.
    - If key information is missing, indicate so.
    - Always include evidence entries that reference items from context.
    """
    company = context.get("company")
    if not company:
        return {"error": "missing_company_in_context"}

    projects = context.get("projects", [])
    budgets = context.get("budgets", [])
    evidence = context.get("evidence", [])

    if not projects and not budgets:
        analysis_text = (
            f"No project or budget information found for company {company.get('name')}."
            " Cannot provide analysis without evidence."
        )
        return {
            "company": company.get("name"),
            "analysis": analysis_text,
            "evidence": [],
            "sources": [],
        }

    # Build a simple deterministic analysis summary using only context fields
    lines = []
    lines.append(f"Company {company.get('name')} has {len(projects)} project(s) referenced in the supplied context.")

    total_project_amount = sum([p.get("amount") or 0 for p in projects])
    lines.append(f"Total value across listed projects: {total_project_amount} (currency as recorded in budgets).")

    program_names = list({b.get("program") for b in budgets if b.get("program")})
    if program_names:
        lines.append(f"Related programme(s): {', '.join(program_names)}.")

    analysis_text = " ".join(lines)

    # Prepare sources: list budget programs and years
    sources = [
        {"program": b.get("program"), "year": b.get("year"), "amount": b.get("amount")} for b in budgets
    ]

    # Return the analysis and the evidence as provided (do not invent)
    return {
        "company": company.get("name"),
        "analysis": analysis_text,
        "evidence": evidence,
        "sources": sources,
    }
