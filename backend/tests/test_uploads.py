import io
from pathlib import Path


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_upload_valid_image(test_client, customer_token):
    img = io.BytesIO()
    # create a small PNG via bytes (header only)
    img.write(b"\x89PNG\r\n\x1a\n")
    img.seek(0)
    files = {"file": ("test.png", img, "image/png")}
    response = test_client.post("/api/v1/uploads/images", files=files, headers=_auth_headers(customer_token))
    assert response.status_code in (200, 201)
    data = response.json()
    assert "filename" in data
    Path("uploads/images/test.png").unlink(missing_ok=True)


def test_upload_inventory_image_returns_public_path(test_client, admin_token):
    img = io.BytesIO()
    img.write(b"RIFF\x18\x00\x00\x00WEBPVP8 \x0c\x00\x00\x000000000000")
    img.seek(0)
    files = {"file": ("jack.webp", img, "image/webp")}
    response = test_client.post(
        "/api/v1/uploads/images?destination=inventario",
        files=files,
        headers=_auth_headers(admin_token),
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["destination"] == "inventario"
    assert data["public_path"].startswith("/images/INVENTARIO/")
    assert data["filename"] == "jack.webp"
    Path("public/images/INVENTARIO/jack.webp").unlink(missing_ok=True)


def test_upload_blocked_extension(test_client, customer_token):
    f = io.BytesIO(b"not an image")
    files = {"file": ("bad.txt", f, "text/plain")}
    response = test_client.post("/api/v1/uploads/images", files=files, headers=_auth_headers(customer_token))
    assert response.status_code == 400


def test_upload_requires_authentication(test_client):
    img = io.BytesIO()
    img.write(b"\x89PNG\r\n\x1a\n")
    img.seek(0)
    files = {"file": ("noauth.png", img, "image/png")}

    response = test_client.post("/api/v1/uploads/images", files=files)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_inventory_upload_requires_admin_role(test_client, customer_token):
    img = io.BytesIO()
    img.write(b"RIFF\x18\x00\x00\x00WEBPVP8 \x0c\x00\x00\x000000000000")
    img.seek(0)
    files = {"file": ("not-admin.webp", img, "image/webp")}

    response = test_client.post(
        "/api/v1/uploads/images?destination=inventario",
        files=files,
        headers=_auth_headers(customer_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Acceso denegado. Solo administradores."
