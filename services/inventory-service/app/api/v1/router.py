from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_identity, get_db, require_admin
from app.repositories.inventory import InventoryRepository
from app.schemas.common import HealthResponse
from app.schemas.inventory import (
    InventoryItemCreateRequest,
    InventoryItemResponse,
    InventoryItemUpdateRequest,
    InventoryListResponse,
    InventoryReleaseRequest,
    InventoryReservationRequest,
)
from app.services.inventory import InventoryService

api_router = APIRouter(tags=["inventory"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="inventory-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="inventory-service", status="ok")


@api_router.get("/inventory", response_model=InventoryListResponse)
def list_inventory(
    sku: str | None = Query(default=None),
    product_id: int | None = Query(default=None),
    active_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> InventoryListResponse:
    service = InventoryService(InventoryRepository(db))
    return service.list_items(sku=sku, product_id=product_id, active_only=active_only, limit=limit, offset=offset)


@api_router.get("/inventory/{inventory_id}", response_model=InventoryItemResponse)
def get_inventory_item(inventory_id: int, db: Session = Depends(get_db)) -> InventoryItemResponse:
    service = InventoryService(InventoryRepository(db))
    try:
        return service.get_item(inventory_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@api_router.get("/inventory/sku/{sku}", response_model=InventoryItemResponse)
def get_inventory_item_by_sku(sku: str, db: Session = Depends(get_db)) -> InventoryItemResponse:
    service = InventoryService(InventoryRepository(db))
    try:
        return service.get_item_by_sku(sku)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@api_router.post("/inventory", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryItemCreateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    service = InventoryService(InventoryRepository(db))
    try:
        return service.create_item(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@api_router.patch("/inventory/{inventory_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    inventory_id: int,
    payload: InventoryItemUpdateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    service = InventoryService(InventoryRepository(db))
    try:
        return service.update_item(inventory_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@api_router.post("/inventory/reservations", response_model=InventoryItemResponse)
def reserve_inventory(
    payload: InventoryReservationRequest,
    _: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    service = InventoryService(InventoryRepository(db))
    try:
        return service.reserve(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@api_router.post("/inventory/reservations/release", response_model=InventoryItemResponse)
def release_inventory(
    payload: InventoryReleaseRequest,
    _: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    service = InventoryService(InventoryRepository(db))
    try:
        return service.release(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

