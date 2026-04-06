from fastapi import FastAPI

from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.models import Notification  # noqa: F401

app = FastAPI(title="Notification Service", version="1.0.0")
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    pass


@app.get("/")
def index() -> dict[str, str]:
    return {"service": "notification-service", "status": "ok"}