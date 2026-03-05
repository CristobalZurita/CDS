#!/usr/bin/env python3
"""
Test de Endpoints en Vivo
=========================
Testea todos los endpoints del API de forma NO DESTRUCTIVA.

Solo hace peticiones GET y verifica que respondan correctamente.
NO modifica datos (no hace POST/PUT/DELETE reales).

Uso:
    # Primero iniciar el servidor:
    uvicorn app.main:app --reload

    # Luego en otra terminal:
    python scripts/test_endpoints.py
    python scripts/test_endpoints.py --verbose
    python scripts/test_endpoints.py --url http://localhost:8000
"""

__test__ = False

import sys
import argparse
from datetime import datetime
from typing import List, Tuple, Optional

try:
    import httpx
except ImportError:
    print("ERROR: httpx no instalado.")
    print("Ejecute: pip install httpx")
    sys.exit(1)


def get_endpoints_from_openapi(client: httpx.Client) -> List[dict]:
    """Obtiene la lista de endpoints desde OpenAPI schema"""
    try:
        resp = client.get("/openapi.json")
        if resp.status_code != 200:
            return []

        schema = resp.json()
        endpoints = []

        for path, methods in schema.get("paths", {}).items():
            for method, details in methods.items():
                if method.upper() in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                    endpoints.append({
                        "method": method.upper(),
                        "path": path,
                        "summary": details.get("summary", ""),
                        "tags": details.get("tags", []),
                        "security": bool(details.get("security", []))
                    })

        return endpoints
    except Exception as e:
        print(f"Error obteniendo OpenAPI schema: {e}")
        return []


def test_endpoint(client: httpx.Client, method: str, path: str,
                 auth_token: Optional[str] = None) -> Tuple[int, str, float]:
    """
    Testea un endpoint y retorna (status_code, message, tiempo_ms)
    Solo ejecuta GET de forma segura.
    """

    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # Para seguridad, solo hacemos GET
    # POST/PUT/DELETE se simulan verificando que el endpoint existe
    if method != "GET":
        # Solo verificamos que el endpoint está definido, no lo ejecutamos
        return (0, "SKIPPED (no-GET)", 0)

    # Reemplazar parámetros de path con valores de prueba
    test_path = path
    if "{" in path:
        # Usar ID 1 para pruebas (es seguro porque solo es GET)
        test_path = path.replace("{id}", "1")
        test_path = test_path.replace("{repair_id}", "1")
        test_path = test_path.replace("{tool_id}", "1")
        test_path = test_path.replace("{user_id}", "1")
        test_path = test_path.replace("{client_id}", "1")
        test_path = test_path.replace("{message_id}", "1")
        test_path = test_path.replace("{item_id}", "1")
        # Patrón genérico para cualquier otro {xxx_id} o {xxx}
        import re
        test_path = re.sub(r'\{[^}]+\}', '1', test_path)

    try:
        start = datetime.now()
        resp = client.get(test_path, headers=headers)
        elapsed = (datetime.now() - start).total_seconds() * 1000

        if resp.status_code == 200:
            return (200, "OK", elapsed)
        elif resp.status_code == 401:
            return (401, "AUTH_REQUIRED", elapsed)
        elif resp.status_code == 403:
            return (403, "FORBIDDEN", elapsed)
        elif resp.status_code == 404:
            return (404, "NOT_FOUND", elapsed)
        elif resp.status_code == 422:
            return (422, "VALIDATION_ERROR", elapsed)
        elif resp.status_code >= 500:
            return (resp.status_code, "SERVER_ERROR", elapsed)
        else:
            return (resp.status_code, f"HTTP_{resp.status_code}", elapsed)

    except httpx.ConnectError:
        return (-1, "CONNECTION_ERROR", 0)
    except httpx.TimeoutException:
        return (-2, "TIMEOUT", 0)
    except Exception as e:
        return (-3, f"ERROR: {str(e)[:50]}", 0)


