from fastapi import FastAPI

from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.models import Order, OrderItem  # noqa: F401

app = FastAPI(title="Order Service", version="1.0.0")
app.include_router(api_router)


@app.get("/")
def index() -> dict[str, str]:
    return {"service": "order-service", "status": "ok"}

@app.on_event("startup")
def on_startup() -> None:
    pass
