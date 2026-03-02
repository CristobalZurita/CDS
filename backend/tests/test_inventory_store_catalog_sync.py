import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.routers.inventory import get_store_catalog_status, sync_store_catalog
import scripts.sync_store_catalog_from_inventory_images as sync_module


def test_get_store_catalog_status_uses_sync_status(monkeypatch):
    expected = {
        "files_count": 3,
        "linked_products_count": 2,
        "explicit_store_visible_count": 2,
        "with_nonzero_stock_count": 1,
        "sellable_now_count": 1,
        "pending_images_count": 1,
        "orphan_rows_count": 0,
        "pending_images": ["nuevo.webp"],
        "orphan_rows": [],
    }

    monkeypatch.setattr(sync_module, "build_catalog_status", lambda: expected)

    payload = get_store_catalog_status(user={"user_id": "1", "role": "admin"})

    assert payload == expected


def test_sync_store_catalog_returns_sync_result_and_status(monkeypatch):
    sync_result = {
        "images": 3,
        "matched": 2,
        "created": 1,
        "matched_items": [],
        "created_items": [],
    }
    status_payload = {
        "files_count": 3,
        "linked_products_count": 3,
        "explicit_store_visible_count": 3,
        "with_nonzero_stock_count": 1,
        "sellable_now_count": 1,
        "pending_images_count": 0,
        "orphan_rows_count": 0,
        "pending_images": [],
        "orphan_rows": [],
    }

    monkeypatch.setattr(sync_module, "sync_catalog", lambda apply_changes: sync_result)
    monkeypatch.setattr(sync_module, "build_catalog_status", lambda: status_payload)

    payload = sync_store_catalog(user={"user_id": "1", "role": "admin"})

    assert payload["ok"] is True
    assert payload["result"] == sync_result
    assert payload["status"] == status_payload
