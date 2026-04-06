from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.events.publisher import publisher
from app.services.catalog import CatalogService

app = FastAPI(title="Catalog Service", version="1.0.0")
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    publisher.publish("service.started", {"service": settings.service_name})
    db = SessionLocal()
    try:
        CatalogService(db).seed_defaults()
    finally:
        db.close()


@app.get("/")
def index() -> dict:
    return {"name": settings.service_name, "message": "catalog service online"}


@app.get("/metrics")
def metrics() -> str:
    return "# metrics placeholder\n"