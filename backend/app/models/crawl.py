import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CrawlRun(Base, TimestampMixin):
    __tablename__ = "crawl_run"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    documents_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
