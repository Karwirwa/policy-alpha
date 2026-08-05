import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PredictionRecord(Base, TimestampMixin):
    __tablename__ = "prediction_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    company_id: Mapped[str] = mapped_column(String(128), ForeignKey("company.id"), nullable=False, index=True)
    recommendation: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    prediction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_return: Mapped[float | None] = mapped_column(Float, nullable=True)
    prediction_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    company = relationship("Company")


class CalibrationRun(Base, TimestampMixin):
    __tablename__ = "calibration_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    run_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    companies_analyzed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommendations_generated: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class FactorPerformance(Base, TimestampMixin):
    __tablename__ = "factor_performance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    factor_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    weight_used: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    average_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommended_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    samples: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
