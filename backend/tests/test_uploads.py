import io
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_upload_valid_image(tmp_path):
    img = io.BytesIO()
    # create a small PNG via bytes (header only)
    img.write(b"\x89PNG\r\n\x1a\n")
    img.seek(0)
    files = {"file": ("test.png", img, "image/png")}
    response = client.post("/api/v1/uploads/images", files=files)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "filename" in data


def test_upload_blocked_extension():
    f = io.BytesIO(b"not an image")
    files = {"file": ("bad.txt", f, "text/plain")}
    response = client.post("/api/v1/uploads/images", files=files)
    assert response.status_code == 400
