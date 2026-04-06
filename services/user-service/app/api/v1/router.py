from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_identity, get_db, require_admin
from app.schemas.common import HealthResponse
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserRoleUpdateRequest,
    UserStatusUpdateRequest,
)
from app.services.user import UserService

api_router = APIRouter(prefix="/api/v1", tags=["user"])


@api_router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(service="user-service", status="ok")


@api_router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    return HealthResponse(service="user-service", status="ok")


@api_router.get("/users/me", response_model=UserProfileResponse)
def get_current_user_profile(
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)
    return service.get_or_create_current_user(email=identity["email"], role=identity["role"])


@api_router.patch("/users/me", response_model=UserProfileResponse)
def update_current_user_profile(
    payload: UserProfileUpdateRequest,
    identity: dict[str, str] = Depends(get_current_identity),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)
    profile = service.get_or_create_current_user(email=identity["email"], role=identity["role"])
    return service.update_current_user(profile, payload)


@api_router.get("/users", response_model=list[UserProfileResponse])
def list_users(
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UserProfileResponse]:
    service = UserService(db)
    return service.list_users()


@api_router.get("/users/{user_id}", response_model=UserProfileResponse)
def get_user_by_id(
    user_id: int,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)
    profile = service.get_user_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return profile


@api_router.patch("/users/{user_id}/role", response_model=UserProfileResponse)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)
    profile = service.get_user_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return service.update_role(profile, payload.role)


@api_router.patch("/users/{user_id}/status", response_model=UserProfileResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdateRequest,
    _: dict[str, str] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserService(db)
    profile = service.get_user_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return service.set_active(profile, payload.is_active)
