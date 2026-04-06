from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_identity, get_db
from app.repositories.notification import NotificationRepository
from app.schemas.common import HealthResponse
from app.schemas.notification import (
    NotificationCreateRequest,
    NotificationListResponse,
    NotificationResponse,
    NotificationStatusUpdateRequest,
)
from app.services.notification import NotificationService

api_router = APIRouter(prefix="/api/v1", tags=["notification"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="notification-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="notification-service", status="ok")


@api_router.get("/notifications", response_model=NotificationListResponse)
def list_notifications(
    recipient: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> NotificationListResponse:
    service = NotificationService(NotificationRepository(db))
    return service.list_notifications(
        identity["email"], identity["role"], recipient=recipient, status=status_filter, limit=limit, offset=offset
    )


@api_router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    service = NotificationService(NotificationRepository(db))
    return service.create_notification(identity["email"], payload)


@api_router.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    service = NotificationService(NotificationRepository(db))
    try:
        return service.get_notification(identity["email"], identity["role"], notification_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@api_router.patch("/notifications/{notification_id}/status", response_model=NotificationResponse)
def update_notification_status(
    notification_id: int,
    payload: NotificationStatusUpdateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    service = NotificationService(NotificationRepository(db))
    try:
        return service.update_status(identity["role"], notification_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@api_router.post("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    service = NotificationService(NotificationRepository(db))
    try:
        return service.mark_read(identity["email"], identity["role"], notification_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
