from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    get_token_ttl_seconds,
    verify_password,
)
from app.repositories.auth import AuthRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.auth_repository = AuthRepository()

    def register(self, payload: RegisterRequest):
        existing_user = self.user_repository.get_by_email(payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user = self.user_repository.create(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=get_password_hash(payload.password),
            role="user",
        )
        return user

    def login(self, payload: LoginRequest) -> dict[str, str]:
        user = self.user_repository.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        return self._issue_token_pair(user.email, user.role)

    def refresh(self, payload: RefreshTokenRequest) -> dict[str, str]:
        token_data = self._decode_or_raise(payload.refresh_token, error_detail="Invalid or expired refresh token")

        if token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        email = token_data.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        if not self.auth_repository.is_refresh_token_active(email, payload.refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or rotated",
            )

        user = self.user_repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        self.auth_repository.revoke_refresh_token(email, payload.refresh_token)
        return self._issue_token_pair(user.email, user.role)

    def logout(self, token: str) -> dict[str, str]:
        payload = self._decode_or_raise(token, error_detail="Invalid or expired token")

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        ttl = get_token_ttl_seconds(payload)
        self.auth_repository.blacklist_token(token, ttl)
        return {"message": "Logged out successfully"}

    def logout_all(self, current_user_email: str) -> dict[str, str]:
        self.auth_repository.revoke_all_refresh_tokens(current_user_email)
        return {"message": "All sessions revoked successfully"}

    def change_password(self, current_user_email: str, payload: ChangePasswordRequest) -> dict[str, str]:
        user = self.user_repository.get_by_email(current_user_email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not verify_password(payload.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        if payload.current_password == payload.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password",
            )

        self.user_repository.update_password(user, get_password_hash(payload.new_password))
        self.auth_repository.revoke_all_refresh_tokens(current_user_email)
        return {"message": "Password changed successfully. Please log in again."}

    def _issue_token_pair(self, email: str, role: str) -> dict[str, str]:
        access_token = create_access_token(subject=email, role=role)
        refresh_token = create_refresh_token(subject=email)

        refresh_payload = decode_token(refresh_token)
        refresh_ttl = get_token_ttl_seconds(refresh_payload)
        self.auth_repository.store_refresh_token(email, refresh_token, refresh_ttl)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def _decode_or_raise(token: str, *, error_detail: str) -> dict:
        try:
            return decode_token(token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail,
            ) from exc
