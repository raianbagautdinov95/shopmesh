from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_identity, get_db
from app.repositories.cart import CartRepository
from app.schemas.cart import CartItemCreateRequest, CartItemUpdateRequest, CartResponse
from app.schemas.common import HealthResponse
from app.services.cart import CartService

api_router = APIRouter(prefix="/api/v1", tags=["cart"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="cart-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="cart-service", status="ok")


@api_router.get("/cart", response_model=CartResponse)
def get_cart(
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(CartRepository(db))
    return service.get_cart(identity["email"])


@api_router.post("/cart/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: CartItemCreateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(CartRepository(db))
    return service.add_item(identity["email"], payload)


@api_router.patch("/cart/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(CartRepository(db))
    try:
        return service.update_item(identity["email"], item_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@api_router.delete("/cart/items/{item_id}", response_model=CartResponse)
def remove_cart_item(
    item_id: int,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(CartRepository(db))
    try:
        return service.remove_item(identity["email"], item_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@api_router.delete("/cart", response_model=CartResponse)
def clear_cart(
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> CartResponse:
    service = CartService(CartRepository(db))
    return service.clear_cart(identity["email"])
