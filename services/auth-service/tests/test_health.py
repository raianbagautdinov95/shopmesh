from fastapi.testclient import TestClient

from app.main import app

def test_auth_health() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["service"] == "auth"
