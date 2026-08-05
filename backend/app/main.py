from fastapi import FastAPI

from fastapi import FastAPI

from fastapi import FastAPI

from app.api.evidence import router as evidence_router
from app.api.graph import router as graph_router
from app.api.opportunity import router as opportunity_router
from app.api.health import router as health_router
from app.api.portfolio import router as portfolio_router
from app.api.watchlist import router as watchlist_router
from app.api.simulation import router as simulation_router
from app.api.calibration import router as calibration_router
from app.db.init import init_db

app = FastAPI(title="Policy Alpha API", version="0.1.0")
app.include_router(health_router)
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
app.include_router(__import__('app.api.portfolio_overview', fromlist=['router']).router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
