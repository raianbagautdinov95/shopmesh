from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_identity(
    authorization: str | None = Header(default=None),
    x_user_email: str | None = Header(default=None),
    x_user_role: str | None = Header(default="user"),
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, str]:
    if x_user_email:
        return {"email": x_user_email.lower(), "role": (x_user_role or "user").lower()}

    bearer_token = token
    if not bearer_token and authorization and authorization.lower().startswith("bearer "):
        bearer_token = authorization.split(" ", 1)[1]

    if not bearer_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        payload = decode_token(bearer_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return {"email": email.lower(), "role": (payload.get("role") or "user").lower()}


def require_admin(identity: dict[str, str] = Depends(get_current_identity)) -> dict[str, str]:
    if identity.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return identity
