from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _base_payload(subject: str, token_type: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "nbf": now,
        "iss": settings.jwt_issuer,
        "jti": str(uuid4()),
    }


def create_access_token(subject: str, role: str) -> str:
    payload = _base_payload(subject=subject, token_type="access")
    payload.update(
        {
            "role": role,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.jwt_expire_minutes),
        }
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    payload = _base_payload(subject=subject, token_type="refresh")
    payload.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(days=settings.jwt_refresh_expire_days),
        }
    )
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def get_token_ttl_seconds(payload: dict[str, Any]) -> int:
    exp = payload.get("exp")
    if not exp:
        return 0

    now_ts = int(datetime.now(timezone.utc).timestamp())
    ttl = int(exp) - now_ts
    return max(ttl, 0)
