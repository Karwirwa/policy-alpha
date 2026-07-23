from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
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
