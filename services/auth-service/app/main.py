from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.api.v1.auth import router as auth_router
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):

    yield


app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)


@app.get("/")
def index() -> dict[str, str]:
    return {"service": "auth-service", "status": "ok"}


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"service": "auth-service", "status": "healthy"}


@app.get("/api/v1/ready")
def ready() -> dict[str, str]:
    return {"service": "auth-service", "status": "ready"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)