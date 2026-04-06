import asyncio

import httpx
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["gateway"])


@router.get("/api/status")
async def aggregate_status() -> dict:
    services = {
        "auth-service": settings.auth_service_url,
        "user-service": settings.user_service_url,
        "catalog-service": settings.catalog_service_url,
        "cart-service": settings.cart_service_url,
        "order-service": settings.order_service_url,
        "payment-service": settings.payment_service_url,
        "inventory-service": settings.inventory_service_url,
        "notification-service": settings.notification_service_url,
    }

    async with httpx.AsyncClient(timeout=2.5) as client:
        async def fetch(name: str, base_url: str):
            try:
                response = await client.get(f"{base_url}/api/v1/health")
                data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"status": response.text}
                return name, {"up": response.status_code < 500, "status_code": response.status_code, "data": data}
            except Exception as exc:
                return name, {"up": False, "error": str(exc)}

        results = dict(await asyncio.gather(*(fetch(name, url) for name, url in services.items())))

    overall = "ok" if all(item.get("up") for item in results.values()) else "degraded"
    return {"gateway": "ok", "overall": overall, "services": results}
