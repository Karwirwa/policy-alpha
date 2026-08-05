from datetime import datetime
from pydantic import BaseModel


class BuyRequest(BaseModel):
    company_id: str
    buy_date: datetime
    buy_price: float
    shares: int


class UpdatePriceRequest(BaseModel):
    uuid: str
    current_price: float


class SimulationResponse(BaseModel):
    uuid: str
    company_id: str
    buy_date: datetime
    buy_price: float
    current_price: float
    shares: int
    profit_loss: float
    percent_return: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
