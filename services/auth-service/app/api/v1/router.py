from fastapi import APIRouter

from app.schemas.common import HealthResponse
from app.schemas.resource import AuthResource
from app.services.auth import sample_auth_payload

api_router = APIRouter(prefix="/api/v1", tags=["auth"])

@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="auth", status="ok")

@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="auth", status="ok")

@api_router.get("/auth/sample", response_model=AuthResource)
def get_sample() -> AuthResource:
    return AuthResource(**sample_auth_payload())
