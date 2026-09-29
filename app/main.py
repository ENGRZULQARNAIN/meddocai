from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.example import router as example_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.is_local else None,  # hide Swagger outside local
    redoc_url=None,
)

Instrumentator().instrument(app).expose(app)

app.include_router(example_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health() -> dict:
    # Deliberately not rate-limited: load balancer / orchestrator health
    # probes hit this constantly, and it does no work worth protecting.
    return {"status": "ok", "environment": settings.environment}
