from app.models.base import Base, TimestampMixin
# Import milestone-2 domain entities so they are registered with SQLAlchemy's
# declarative base at import time. Alembic uses Base.metadata for autogeneration
# of migrations, so models must be imported here.
from app.models import entities  # noqa: F401

__all__ = ["Base", "TimestampMixin"]