def run_tests(base_url: str, verbose: bool = False, auth_token: str = None):
    """Ejecuta todos los tests de endpoints"""

    print("\n" + "="*70)
    print("  TEST DE ENDPOINTS - CDS API")
    print("  Modo: Solo lectura (GET requests)")
    print(f"  URL: {base_url}")
    print("="*70)

    with httpx.Client(base_url=base_url, timeout=30.0) as client:

        # 1. Verificar que el servidor está corriendo
        print("\n[1] Verificando servidor...")
        try:
            resp = client.get("/docs")
            if resp.status_code == 200:
                print("  ✓ Servidor respondiendo correctamente")
            else:
                print(f"  ✗ Servidor respondió con código {resp.status_code}")
        except httpx.ConnectError:
            print("  ✗ No se puede conectar al servidor")
            print(f"    Verifique que el servidor esté corriendo en {base_url}")
            return
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return

        # 2. Obtener lista de endpoints desde OpenAPI
        print("\n[2] Obteniendo endpoints desde OpenAPI...")
        endpoints = get_endpoints_from_openapi(client)

        if not endpoints:
            print("  ✗ No se pudieron obtener los endpoints")
            print("    Probando endpoints conocidos manualmente...")
            endpoints = [
                {"method": "GET", "path": "/api/v1/brands/", "tags": ["brands"], "security": False},
                {"method": "GET", "path": "/api/v1/instruments/", "tags": ["instruments"], "security": False},
                {"method": "GET", "path": "/api/v1/repairs/", "tags": ["repairs"], "security": True},
                {"method": "GET", "path": "/api/v1/tools/", "tags": ["tools"], "security": True},
                {"method": "GET", "path": "/api/v1/users/", "tags": ["users"], "security": True},
            ]

        print(f"  ✓ {len(endpoints)} endpoints encontrados")

        # 3. Agrupar por tags
        by_tag = {}
        for ep in endpoints:
            tag = ep["tags"][0] if ep["tags"] else "other"
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(ep)

        # 4. Ejecutar tests
        print("\n[3] Ejecutando tests...")
        print("-"*70)

        results = {
            "ok": 0,
            "auth_required": 0,
            "not_found": 0,
            "errors": 0,
            "skipped": 0
        }

        for tag in sorted(by_tag.keys()):
            tag_endpoints = by_tag[tag]
            print(f"\n  [{tag}] ({len(tag_endpoints)} endpoints)")

            for ep in tag_endpoints:
                method = ep["method"]
                path = ep["path"]

                status, msg, elapsed = test_endpoint(client, method, path, auth_token)

                if method != "GET":
                    results["skipped"] += 1
                    if verbose:
                        print(f"    - {method:6} {path:40} -> SKIPPED")
                    continue

                # Determinar icono y conteo
                if status == 200:
                    icon = "✓"
                    results["ok"] += 1
                elif status in (401, 403):
                    icon = "🔒"
                    results["auth_required"] += 1
                elif status == 404:
                    icon = "?"
                    results["not_found"] += 1
                elif status < 0:
                    icon = "✗"
                    results["errors"] += 1
                else:
                    icon = "!"
                    results["errors"] += 1

                if verbose or status not in (200, 401, 403, 0):
                    time_str = f"{elapsed:.0f}ms" if elapsed > 0 else ""
                    print(f"    {icon} {method:6} {path:40} -> {status:3} {msg} {time_str}")

        # 5. Resumen
        print("\n" + "="*70)
        print("  RESUMEN")
        print("="*70)
        print(f"\n  Resultados:")
        print(f"    ✓ OK (200):          {results['ok']}")
        print(f"    🔒 Auth requerida:    {results['auth_required']}")
        print(f"    ? Not Found (404):   {results['not_found']}")
        print(f"    ✗ Errores:           {results['errors']}")
        print(f"    - Skipped (no-GET):  {results['skipped']}")

        total_tested = results['ok'] + results['auth_required'] + results['not_found'] + results['errors']
        print(f"\n  Total testeados: {total_tested}")
        print(f"  Total endpoints: {len(endpoints)}")

        if results['errors'] == 0:
            print("\n  ✓ Todos los endpoints GET responden correctamente")
        else:
            print(f"\n  ✗ {results['errors']} endpoints con errores")

        print("\n" + "="*70 + "\n")

        return results['errors'] == 0


def main():
    parser = argparse.ArgumentParser(description="Test de endpoints del API CDS")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="URL base del servidor (default: http://localhost:8000)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Mostrar todos los resultados")
    parser.add_argument("--token", "-t",
                       help="Token JWT para autenticación (opcional)")

    args = parser.parse_args()

    success = run_tests(args.url, args.verbose, args.token)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
