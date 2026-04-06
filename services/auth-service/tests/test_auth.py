from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def exists(self, key: str) -> int:
        return int(key in self.store)

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value

    def delete(self, *keys: str) -> None:
        for key in keys:
            self.store.pop(key, None)

    def scan_iter(self, match: str):
        prefix = match.rstrip("*")
        for key in list(self.store.keys()):
            if key.startswith(prefix):
                yield key


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db(monkeypatch) -> Generator[None, None, None]:
    from app.repositories import auth as auth_repository_module

    fake_redis = FakeRedis()
    monkeypatch.setattr(auth_repository_module, "redis_client", fake_redis)




    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()



@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_register_login_me_refresh_logout_flow(client: TestClient):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "password123",
            "full_name": "Test User",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "user@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["token_type"] == "bearer"

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    rotated_tokens = refresh_response.json()
    assert rotated_tokens["refresh_token"] != tokens["refresh_token"]

    old_refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert old_refresh_response.status_code == 401

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
    )
    assert logout_response.status_code == 200

    revoked_me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
    )
    assert revoked_me_response.status_code == 401


def test_admin_only_requires_admin_role(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "Regular User",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user2@example.com", "password": "password123"},
    )
    tokens = login_response.json()

    admin_response = client.get(
        "/api/v1/auth/admin-only",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert admin_response.status_code == 403
