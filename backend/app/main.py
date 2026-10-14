import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from fastapi import FastAPI

from app.core.config import get_settings
from app.api import kenya_opportunities
from app.api.evidence import router as evidence_router
from app.api.graph import router as graph_router
from app.api.opportunity import router as opportunity_router
from app.api.health import router as health_router
from app.api.portfolio import router as portfolio_router
from app.api.watchlist import router as watchlist_router
from app.api.simulation import router as simulation_router
from app.api.calibration import router as calibration_router
from app.db.database import SessionLocal
from app.db.init import init_db
from app.services.demo_seed import seed_kenya_demo

logger = logging.getLogger(__name__)

app = FastAPI(title="Policy Alpha API", version="0.1.0")

# Minimal CORS configuration for local frontend development. Allow only the
# frontend development origins to keep the change scoped and safe.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(kenya_opportunities.router)
app.include_router(evidence_router)
app.include_router(graph_router)
app.include_router(opportunity_router)
app.include_router(portfolio_router)
app.include_router(watchlist_router)
app.include_router(simulation_router)
app.include_router(calibration_router)
app.include_router(__import__('app.api.crawler', fromlist=['router']).router)
app.include_router(__import__('app.api.pipeline', fromlist=['router']).router)
app.include_router(__import__('app.api.stats', fromlist=['router']).router)
app.include_router(__import__('app.api.country', fromlist=['router']).router)
app.include_router(__import__('app.api.countries', fromlist=['router']).router)
app.include_router(__import__('app.api.executive', fromlist=['router']).router)
app.include_router(__import__('app.api.alerts', fromlist=['router']).router)
app.include_router(__import__('app.api.portfolio_overview', fromlist=['router']).router)
app.include_router(__import__('app.api.crawler_metrics', fromlist=['router']).router)
app.include_router(__import__('app.api.history', fromlist=['router']).router)
app.include_router(__import__('app.api.demo', fromlist=['router']).router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    settings = get_settings()
    if not settings.demo_seed_enabled:
        logger.info("Demo seed skipped (DEMO_SEED_ENABLED=false)")
        return

    try:
        with SessionLocal() as session:
            inserted = seed_kenya_demo(session)
    except Exception:
        logger.exception("Demo seed failed")
        raise

    logger.info("Demo seed complete: %s records", inserted)
