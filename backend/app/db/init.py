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
from app.models.government_event import GovernmentEvent  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.tender import Tender  # noqa: F401
from app.models.portfolio import Portfolio, PortfolioPosition, Watchlist, InvestmentSimulation, OpportunityScoreHistory  # noqa: F401
from app.models.prediction import PredictionRecord, CalibrationRun, FactorPerformance  # noqa: F401
from app.models.processing import ProcessingJob  # noqa: F401
from app.models.alert import AlertSubscription, NotificationHistory  # noqa: F401
from app.models.historical_snapshot import HistoricalSnapshot  # noqa: F401
from app.models.demo_mode import DemoMode  # noqa: F401


def init_db() -> None:
    """Create database tables for all registered models.

    Also perform lightweight migrations for known schema drift in development
    environments: when the evidence table exists but is missing recently added
    nullable columns, add them so the application can operate without a full
    migration system.
    """
    Base.metadata.create_all(bind=engine)

    # Lightweight runtime migration: add missing nullable columns to evidence
    # when the database was created from an older schema. This keeps the
    # fix minimal and limited to the evidence table only.
    try:
        from sqlalchemy import text

        with engine.begin() as conn:
            # Only supported for SQLite; for other DBs rely on proper migrations
            if engine.dialect.name == "sqlite":
                # --- existing evidence table compatibility ---
                res = conn.execute(text("PRAGMA table_info(evidence);"))
                existing_cols = [row[1] for row in res.fetchall()]
                statements = []
                if "government_level" not in existing_cols:
                    statements.append("ALTER TABLE evidence ADD COLUMN government_level VARCHAR(64);")
                if "language" not in existing_cols:
                    statements.append("ALTER TABLE evidence ADD COLUMN language VARCHAR(16);")
                if "publication_date" not in existing_cols:
                    statements.append("ALTER TABLE evidence ADD COLUMN publication_date DATETIME;")
                if "last_verified" not in existing_cols:
                    statements.append("ALTER TABLE evidence ADD COLUMN last_verified DATETIME;")
                if "verification_status" not in existing_cols:
                    statements.append(
                        "ALTER TABLE evidence ADD COLUMN verification_status VARCHAR(32) NOT NULL DEFAULT 'unverified';"
                    )

                for s in statements:
                    conn.execute(text(s))

                conn.execute(
                    text(
                        "CREATE INDEX IF NOT EXISTS ix_evidence_verification_status "
                        "ON evidence (verification_status);"
                    )
                )

                # --- ensure composite indexes exist on entity_relationship ---
                # This prevents severe performance regressions when listing
                # neighbors in the graph service. Create the indexes if they do
                # not already exist (SQLite PRAGMA index_list returns index info).
                try:
                    idx_res = conn.execute(text("PRAGMA index_list('entity_relationship');"))
                    existing_idx = [row[1] for row in idx_res.fetchall()]
                except Exception:
                    existing_idx = []

                idx_statements = []
                if 'ix_entity_relationship_source' not in existing_idx:
                    idx_statements.append(
                        "CREATE INDEX IF NOT EXISTS ix_entity_relationship_source ON entity_relationship (source_entity_type, source_entity_id);"
                    )
                if 'ix_entity_relationship_target' not in existing_idx:
                    idx_statements.append(
                        "CREATE INDEX IF NOT EXISTS ix_entity_relationship_target ON entity_relationship (target_entity_type, target_entity_id);"
                    )

                for s in idx_statements:
                    conn.execute(text(s))
    except Exception:
        # Keep init_db best-effort; do not raise on migration failure here to
        # avoid preventing the application from starting in other environments.
        pass
