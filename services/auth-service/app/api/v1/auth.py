from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh(payload)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    return service.logout(token)


@router.post("/logout-all", response_model=LogoutResponse)
def logout_all(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.logout_all(current_user.email)


@router.post("/change-password", response_model=LogoutResponse)
def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    return service.change_password(current_user.email, payload)


@router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/admin-only")
def admin_only(current_user=Depends(require_role("admin"))):
    return {
        "message": "Welcome admin",
        "user": current_user.email,
        "role": current_user.role,
    }
