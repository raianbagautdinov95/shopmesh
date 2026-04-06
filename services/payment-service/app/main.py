from fastapi import FastAPI

from app.api.v1.router import api_router
from app.models import Payment

app = FastAPI(title="Payment Service", version="1.0.0")
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    pass


@app.get("/")
def index() -> dict[str, str]:
    return {"service": "payment-service", "status": "ok"}
