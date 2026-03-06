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
