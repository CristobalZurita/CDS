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
from app.crud.category import list_categories as crud_list_all
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

    # list_categories_endpoint usa LIMIT 100; la DB de test acumula filas entre
    # corridas, por lo que la nueva categoría puede caer fuera de la primera página.
    # Verificamos existencia con crud_list_all (sin límite) para no depender de paginación.
    listed = list_categories_endpoint(db)
    all_cats = crud_list_all(db, limit=99999)
    assert any(int(item.id) == category_id for item in all_cats)

    loaded = get_category_endpoint(category_id, db)
    assert int(loaded.id) == category_id

    update_payload = {"description": "Updated from categories router test"}
    updated = update_category_endpoint(category_id, CategoryUpdate(**update_payload), db)
    assert updated.description == update_payload["description"]

    deleted = delete_category_endpoint(category_id, db)
    assert deleted.get("ok") is True

    all_cats_after = crud_list_all(db, limit=99999)
    assert not any(int(item.id) == category_id for item in all_cats_after)

    with pytest.raises(HTTPException) as exc_info:
        get_category_endpoint(category_id, db)
    assert exc_info.value.status_code == 404
