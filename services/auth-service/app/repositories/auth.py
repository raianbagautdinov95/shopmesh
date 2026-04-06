from app.db.redis_client import redis_client


class AuthRepository:
    def is_token_blacklisted(self, token: str) -> bool:
        return redis_client.exists(f"blacklist:{token}") > 0

    def blacklist_token(self, token: str, ttl_seconds: int) -> None:
        if ttl_seconds > 0:
            redis_client.setex(f"blacklist:{token}", ttl_seconds, "1")

    def store_refresh_token(self, user_email: str, refresh_token: str, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        redis_client.setex(f"refresh:{user_email}:{refresh_token}", ttl_seconds, "1")

    def is_refresh_token_active(self, user_email: str, refresh_token: str) -> bool:
        return redis_client.exists(f"refresh:{user_email}:{refresh_token}") > 0

    def revoke_refresh_token(self, user_email: str, refresh_token: str) -> None:
        redis_client.delete(f"refresh:{user_email}:{refresh_token}")

    def revoke_all_refresh_tokens(self, user_email: str) -> None:
        keys = list(redis_client.scan_iter(match=f"refresh:{user_email}:*"))
        if keys:
            redis_client.delete(*keys)
