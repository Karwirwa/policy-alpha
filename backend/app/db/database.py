from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_WORKTREE_ROOT = _BACKEND_DIR.parent
_DB_FILE = _WORKTREE_ROOT / "policy_alpha.db"
DATABASE_URL = (
    settings.database_url
    if "database_url" in settings.model_fields_set
    else f"sqlite:///{_DB_FILE.as_posix()}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args=settings.sqlite_connect_args if settings.is_sqlite else None,
    echo=settings.database_echo,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """Yield a database session for FastAPI dependency injection.

    This helper exists so the application can safely open and close sessions
    around each request without duplicating session-management logic.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
