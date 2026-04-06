from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_identity, get_db
from app.repositories.order import OrderRepository
from app.schemas.common import HealthResponse
from app.schemas.order import OrderCreateRequest, OrderResponse, OrderStatusUpdateRequest
from app.services.order import OrderService

api_router = APIRouter(prefix="/api/v1", tags=["order"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="order-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="order-service", status="ok")


@api_router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> list[OrderResponse]:
    service = OrderService(OrderRepository(db))
    return service.list_orders(identity["email"], identity["role"])


@api_router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> OrderResponse:
    service = OrderService(OrderRepository(db))
    return service.create_order(identity["email"], payload)


@api_router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> OrderResponse:
    service = OrderService(OrderRepository(db))
    try:
        return service.get_order(identity["email"], identity["role"], order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@api_router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> OrderResponse:
    service = OrderService(OrderRepository(db))
    try:
        return service.update_status(identity["role"], order_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@api_router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> OrderResponse:
    service = OrderService(OrderRepository(db))
    try:
        return service.cancel_order(identity["email"], identity["role"], order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
