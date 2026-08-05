from fastapi import FastAPI

from fastapi import FastAPI

from app.api.evidence import router as evidence_router
from app.api.graph import router as graph_router
from app.api.health import router as health_router
from app.db.init import init_db

app = FastAPI(title="Policy Alpha API", version="0.1.0")
app.include_router(health_router)
app.include_router(evidence_router)
app.include_router(graph_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
