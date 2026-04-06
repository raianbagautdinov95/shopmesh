from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import InventoryItem  # noqa: F401


app = FastAPI(
    title="Inventory Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.on_event("startup")
def on_startup() -> None:


    db = SessionLocal()
    try:
        existing = db.execute(select(InventoryItem)).scalars().first()
        if existing is None:
            db.add_all(
                [
                    InventoryItem(
                        product_id=1,
                        product_name="ShopMesh Desk Lamp",
                        sku="SKU-LAMP-001",
                        warehouse_code="WH-MAIN",
                        available_quantity=25,
                        reserved_quantity=0,
                        reorder_threshold=5,
                        is_active=True,
                    ),
                    InventoryItem(
                        product_id=2,
                        product_name="ShopMesh Mechanical Keyboard",
                        sku="SKU-KEYBOARD-001",
                        warehouse_code="WH-MAIN",
                        available_quantity=18,
                        reserved_quantity=0,
                        reorder_threshold=4,
                        is_active=True,
                    ),
                    InventoryItem(
                        product_id=3,
                        product_name="ShopMesh Wireless Mouse",
                        sku="SKU-MOUSE-001",
                        warehouse_code="WH-MAIN",
                        available_quantity=40,
                        reserved_quantity=0,
                        reorder_threshold=8,
                        is_active=True,
                    ),
                    InventoryItem(
                        product_id=4,
                        product_name="ShopMesh USB-C Dock",
                        sku="SKU-DOCK-001",
                        warehouse_code="WH-SECONDARY",
                        available_quantity=12,
                        reserved_quantity=0,
                        reorder_threshold=3,
                        is_active=True,
                    ),
                    InventoryItem(
                        product_id=5,
                        product_name="ShopMesh Monitor Stand",
                        sku="SKU-STAND-001",
                        warehouse_code="WH-SECONDARY",
                        available_quantity=16,
                        reserved_quantity=0,
                        reorder_threshold=4,
                        is_active=True,
                    ),
                ]
            )
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "inventory-service", "status": "ok"}


app.include_router(api_router, prefix=settings.api_v1_prefix)

Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")