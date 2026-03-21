import uuid


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_stock_movements_can_filter_by_product(test_client, db, admin_token):
    from app.models.category import Category
    from app.models.inventory import Product
    from app.models.stock import Stock
    from app.models.stock_movement import StockMovement

    slug = uuid.uuid4().hex[:8]
    category = Category(name=f"Stock Mov {slug}", description="Categoria stock")
    db.add(category)
    db.flush()

    product = Product(
        category_id=category.id,
        name=f"Producto Stock {slug}",
        sku=f"STOCK-{slug.upper()}",
        description="Producto para movimientos",
        price=15000,
        quantity=9,
        min_quantity=2,
    )
    db.add(product)
    db.flush()

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=9,
        minimum_stock=2,
    )
    db.add(stock)
    db.flush()

    db.add(
        StockMovement(
            stock_id=stock.id,
            movement_type="OUT",
            quantity=2,
            notes="Uso en reparacion",
        )
    )
    db.commit()

    response = test_client.get(
        f"/api/v1/stock-movements/?product_id={product.id}",
        headers=_auth_headers(admin_token),
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["stock_id"] == stock.id
    assert payload[0]["component_table"] == "products"
    assert payload[0]["component_id"] == product.id
    assert payload[0]["movement_type"] == "OUT"


def test_stock_movement_create_sets_performed_by(test_client, db, admin_token, admin_account):
    from app.models.category import Category
    from app.models.inventory import Product
    from app.models.stock import Stock

    slug = uuid.uuid4().hex[:8]
    category = Category(name=f"Stock Create {slug}", description="Categoria stock create")
    db.add(category)
    db.flush()

    product = Product(
        category_id=category.id,
        name=f"Producto Create {slug}",
        sku=f"CREATE-{slug.upper()}",
        description="Producto para crear movimiento",
        price=9000,
        quantity=5,
        min_quantity=1,
    )
    db.add(product)
    db.flush()

    stock = Stock(
        component_table="products",
        component_id=product.id,
        quantity=5,
        minimum_stock=1,
    )
    db.add(stock)
    db.commit()

    response = test_client.post(
        "/api/v1/stock-movements/",
        headers=_auth_headers(admin_token),
        json={
            "stock_id": stock.id,
            "movement_type": "RESERVE",
            "quantity": 1,
            "notes": "Reserva manual",
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["stock_id"] == stock.id
    assert payload["movement_type"] == "RESERVE"
    assert payload["quantity"] == 1
    assert payload["performed_by"] == admin_account["user"].id
