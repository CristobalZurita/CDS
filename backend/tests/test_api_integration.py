import uuid
from pathlib import Path


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_category(db, *, slug: str):
    from app.models.category import Category

    category = Category(
        name=f"Categoria Integracion {slug}",
        description=f"Categoria de prueba {slug}",
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def test_login_with_valid_credentials_returns_tokens(api_client, disable_turnstile, admin_account):
    response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_account["email"],
            "password": admin_account["password"],
            "turnstile_token": "test-bypass",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["token_type"] == "bearer"


def test_login_with_wrong_credentials_returns_401(api_client, disable_turnstile, admin_account):
    response = api_client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_account["email"],
            "password": "incorrect-pass",
            "turnstile_token": "test-bypass",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email o contraseña incorrectos"


def test_repairs_endpoint_accepts_valid_admin_token(api_client, admin_token):
    response = api_client.get("/api/v1/repairs/", headers=_auth_headers(admin_token))

    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)


def test_user_schema_supports_nullable_username(db):
    from app.core.security import hash_password
    from app.models.user import User
    from app.schemas.user import UserRead

    slug = uuid.uuid4().hex[:8]
    db_user = User(
        email=f"nullable-user-{slug}@example.com",
        username=None,
        first_name="Nullable",
        last_name=f"User {slug}",
        hashed_password=hash_password("nullable-user-pass"),
        role_id=3,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    serialized = UserRead.model_validate(db_user).model_dump()
    assert serialized["id"] == db_user.id
    assert serialized["username"] is None


def test_repair_lifecycle_create_update_archive_reactivate(api_client, admin_token, customer_account):
    slug = uuid.uuid4().hex[:8]
    create_response = api_client.post(
        "/api/v1/repairs/",
        headers=_auth_headers(admin_token),
        json={
            "client_id": customer_account["client"].id,
            "title": f"Lifecycle OT {slug}",
            "description": f"Problema lifecycle {slug}",
            "payment_method": "transfer",
            "paid_amount": 25000,
        },
    )

    assert create_response.status_code in (200, 201), create_response.text
    created = create_response.json()
    repair_id = created["id"]

    detail_response = api_client.get(f"/api/v1/repairs/{repair_id}", headers=_auth_headers(admin_token))
    assert detail_response.status_code == 200, detail_response.text
    detail = detail_response.json()
    assert detail["id"] == repair_id
    assert detail["client"]["id"] == customer_account["client"].id
    assert detail["status_code"] == "ingreso"
    assert detail["allowed_status_ids"] == [1, 2, 10]

    update_response = api_client.put(
        f"/api/v1/repairs/{repair_id}",
        headers=_auth_headers(admin_token),
        json={
            "diagnosis": f"Diagnostico {slug}",
            "work_performed": f"Trabajo {slug}",
            "status_id": 2,
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["diagnosis"] == f"Diagnostico {slug}"
    assert updated["work_performed"] == f"Trabajo {slug}"
    assert updated["status_id"] == 2

    updated_detail_response = api_client.get(f"/api/v1/repairs/{repair_id}", headers=_auth_headers(admin_token))
    assert updated_detail_response.status_code == 200, updated_detail_response.text
    updated_detail = updated_detail_response.json()
    assert updated_detail["status_code"] == "diagnostico"
    assert updated_detail["allowed_status_ids"] == [2, 3, 10]

    archive_response = api_client.post(f"/api/v1/repairs/{repair_id}/archive", headers=_auth_headers(admin_token))
    assert archive_response.status_code == 200, archive_response.text
    assert archive_response.json()["ok"] is True

    archived_detail_response = api_client.get(f"/api/v1/repairs/{repair_id}", headers=_auth_headers(admin_token))
    assert archived_detail_response.status_code == 200, archived_detail_response.text
    assert archived_detail_response.json()["archived_at"] is not None

    reactivate_response = api_client.post(
        f"/api/v1/repairs/{repair_id}/reactivate",
        headers=_auth_headers(admin_token),
    )
    assert reactivate_response.status_code == 200, reactivate_response.text
    assert reactivate_response.json()["status_id"] == 1


def test_inventory_crud_flow(api_client, admin_token, db):
    slug = uuid.uuid4().hex[:8]
    category = _create_category(db, slug=slug)

    create_response = api_client.post(
        "/api/v1/inventory/",
        headers=_auth_headers(admin_token),
        json={
            "name": f"Item Integracion {slug}",
            "sku": f"INT-{slug.upper()}",
            "category_id": category.id,
            "price": 9900,
            "stock": 7,
            "min_quantity": 2,
            "enabled": True,
            "store_visible": True,
        },
    )
    assert create_response.status_code in (200, 201), create_response.text
    created = create_response.json()
    product_id = created["id"]
    assert created["store_visible"] is True

    get_response = api_client.get(f"/api/v1/inventory/{product_id}", headers=_auth_headers(admin_token))
    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["sku"] == f"INT-{slug.upper()}"

    update_response = api_client.put(
        f"/api/v1/inventory/{product_id}",
        headers=_auth_headers(admin_token),
        json={
            "name": f"Item Integracion {slug} Editado",
            "price": 12900,
            "stock": 11,
            "store_visible": False,
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["name"] == f"Item Integracion {slug} Editado"
    assert updated["stock"] == 11
    assert updated["store_visible"] is False

    delete_response = api_client.delete(f"/api/v1/inventory/{product_id}", headers=_auth_headers(admin_token))
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["ok"] is True

    deleted_detail = api_client.get(f"/api/v1/inventory/{product_id}", headers=_auth_headers(admin_token))
    assert deleted_detail.status_code == 404


def test_clients_crud_flow(api_client, admin_token, db):
    from app.models.client import Client

    slug = uuid.uuid4().hex[:8]
    create_response = api_client.post(
        "/api/v1/clients/",
        headers=_auth_headers(admin_token),
        json={
            "name": f"Cliente Integracion {slug}",
            "email": f"cliente.{slug}@example.com",
            "phone": f"+569{slug}",
            "city": "Santiago",
            "region": "RM",
        },
    )
    assert create_response.status_code in (200, 201), create_response.text
    created = create_response.json()
    client_id = created["id"]
    assert created["name"] == f"Cliente Integracion {slug}"

    get_response = api_client.get(f"/api/v1/clients/{client_id}", headers=_auth_headers(admin_token))
    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["email"] == f"cliente.{slug}@example.com"

    update_response = api_client.put(
        f"/api/v1/clients/{client_id}",
        headers=_auth_headers(admin_token),
        json={
            "city": "Valparaiso",
            "phone": f"+5699{slug}",
        },
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["ok"] is True

    db.expire_all()
    stored = db.query(Client).filter(Client.id == client_id).first()
    assert stored is not None
    assert stored.city == "Valparaiso"
    assert stored.phone == f"+5699{slug}"

    delete_response = api_client.delete(f"/api/v1/clients/{client_id}", headers=_auth_headers(admin_token))
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json()["ok"] is True

    db.expire_all()
    assert db.query(Client).filter(Client.id == client_id).first() is None


def test_signature_request_flow_persists_signature(api_client, admin_token, sample_ot):
    repair_id = sample_ot["repair_id"]
    create_response = api_client.post(
        "/api/v1/signatures/requests",
        headers=_auth_headers(admin_token),
        json={
            "repair_id": repair_id,
            "request_type": "ingreso",
            "expires_minutes": 5,
        },
    )
    assert create_response.status_code == 200, create_response.text
    created = create_response.json()
    token = created["token"]
    request_id = created["id"]

    lookup_response = api_client.get(f"/api/v1/signatures/requests/token/{token}")
    assert lookup_response.status_code == 200, lookup_response.text
    assert lookup_response.json()["id"] == request_id

    image_base64 = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WlH0e0AAAAASUVORK5CYII="
    )
    submit_response = api_client.post(
        "/api/v1/signatures/submit",
        json={
            "token": token,
            "image_base64": image_base64,
        },
    )
    assert submit_response.status_code == 200, submit_response.text
    submitted = submit_response.json()
    assert submitted["ok"] is True

    signature_path = Path(submitted["path"])
    assert signature_path.exists()

    repair_response = api_client.get(f"/api/v1/repairs/{repair_id}", headers=_auth_headers(admin_token))
    assert repair_response.status_code == 200, repair_response.text
    assert repair_response.json()["signature_ingreso_path"] == submitted["path"]

    request_response = api_client.get(f"/api/v1/signatures/requests/{request_id}", headers=_auth_headers(admin_token))
    assert request_response.status_code == 200, request_response.text
    request_payload = request_response.json()
    assert request_payload["status"] == "signed"
    assert request_payload["signed_at"] is not None

    signature_path.unlink(missing_ok=True)
