import re
from datetime import datetime, timezone
from typing import List

from app.models.government_event import GovernmentEvent, EventType
from app.models.evidence import Evidence


class EventExtractionService:
    """Deterministic rule-based extraction of events from Evidence records."""

    RULES = [
        (r"\bapproved\b|\ballocated\b", EventType.BUDGET_APPROVED),
        (r"\bincrease\b|\brevised upward\b|\bincreased\b", EventType.BUDGET_INCREASED),
        (r"\breduc\b|\breduce\b|\breduced\b", EventType.BUDGET_REDUCED),
        (r"\bpublish\b|\bpublished\b", EventType.TENDER_PUBLISHED),
        (r"\baward\b|\bawarded\b", EventType.TENDER_AWARDED),
        (r"\bprocure\b|\bprocurement started\b", EventType.PROCUREMENT_STARTED),
        (r"\bprocurement completed\b|\bprocurement\s+completed\b", EventType.PROCUREMENT_COMPLETED),
        (r"\bstart(ed)?\b|\bcommenc(ed|e)\b", EventType.PROJECT_STARTED),
        (r"\bdelay\b|\bdelayed\b", EventType.PROJECT_DELAYED),
        (r"\bcompleted\b|\bcomplete\b", EventType.PROJECT_COMPLETED),
        (r"\bsign(ed)?\b|\bsigned\b", EventType.CONTRACT_SIGNED),
        (r"\bextend(ed)?\b|\bextended\b", EventType.CONTRACT_EXTENDED),
        (r"\bblacklist(ed)?\b|\bblacklisted\b", EventType.COMPANY_BLACKLISTED),
        (r"\bpolicy\b|\bpolicies\b|\bintroduced\b", EventType.POLICY_CREATED),
        (r"\bamend(ed)?\b|\bamended\b", EventType.POLICY_UPDATED),
        (r"\brepeal(ed)?\b|\brepealed\b", EventType.POLICY_REPEALED),
        (r"\bregulation\b|\bregulations\b", EventType.REGULATION_CREATED),
        (r"\bmention(ed)?\b|\bmentioned\b", EventType.COMPANY_MENTIONED),
    ]

    def __init__(self) -> None:
        # precompile regexes
        self.compiled = [(re.compile(pat, re.IGNORECASE), ev) for pat, ev in self.RULES]

    def extract_from_evidence(self, evidence: Evidence) -> List[GovernmentEvent]:
        text = " ".join([evidence.title or "", evidence.summary or "", evidence.raw_text or ""]).lower()
        events: List[GovernmentEvent] = []
        for regex, ev_type in self.compiled:
            if regex.search(text):
                # Create event
                title = f"{ev_type.value.replace('_', ' ').title()} detected"
                description = f"Detected '{ev_type.value}' from evidence id {evidence.id}"
                # try to infer event date from evidence extracted_at
                event_date = evidence.extracted_at
                detected_date = datetime.now(timezone.utc)
                confidence = evidence.evidence_strength
                ge = GovernmentEvent(
                    event_type=ev_type,
                    title=title,
                    description=description,
                    event_date=event_date,
                    detected_date=detected_date,
                    confidence=confidence,
                    source_document_id=evidence.document_id,
                    evidence_id=evidence.id,
                    country_id=evidence.country_id,
                )
                events.append(ge)
        return events
