import uuid

from app.models.media import MediaAsset, MediaBinding


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _seed_media_binding(db):
    slug = uuid.uuid4().hex[:8]
    asset = MediaAsset(
        public_id=f"tests/media-{slug}",
        secure_url=f"https://res.cloudinary.com/demo/image/upload/tests/media-{slug}.webp",
        folder="tests",
        original_filename=f"media-{slug}.webp",
        format="webp",
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    binding = MediaBinding(
        slot_key=f"tests.slot.{slug}",
        asset_id=asset.id,
        label="Test slot",
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return asset, binding


def test_media_assets_require_media_read_permission(test_client, db, admin_token, customer_token, monkeypatch):
    monkeypatch.setenv("ENFORCE_PERMISSIONS_IN_TESTS", "1")
    _seed_media_binding(db)

    customer = test_client.get("/api/v1/media/assets", headers=_auth_headers(customer_token))
    assert customer.status_code == 403, customer.text

    admin = test_client.get("/api/v1/media/assets", headers=_auth_headers(admin_token))
    assert admin.status_code == 200, admin.text
    payload = admin.json()
    assert isinstance(payload, list)
    assert payload


def test_media_bindings_split_public_and_admin_access(test_client, db, admin_token, customer_token, monkeypatch):
    monkeypatch.setenv("ENFORCE_PERMISSIONS_IN_TESTS", "1")
    _, binding = _seed_media_binding(db)

    customer = test_client.get("/api/v1/media/bindings", headers=_auth_headers(customer_token))
    assert customer.status_code == 403, customer.text

    public = test_client.get("/api/v1/media/public/bindings")
    assert public.status_code == 200, public.text
    public_payload = public.json()
    assert any(entry["slot_key"] == binding.slot_key for entry in public_payload)

    admin = test_client.get("/api/v1/media/bindings", headers=_auth_headers(admin_token))
    assert admin.status_code == 200, admin.text
    admin_payload = admin.json()
    assert any(entry["slot_key"] == binding.slot_key for entry in admin_payload)
