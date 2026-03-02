import io
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

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


def test_upload_inventory_image_returns_public_path():
    img = io.BytesIO()
    img.write(b"RIFF\x18\x00\x00\x00WEBPVP8 \x0c\x00\x00\x000000000000")
    img.seek(0)
    files = {"file": ("jack.webp", img, "image/webp")}
    response = client.post("/api/v1/uploads/images?destination=inventario", files=files)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["destination"] == "inventario"
    assert data["public_path"].startswith("/images/INVENTARIO/")
    assert data["filename"] == "jack.webp"
    Path("public/images/INVENTARIO/jack.webp").unlink(missing_ok=True)


def test_upload_blocked_extension():
    f = io.BytesIO(b"not an image")
    files = {"file": ("bad.txt", f, "text/plain")}
    response = client.post("/api/v1/uploads/images", files=files)
    assert response.status_code == 400
