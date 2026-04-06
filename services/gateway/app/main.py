from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.api.router import api_router
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(title="ShopMesh Gateway", version="1.0.0")
app.add_middleware(RequestIDMiddleware)
app.include_router(api_router)


@app.get("/")
def index() -> dict[str, str]:
    return {"service": "gateway", "status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

