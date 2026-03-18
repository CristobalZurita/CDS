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


def test_build_legacy_local_path_normalizes_relative_contract():
    assert (
        cloudinary_service.build_legacy_local_path("INVENTARIO/NE555_AS.webp")
        == "/images/INVENTARIO/NE555_AS.webp"
    )
    assert (
        cloudinary_service.build_legacy_local_path("/instrumentos/KORG_M1.webp")
        == "/images/instrumentos/KORG_M1.webp"
    )


def test_extract_filename_from_local_path_supports_expected_prefix():
    assert (
        cloudinary_service.extract_filename_from_local_path(
            "/images/INVENTARIO/AUDIO_JACK_CHASIS_MONO_6_3.webp",
            expected_relative_prefix="INVENTARIO",
        )
        == "AUDIO_JACK_CHASIS_MONO_6_3.webp"
    )
    assert (
        cloudinary_service.extract_filename_from_local_path("https://cdn.example.com/path/file.webp")
        == "file.webp"
    )
