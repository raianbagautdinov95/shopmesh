from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


class TokenDecodeError(ValueError):
    pass


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise TokenDecodeError("Invalid token") from exc

    if payload.get("type") != "access":
        raise TokenDecodeError("Invalid token type")

    return payload