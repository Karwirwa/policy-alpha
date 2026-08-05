from app.db.database import engine
from app.models.base import Base

# Import models to ensure they are registered with SQLAlchemy metadata.
from app.models.agency import Agency  # noqa: F401
from app.models.budget import Budget  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.country import Country  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.entity_relationship import EntityRelationship  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.tender import Tender  # noqa: F401


def init_db() -> None:
    """Create database tables for all registered models."""
    Base.metadata.create_all(bind=engine)
