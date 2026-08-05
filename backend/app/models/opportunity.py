from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OpportunityScore(Base, TimestampMixin):
    __tablename__ = "opportunity_score"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[str] = mapped_column(String(128), ForeignKey("company.id"), nullable=False, index=True)
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommendation: Mapped[str] = mapped_column(String(64), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    company = relationship("Company")
    breakdowns: Mapped[list["ScoreBreakdown"]] = relationship(
        "ScoreBreakdown", back_populates="opportunity", cascade="all, delete-orphan"
    )


class ScoreBreakdown(Base, TimestampMixin):
    __tablename__ = "score_breakdown"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    opportunity_score_id: Mapped[int] = mapped_column(ForeignKey("opportunity_score.id"), nullable=False, index=True)
    factor: Mapped[str] = mapped_column(String(128), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)

    opportunity = relationship("OpportunityScore", back_populates="breakdowns")
