from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_login_rate_limit():
    url = "/api/v1/auth/login"
    payload = {"email": "noone@example.com", "password": "wrongpw"}
    # slowapi uses request.client; TestClient sets client host automatically. Keep headers minimal.
    headers = {}

    # make several requests to trigger rate limit (limit is 5/minute)
    status_codes = []
    for i in range(8):
        r = client.post(url, json=payload, headers=headers)
        status_codes.append(r.status_code)

    # After the limit is reached, at least one 429 should appear
    assert 429 in status_codes
