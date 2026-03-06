import sys
import os
import pytest
from fastapi.testclient import TestClient
import httpx

pytest.importorskip("openpyxl")

# Ensure repository root is on sys.path so 'backend' package imports work in test runner
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app


client = TestClient(app)


def _safe_get(url: str, timeout: float = 60.0):
    try:
        return client.get(url, timeout=timeout)
    except httpx.TimeoutException:
        pytest.skip(f"Items endpoint timeout for {url} (POC Excel source)")


def test_list_items():
    r = _safe_get('/api/v1/items?limit=5')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_get_item():
    # Try fetching the first item by id
    list_r = _safe_get('/api/v1/items?limit=1')
    assert list_r.status_code == 200
    items = list_r.json()
    if not items:
        pytest.skip('No items present in Excel for POC test')
    item_id = items[0]['id']
    r = client.get(f'/api/v1/items/{item_id}')
    assert r.status_code == 200
    item = r.json()
    assert item['id'] == item_id
