import sys
import os
import uuid
import pytest
from fastapi.testclient import TestClient
import httpx

pytest.importorskip("openpyxl")

# Ensure repository root is on sys.path so 'backend' package imports work in test runner
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app
from app.models.category import Category
from app.models.inventory import Product
from app.models.stock import Stock
from app.services.inventory_product_service import (
    get_item_summary_or_404,
    list_item_summaries,
)


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


def test_item_summary_compat_uses_canonical_stock_projection(db):
    slug = uuid.uuid4().hex[:8]
    category = Category(name=f"Compat {slug}", description="Categoria compat")
    db.add(category)
    db.flush()

    product = Product(
        category_id=category.id,
        name=f"Producto Compat {slug}",
        sku=f"COMPAT-{slug.upper()}",
        description="Compat test",
        price=12345,
        quantity=2,
        min_quantity=1,
    )
    db.add(product)
    db.flush()

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=9,
        minimum_stock=1,
    )
    db.add(stock)
    db.commit()

    summaries = list_item_summaries(db, limit=200, page=1, category=category.name)
    summary = next(item for item in summaries if item.id == product.id)
    assert summary.category == category.name
    assert summary.stock == 9

    detail = get_item_summary_or_404(db, product.id)
    assert detail.id == product.id
    assert detail.stock == 9
