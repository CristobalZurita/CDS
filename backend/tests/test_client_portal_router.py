"""
test_client_portal_router.py
============================
Verifica que las rutas /api/v1/client/* son servidas por app.routers.client_portal
(el módulo renombrado desde app.routers.client).

Mismo patrón que test_api_router_dedupe.py — deconstructivo: se usa lo que existe.
ADITIVO: no modifica tests existentes.
"""

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


def test_client_portal_routes_are_registered():
    """Al menos una ruta /api/v1/client/* debe estar registrada."""
    routes = [
        (method, path)
        for method, path, _ in _iter_api_routes()
        if path.startswith("/api/v1/client")
    ]
    assert routes, "Expected /api/v1/client routes to be registered"


def test_client_portal_routes_served_by_client_portal_module():
    """
    Todas las rutas /api/v1/client/* deben provenir de app.routers.client_portal.
    No debe quedar ninguna servida por el módulo legacy app.routers.client.
    """
    routes = [
        (method, path, module)
        for method, path, module in _iter_api_routes()
        if path.startswith("/api/v1/client")
    ]

    # Ninguna ruta debe apuntar al módulo legacy
    legacy_routes = [
        f"{method} {path} -> {module}"
        for method, path, module in routes
        if module == "app.routers.client"
    ]
    assert legacy_routes == [], (
        f"Routes still served by legacy app.routers.client: {legacy_routes}"
    )

    # Al menos una debe apuntar al módulo nuevo
    portal_routes = [
        (method, path)
        for method, path, module in routes
        if module == "app.routers.client_portal"
    ]
    assert portal_routes, (
        "No routes served by app.routers.client_portal — check router registration in router.py"
    )
