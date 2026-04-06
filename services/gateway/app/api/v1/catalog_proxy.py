from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.v1._proxy import proxy_request
from app.core.config import settings
from app.core.security import TokenDecodeError, decode_access_token

router = APIRouter(prefix="/api/v1", tags=["catalog"])
bearer = HTTPBearer(auto_error=False)


def optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict | None:
    if credentials is None:
        return None
    try:
        return decode_access_token(credentials.credentials)
    except TokenDecodeError:
        return None


@router.api_route("/categories", methods=["GET", "POST"])
@router.api_route("/categories/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@router.api_route("/products", methods=["GET", "POST"])
@router.api_route("/products/{path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
async def catalog_proxy(path: str = "", request: Request = None, user: dict | None = Depends(optional_user)) -> Response:
    upstream_path = request.url.path
    extra_headers = None
    if user and user.get("sub"):
        extra_headers = {
            "X-User-Email": user["sub"],
            "X-User-Role": user.get("role", "user") or "user",
        }
    return await proxy_request(request, settings.catalog_service_url, upstream_path, extra_headers=extra_headers)
