from fastapi.testclient import TestClient
import importlib
import uuid

import app.main as _main


def test_categories_router_crud_flow():
    importlib.reload(_main)
    client = TestClient(_main.app)

    unique = uuid.uuid4().hex[:8]
    create_payload = {
        "name": f"Category Test {unique}",
        "description": "Category created from router CRUD test",
    }

    created_res = client.post("/api/v1/categories/", json=create_payload)
    assert created_res.status_code in (200, 201)
    created = created_res.json()
    assert created.get("id") is not None
    category_id = int(created["id"])

    listed_res = client.get("/api/v1/categories/")
    assert listed_res.status_code == 200
    listed = listed_res.json()
    assert any(int(item.get("id", -1)) == category_id for item in listed)

    update_payload = {"description": "Updated from categories router test"}
    updated_res = client.put(f"/api/v1/categories/{category_id}", json=update_payload)
    assert updated_res.status_code == 200
    updated = updated_res.json()
    assert updated.get("description") == update_payload["description"]

    delete_res = client.delete(f"/api/v1/categories/{category_id}")
    assert delete_res.status_code == 200
    assert delete_res.json().get("ok") is True

    listed_after_delete = client.get("/api/v1/categories/")
    assert listed_after_delete.status_code == 200
    assert not any(int(item.get("id", -1)) == category_id for item in listed_after_delete.json())
