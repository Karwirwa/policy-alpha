import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class PortfolioPosition(Base, TimestampMixin):
    __tablename__ = "portfolio_position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(128), ForeignKey("company.id"), nullable=False, index=True)
    allocation_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    portfolio = relationship("Portfolio")
    company = relationship("Company")


class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    company_id: Mapped[str] = mapped_column(String(128), ForeignKey("company.id"), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    company = relationship("Company")


class InvestmentSimulation(Base, TimestampMixin):
    __tablename__ = "investment_simulation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    company_id: Mapped[str] = mapped_column(String(128), ForeignKey("company.id"), nullable=False, index=True)
    buy_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    buy_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    shares: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    profit_loss: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    percent_return: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")

    company = relationship("Company")


class OpportunityScoreHistory(Base):
    __tablename__ = "opportunity_score_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[str] = mapped_column(String(128), ForeignKey("company.id"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(64), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    company = relationship("Company")
