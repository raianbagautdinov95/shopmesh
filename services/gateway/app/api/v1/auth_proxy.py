from fastapi import APIRouter, Request, Response

from app.api.v1._proxy import proxy_request
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def auth_proxy(path: str, request: Request) -> Response:
    upstream_path = f"/api/v1/auth/{path}" if path else "/api/v1/auth"
    return await proxy_request(request, settings.auth_service_url, upstream_path)
