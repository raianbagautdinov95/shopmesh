from fastapi.testclient import TestClient

from app.main import app


def test_create_and_get_payment_intent() -> None:
    client = TestClient(app)
    headers = {"X-User-Email": "buyer@example.com", "X-User-Role": "user"}

    create_response = client.post(
        "/api/v1/payments/intents",
        headers=headers,
        json={"order_id": 101, "amount": "149.99", "currency": "usd", "description": "Order 101 payment"},
    )
    assert create_response.status_code == 201, create_response.text
    payload = create_response.json()
    assert payload["status"] == "pending"
    assert payload["currency"] == "USD"
    assert payload["client_secret"].startswith("secret_")

    payment_id = payload["id"]
    get_response = client.get(f"/api/v1/payments/{payment_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["order_id"] == 101
