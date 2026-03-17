import os

from app.services import cloudinary_service


def test_resolve_cloudinary_config_accepts_explicit_env(monkeypatch):
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "demo-cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "demo-key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "demo-secret")
    monkeypatch.delenv("CLOUDINARY_URL", raising=False)

    config = cloudinary_service.resolve_cloudinary_config()

    assert config == {
        "cloud_name": "demo-cloud",
        "api_key": "demo-key",          # pragma: allowlist secret
        "api_secret": "demo-secret",    # pragma: allowlist secret
    }


def test_resolve_cloudinary_config_accepts_cloudinary_url(monkeypatch):
    monkeypatch.delenv("CLOUDINARY_CLOUD_NAME", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_KEY", raising=False)
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)
    monkeypatch.setenv("CLOUDINARY_URL", "cloudinary://demo-key:demo-secret@demo-cloud")  # pragma: allowlist secret

    config = cloudinary_service.resolve_cloudinary_config()

    assert config == {
        "cloud_name": "demo-cloud",
        "api_key": "demo-key",
        "api_secret": "demo-secret",
    }


def test_local_path_to_public_id_preserves_folder_contract():
    assert (
        cloudinary_service.local_path_to_public_id("/images/logo/NUEVO_cirujano.webp")
        == "logo/NUEVO_cirujano"
    )
    assert (
        cloudinary_service.local_path_to_public_id("/images/INVENTARIO/NE555_AS.webp")
        == "INVENTARIO/NE555_AS"
    )
