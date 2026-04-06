from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import get_current_user_payload
from app.api.v1._proxy import proxy_request
from app.core.config import settings

router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.api_route("", methods=["GET", "DELETE"])
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def cart_proxy(path: str = "", request: Request = None, current_user: dict = Depends(get_current_user_payload)) -> Response:
    upstream_path = request.url.path
    extra_headers = {
        "X-User-Email": current_user["email"],
        "X-User-Role": current_user.get("role", "user") or "user",
    }
    return await proxy_request(request, settings.cart_service_url, upstream_path, extra_headers=extra_headers)
