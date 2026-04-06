from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_products_returns_seeded_items() -> None:
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 1


def test_get_product_by_slug() -> None:
    response = client.get("/api/v1/products/slug/shopmesh-wireless-headphones")
    assert response.status_code == 200
    assert response.json()["sku"] == "SM-HEADPHONES-01"
