from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.analyze import router as analyze_router

app = FastAPI(title="Policy Alpha API", version="0.1.0")
app.include_router(health_router)
app.include_router(analyze_router)
