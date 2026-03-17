from __future__ import annotations

from collections import Counter

from app.main import app


def _iter_api_routes():
    for route in app.routes:
        methods = getattr(route, "methods", None)
        if not methods:
            continue

        endpoint = getattr(route, "endpoint", None)
        endpoint_module = getattr(endpoint, "__module__", "")

        for method in sorted(methods):
            if method in {"HEAD", "OPTIONS"}:
                continue
            yield method, route.path, endpoint_module


def test_api_v1_has_no_duplicate_method_path_registrations():
    route_keys = [(method, path) for method, path, _ in _iter_api_routes() if path.startswith("/api/v1/")]
    counts = Counter(route_keys)
    duplicates = [f"{method} {path} x{count}" for (method, path), count in counts.items() if count > 1]
    assert duplicates == [], f"Duplicate /api/v1 route registrations detected: {duplicates}"


def test_repairs_routes_are_served_by_repair_router_layer():
    repairs_routes = [
        (method, path, module)
        for method, path, module in _iter_api_routes()
        if path.startswith("/api/v1/repairs")
    ]
    assert repairs_routes, "Expected /api/v1/repairs routes to be registered"

    mismatches = [
        f"{method} {path} -> {module}"
        for method, path, module in repairs_routes
        if module != "app.routers.repair"
    ]
    assert mismatches == [], f"Unexpected router layer for /api/v1/repairs routes: {mismatches}"


def test_categories_routes_are_served_by_category_router_layer():
    categories_routes = [
        (method, path, module)
        for method, path, module in _iter_api_routes()
        if path.startswith("/api/v1/categories")
    ]
    assert categories_routes, "Expected /api/v1/categories routes to be registered"

    mismatches = [
        f"{method} {path} -> {module}"
        for method, path, module in categories_routes
        if module != "app.routers.category"
    ]
    assert mismatches == [], f"Unexpected router layer for /api/v1/categories routes: {mismatches}"


def test_openapi_marks_inventory_as_canonical_and_items_as_compatibility(test_client):
    paths = test_client.app.openapi()["paths"]
    inventory_list_path = "/api/v1/inventory/" if "/api/v1/inventory/" in paths else "/api/v1/inventory"

    assert paths["/api/v1/items"]["get"]["deprecated"] is True
    assert paths["/api/v1/items"]["post"]["deprecated"] is True
    assert paths["/api/v1/items/{item_id}"]["get"]["deprecated"] is True
    assert paths["/api/v1/items/{item_id}"]["put"]["deprecated"] is True
    assert paths["/api/v1/items/{item_id}"]["delete"]["deprecated"] is True

    assert paths[inventory_list_path]["get"].get("deprecated") is not True
    assert paths["/api/v1/inventory/{product_id}"]["get"].get("deprecated") is not True


def test_openapi_marks_media_as_canonical_and_images_as_compatibility(test_client):
    paths = test_client.app.openapi()["paths"]

    assert paths["/api/v1/images/catalog"]["get"]["deprecated"] is True
    assert paths["/api/v1/images/resolve"]["get"]["deprecated"] is True
    assert paths["/api/v1/images/resolve-batch"]["post"]["deprecated"] is True
    assert paths["/api/v1/images/search"]["get"]["deprecated"] is True

    assert paths["/api/v1/media/assets"]["get"].get("deprecated") is not True
    assert paths["/api/v1/media/bindings"]["get"].get("deprecated") is not True
