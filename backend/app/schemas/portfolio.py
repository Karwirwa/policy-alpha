from datetime import datetime
from pydantic import BaseModel


class PortfolioCreateRequest(BaseModel):
    name: str
    description: str | None = None


class PortfolioResponse(BaseModel):
    uuid: str
    name: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class AddCompanyRequest(BaseModel):
    company_id: str
    allocation_percent: float = 0.0
    notes: str | None = None


class PortfolioSummaryResponse(BaseModel):
    portfolio_uuid: str
    name: str
    total_companies: int
    average_opportunity_score: float
    average_return: float
    highest_performing: float | None
    worst_performing: float | None
    current_recommendations: dict

    class Config:
        from_attributes = True
