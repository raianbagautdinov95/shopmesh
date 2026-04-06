from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_identity, get_db
from app.repositories.payment import PaymentRepository
from app.schemas.common import HealthResponse
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentIntentResponse,
    PaymentListResponse,
    PaymentResponse,
    PaymentStatusUpdateRequest,
)
from app.services.payment import PaymentService

api_router = APIRouter(prefix="/api/v1", tags=["payment"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="payment-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="payment-service", status="ok")


@api_router.get("/payments", response_model=PaymentListResponse)
def list_payments(
    order_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> PaymentListResponse:
    service = PaymentService(PaymentRepository(db))
    return service.list_payments(identity["email"], identity["role"], order_id=order_id, limit=limit, offset=offset)


@api_router.post("/payments/intents", response_model=PaymentIntentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_intent(
    payload: PaymentCreateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> PaymentIntentResponse:
    service = PaymentService(PaymentRepository(db))
    return service.create_payment_intent(identity["email"], payload)


@api_router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    service = PaymentService(PaymentRepository(db))
    try:
        return service.get_payment(identity["email"], identity["role"], payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@api_router.patch("/payments/{payment_id}/status", response_model=PaymentResponse)
def update_payment_status(
    payment_id: int,
    payload: PaymentStatusUpdateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> PaymentResponse:
    service = PaymentService(PaymentRepository(db))
    try:
        return service.update_status(identity["role"], payment_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
