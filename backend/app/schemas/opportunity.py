from datetime import datetime

from pydantic import BaseModel


class BreakdownItem(BaseModel):
    factor: str
    weight: float
    score: float
    explanation: str


class OpportunityResponse(BaseModel):
    company_id: str
    total_score: float
    confidence: float
    recommendation: str
    explanation: str
    breakdown: list[BreakdownItem]
    supporting_evidence_ids: list[int] = []

    class Config:
        from_attributes = True


class TopOpportunityItem(BaseModel):
    company_id: str
    total_score: float
    recommendation: str
    created_at: datetime

    class Config:
        from_attributes = True
