from fastapi import APIRouter

from app.api.v1.auth_proxy import router as auth_proxy_router
from app.api.v1.catalog_proxy import router as catalog_proxy_router
from app.api.v1.cart_proxy import router as cart_proxy_router
from app.api.v1.gateway_status import router as gateway_status_router
from app.api.v1.inventory_proxy import router as inventory_proxy_router
from app.api.v1.notification_proxy import router as notification_proxy_router
from app.api.v1.order_proxy import router as order_proxy_router
from app.api.v1.payment_proxy import router as payment_proxy_router
from app.api.v1.user_proxy import router as user_proxy_router
from app.schemas.health import HealthResponse

api_router = APIRouter()
api_router.include_router(gateway_status_router)
api_router.include_router(auth_proxy_router)
api_router.include_router(user_proxy_router)
api_router.include_router(catalog_proxy_router)
api_router.include_router(cart_proxy_router)
api_router.include_router(order_proxy_router)
api_router.include_router(payment_proxy_router)
api_router.include_router(inventory_proxy_router)
api_router.include_router(notification_proxy_router)


@api_router.get("/health", response_model=HealthResponse, tags=["gateway"])
def health() -> HealthResponse:
    return HealthResponse(service="gateway", status="ok")


@api_router.get("/ready", response_model=HealthResponse, tags=["gateway"])
def ready() -> HealthResponse:
    return HealthResponse(service="gateway", status="ok")