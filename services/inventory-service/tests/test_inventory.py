from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_inventory_returns_seeded_items() -> None:
    response = client.get("/api/v1/inventory")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 1


def test_get_inventory_by_sku() -> None:
    response = client.get("/api/v1/inventory/sku/SM-HEADPHONES-01")
    assert response.status_code == 200
    assert response.json()["sku"] == "SM-HEADPHONES-01"
