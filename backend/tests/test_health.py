from fastapi.testclient import TestClient

def test_health_endpoint(app):
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert data.get("status") == "ok"
