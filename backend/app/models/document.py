import uuid

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "document"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), nullable=False, default=lambda: str(uuid.uuid4()), unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(256), nullable=False)
    connector_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="document")
