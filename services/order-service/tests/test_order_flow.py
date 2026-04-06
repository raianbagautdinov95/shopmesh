from fastapi.testclient import TestClient

from app.main import app


def test_order_create_and_list() -> None:
    client = TestClient(app)
    headers = {"X-User-Email": "buyer@example.com", "X-User-Role": "user"}

    created = client.post(
        "/api/v1/orders",
        headers=headers,
        json={
            "items": [
                {
                    "product_id": 1,
                    "product_name": "Mechanical Keyboard",
                    "quantity": 2,
                    "unit_price": "99.90",
                    "currency": "USD",
                }
            ],
            "currency": "USD",
        },
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload["status"] == "pending"
    assert payload["items_count"] == 2

    listed = client.get("/api/v1/orders", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1


def test_non_owner_cannot_read_order() -> None:
    client = TestClient(app)
    owner_headers = {"X-User-Email": "owner@example.com", "X-User-Role": "user"}
    other_headers = {"X-User-Email": "other@example.com", "X-User-Role": "user"}

    created = client.post(
        "/api/v1/orders",
        headers=owner_headers,
        json={
            "items": [
                {
                    "product_id": 2,
                    "product_name": "Wireless Mouse",
                    "quantity": 1,
                    "unit_price": "49.00",
                    "currency": "USD",
                }
            ],
            "currency": "USD",
        },
    )
    order_id = created.json()["id"]

    forbidden = client.get(f"/api/v1/orders/{order_id}", headers=other_headers)
    assert forbidden.status_code == 403
