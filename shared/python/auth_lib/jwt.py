import os
from datetime import datetime, timedelta, timezone

import jwt

def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60")))).timestamp()),
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET", "change-me"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))
