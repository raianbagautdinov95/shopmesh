from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
headers = {"X-User-Email": "user@example.com", "X-User-Role": "user"}
admin_headers = {"X-User-Email": "admin@example.com", "X-User-Role": "admin"}


def test_notification_flow() -> None:
    create_response = client.post(
        "/api/v1/notifications",
        json={
            "recipient": "user@example.com",
            "channel": "email",
            "subject": "Order confirmed",
            "message": "Your order is confirmed",
            "related_order_id": 1,
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    notification_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/notifications/{notification_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["recipient"] == "user@example.com"

    mark_read_response = client.post(f"/api/v1/notifications/{notification_id}/read", headers=headers)
    assert mark_read_response.status_code == 200
    assert mark_read_response.json()["is_read"] is True

    update_response = client.patch(
        f"/api/v1/notifications/{notification_id}/status",
        json={"status": "failed", "failure_reason": "provider timeout"},
        headers=admin_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "failed"
