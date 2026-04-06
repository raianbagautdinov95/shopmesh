import os
from pathlib import Path

TEST_DB = Path("./test_cart.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["JWT_SECRET"] = "test-secret"

from jose import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.main import app




def _headers() -> dict[str, str]:
    token = jwt.encode(
        {"sub": "cart-user@example.com", "role": "user", "type": "access", "iss": settings.jwt_issuer},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


def test_cart_add_update_remove_flow() -> None:
    response = client.get("/api/v1/cart", headers=_headers())
    assert response.status_code == 200
    assert response.json()["items"] == []

    response = client.post(
        "/api/v1/cart/items",
        headers=_headers(),
        json={
            "product_id": 1,
            "product_name": "Mechanical Keyboard",
            "quantity": 2,
            "unit_price": "99.99",
            "currency": "usd",
            "sku": "KB-001",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["items_count"] == 2
    item_id = body["items"][0]["id"]

    response = client.patch(
        f"/api/v1/cart/items/{item_id}",
        headers=_headers(),
        json={"quantity": 3},
    )
    assert response.status_code == 200
    assert response.json()["items_count"] == 3

    response = client.delete(f"/api/v1/cart/items/{item_id}", headers=_headers())
    assert response.status_code == 200
    assert response.json()["items"] == []
