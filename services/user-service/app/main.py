from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.events.publisher import publisher



app = FastAPI(title="User Service", version="1.0.0")
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    publisher.publish("service.started", {"service": settings.service_name})


@app.get("/")
def index() -> dict:
    return {"name": settings.service_name, "message": "user service online"}


@app.get("/metrics")
def metrics() -> str:
    return "# metrics placeholder\n"
