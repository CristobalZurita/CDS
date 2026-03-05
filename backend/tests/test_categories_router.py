import pytest
import uuid

from fastapi import HTTPException

from app.api.v1.endpoints.categories import (
    create_category_endpoint,
    delete_category_endpoint,
    get_category_endpoint,
    list_categories_endpoint,
    update_category_endpoint,
)
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def test_categories_router_crud_flow(db):
    unique = uuid.uuid4().hex[:8]
    category_name = f"Category Test {unique}"

    existing = db.query(Category).filter(Category.name == category_name).all()
    for category in existing:
        db.delete(category)
    db.commit()

    created = create_category_endpoint(
        CategoryCreate(
            name=category_name,
            description="Category created from router CRUD test",
        ),
        db,
    )
    assert created.id is not None
    category_id = int(created.id)

    listed = list_categories_endpoint(db)
    assert any(int(item.id) == category_id for item in listed)

    loaded = get_category_endpoint(category_id, db)
    assert int(loaded.id) == category_id

    update_payload = {"description": "Updated from categories router test"}
    updated = update_category_endpoint(category_id, CategoryUpdate(**update_payload), db)
    assert updated.description == update_payload["description"]

    deleted = delete_category_endpoint(category_id, db)
    assert deleted.get("ok") is True

    listed_after_delete = list_categories_endpoint(db)
    assert not any(int(item.id) == category_id for item in listed_after_delete)

    with pytest.raises(HTTPException) as exc_info:
        get_category_endpoint(category_id, db)
    assert exc_info.value.status_code == 404
