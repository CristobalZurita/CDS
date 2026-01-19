#!/usr/bin/env python3
"""
Script de Auditoría del Sistema CDS
===================================
Auditoría NO DESTRUCTIVA - Solo lectura, no modifica nada.

Verifica:
1. Archivos Python vacíos o con solo comentarios
2. Imports rotos o módulos faltantes
3. Endpoints del API (sintaxis y registros)
4. Modelos y sus relaciones
5. Routers registrados vs disponibles
6. Schemas definidos
7. Services y sus dependencias

Uso:
    python scripts/audit_system.py
    python scripts/audit_system.py --verbose
    python scripts/audit_system.py --test-endpoints  # Requiere servidor corriendo
"""

import os
import sys
import ast
import importlib
import importlib.util
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@dataclass
class AuditResult:
    """Resultado de una verificación"""
    category: str
    item: str
    status: str  # OK, WARNING, ERROR
    message: str
    details: Optional[str] = None


@dataclass
class AuditReport:
    """Reporte completo de auditoría"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    results: List[AuditResult] = field(default_factory=list)

    def add(self, category: str, item: str, status: str, message: str, details: str = None):
        self.results.append(AuditResult(category, item, status, message, details))

    def ok(self, category: str, item: str, message: str):
        self.add(category, item, "OK", message)

    def warning(self, category: str, item: str, message: str, details: str = None):
        self.add(category, item, "WARNING", message, details)

    def error(self, category: str, item: str, message: str, details: str = None):
        self.add(category, item, "ERROR", message, details)

    def summary(self) -> Dict[str, int]:
        return {
            "OK": sum(1 for r in self.results if r.status == "OK"),
            "WARNING": sum(1 for r in self.results if r.status == "WARNING"),
            "ERROR": sum(1 for r in self.results if r.status == "ERROR"),
        }


class SystemAuditor:
    """Auditor del sistema - Solo lectura"""

    def __init__(self, root_dir: Path, verbose: bool = False):
        self.root_dir = root_dir
        self.app_dir = root_dir / "app"
        self.verbose = verbose
        self.report = AuditReport()

    def log(self, msg: str):
        if self.verbose:
            print(f"  [DEBUG] {msg}")

    def run_all_audits(self) -> AuditReport:
        """Ejecuta todas las auditorías"""
        print("\n" + "="*60)
        print("  AUDITORÍA DEL SISTEMA CDS")
        print("  Modo: Solo lectura (no destructivo)")
        print("="*60 + "\n")

        audits = [
            ("Archivos Vacíos", self.audit_empty_files),
            ("Sintaxis Python", self.audit_python_syntax),
            ("Imports", self.audit_imports),
            ("Modelos", self.audit_models),
            ("Routers", self.audit_routers),
            ("Schemas", self.audit_schemas),
            ("Services", self.audit_services),
            ("Endpoints Registrados", self.audit_registered_endpoints),
            ("Configuración", self.audit_config),
            ("Base de Datos", self.audit_database),
        ]

        for name, audit_func in audits:
            print(f"\n[{name}]")
            print("-" * 40)
            try:
                audit_func()
            except Exception as e:
                self.report.error(name, "audit_execution", f"Error ejecutando auditoría: {e}")
                print(f"  ERROR: {e}")

        return self.report

    # =========================================================================
    # AUDITORÍA 1: Archivos Vacíos
    # =========================================================================

    def audit_empty_files(self):
        """Detecta archivos Python vacíos o con solo comentarios/docstrings"""

        for py_file in self.app_dir.rglob("*.py"):
            rel_path = py_file.relative_to(self.root_dir)

            try:
                content = py_file.read_text(encoding='utf-8')

                # Archivo completamente vacío
                if not content.strip():
                    self.report.warning("Archivos Vacíos", str(rel_path), "Archivo vacío")
                    print(f"  WARNING: {rel_path} está vacío")
                    continue

                # Solo tiene __init__ o imports triviales
                lines = [l.strip() for l in content.split('\n')
                        if l.strip() and not l.strip().startswith('#')]

                # Filtrar solo docstrings y pass
                code_lines = []
                in_docstring = False
                for line in lines:
                    if '"""' in line or "'''" in line:
                        if line.count('"""') == 2 or line.count("'''") == 2:
                            continue  # Docstring de una línea
                        in_docstring = not in_docstring
                        continue
                    if in_docstring:
                        continue
                    if line not in ('pass', '...'):
                        code_lines.append(line)

                if len(code_lines) == 0:
                    self.report.warning("Archivos Vacíos", str(rel_path),
                                       "Solo contiene docstrings/comentarios")
                    print(f"  WARNING: {rel_path} solo tiene docstrings/comentarios")
                elif len(code_lines) < 3 and py_file.name != "__init__.py":
                    self.report.warning("Archivos Vacíos", str(rel_path),
                                       f"Archivo muy pequeño ({len(code_lines)} líneas de código)")
                    print(f"  WARNING: {rel_path} muy pequeño ({len(code_lines)} líneas)")
                else:
                    self.report.ok("Archivos Vacíos", str(rel_path), "OK")
                    self.log(f"OK: {rel_path}")

            except Exception as e:
                self.report.error("Archivos Vacíos", str(rel_path), f"Error leyendo: {e}")
                print(f"  ERROR: {rel_path}: {e}")

    # =========================================================================
    # AUDITORÍA 2: Sintaxis Python
    # =========================================================================

    def audit_python_syntax(self):
        """Verifica que todos los archivos Python tengan sintaxis válida"""

        errors = []
        ok_count = 0

        for py_file in self.app_dir.rglob("*.py"):
            rel_path = py_file.relative_to(self.root_dir)

            try:
                content = py_file.read_text(encoding='utf-8')
                ast.parse(content)
                self.report.ok("Sintaxis Python", str(rel_path), "Sintaxis válida")
                ok_count += 1
                self.log(f"OK: {rel_path}")
            except SyntaxError as e:
                self.report.error("Sintaxis Python", str(rel_path),
                                 f"Error de sintaxis línea {e.lineno}: {e.msg}")
                errors.append((rel_path, e))
                print(f"  ERROR: {rel_path}:{e.lineno} - {e.msg}")

        if not errors:
            print(f"  OK: {ok_count} archivos con sintaxis válida")
        else:
            print(f"  {len(errors)} archivos con errores de sintaxis")

    # =========================================================================
    # AUDITORÍA 3: Imports
    # =========================================================================

    def audit_imports(self):
        """Verifica que los imports sean válidos"""

        errors = []
        warnings = []

        for py_file in self.app_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            rel_path = py_file.relative_to(self.root_dir)

            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_import(alias.name, rel_path, errors, warnings)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._check_import(node.module, rel_path, errors, warnings,
                                             is_from=True, level=node.level)

            except SyntaxError:
                pass  # Ya reportado en audit_python_syntax
            except Exception as e:
                self.report.error("Imports", str(rel_path), f"Error analizando: {e}")

        if errors:
            print(f"  {len(errors)} imports con errores")
            for path, module, err in errors[:5]:  # Mostrar máximo 5
                print(f"    - {path}: {module} ({err})")
            if len(errors) > 5:
                print(f"    ... y {len(errors)-5} más")

        if warnings:
            print(f"  {len(warnings)} imports con advertencias")

        if not errors and not warnings:
            print("  OK: Todos los imports verificados")

    def _check_import(self, module: str, file_path: Path, errors: list, warnings: list,
                     is_from: bool = False, level: int = 0):
        """Verifica un import específico"""

        # Ignorar imports relativos internos
        if level > 0:
            return

        # Ignorar módulos estándar y de terceros conocidos
        stdlib_and_common = {
            'os', 'sys', 'typing', 'datetime', 'json', 'logging', 'pathlib',
            'uuid', 'hashlib', 'secrets', 're', 'collections', 'functools',
            'fastapi', 'sqlalchemy', 'pydantic', 'jose', 'passlib', 'sendgrid',
            'httpx', 'requests', 'pytest', 'dotenv', 'email_validator'
        }

        root_module = module.split('.')[0]
        if root_module in stdlib_and_common:
            return

        # Verificar imports de app
        if module.startswith('app.'):
            try:
                importlib.import_module(module)
                self.report.ok("Imports", f"{file_path}:{module}", "Import válido")
            except ImportError as e:
                self.report.error("Imports", f"{file_path}:{module}", f"Import fallido: {e}")
                errors.append((file_path, module, str(e)))
            except Exception as e:
                self.report.warning("Imports", f"{file_path}:{module}", f"Error verificando: {e}")
                warnings.append((file_path, module, str(e)))

    # =========================================================================
    # AUDITORÍA 4: Modelos
    # =========================================================================

    def audit_models(self):
        """Verifica los modelos SQLAlchemy"""

        models_dir = self.app_dir / "models"
        if not models_dir.exists():
            self.report.error("Modelos", "models/", "Directorio de modelos no existe")
            print("  ERROR: Directorio app/models no existe")
            return

        models_found = []

        for py_file in models_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            rel_path = py_file.relative_to(self.root_dir)

            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)

                # Buscar clases que hereden de Base
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Verificar si tiene __tablename__
                        has_tablename = any(
                            isinstance(item, ast.Assign) and
                            any(t.id == '__tablename__' for t in item.targets if isinstance(t, ast.Name))
                            for item in node.body
                        )

                        if has_tablename:
                            models_found.append((py_file.stem, node.name))
                            self.report.ok("Modelos", f"{rel_path}:{node.name}",
                                          "Modelo SQLAlchemy válido")
                            self.log(f"OK: Modelo {node.name} en {py_file.name}")

            except Exception as e:
                self.report.error("Modelos", str(rel_path), f"Error analizando: {e}")
                print(f"  ERROR: {rel_path}: {e}")

        print(f"  OK: {len(models_found)} modelos encontrados")
        if self.verbose:
            for file, model in models_found:
                print(f"    - {model} ({file}.py)")

    # =========================================================================
    # AUDITORÍA 5: Routers
    # =========================================================================

    def audit_routers(self):
        """Verifica los routers de FastAPI"""

        routers_dir = self.app_dir / "routers"
        endpoints_dir = self.app_dir / "api" / "v1" / "endpoints"

        routers_found = []

        # Buscar en app/routers/
        if routers_dir.exists():
            for py_file in routers_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                result = self._analyze_router(py_file)
                if result:
                    routers_found.append(result)

        # Buscar en app/api/v1/endpoints/
        if endpoints_dir.exists():
            for py_file in endpoints_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                result = self._analyze_router(py_file)
                if result:
                    routers_found.append(result)

        print(f"  OK: {len(routers_found)} routers encontrados")

        # Verificar cuáles están registrados
        try:
            from app.api.v1.router import api_router
            registered_routes = set()
            for route in api_router.routes:
                if hasattr(route, 'path'):
                    # Extraer el prefijo del path
                    parts = route.path.split('/')
                    if len(parts) > 1:
                        registered_routes.add(parts[1])

            for name, path, endpoints in routers_found:
                prefix = name.replace('_', '-')
                if name in registered_routes or prefix in registered_routes:
                    self.report.ok("Routers", name, f"Registrado con {endpoints} endpoints")
                    print(f"    ✓ {name}: {endpoints} endpoints (registrado)")
                else:
                    self.report.warning("Routers", name, f"NO registrado ({endpoints} endpoints)")
                    print(f"    ? {name}: {endpoints} endpoints (NO registrado)")

        except Exception as e:
            self.report.warning("Routers", "api_router", f"No se pudo verificar registro: {e}")
            for name, path, endpoints in routers_found:
                print(f"    - {name}: {endpoints} endpoints")

    def _analyze_router(self, py_file: Path) -> Optional[Tuple[str, str, int]]:
        """Analiza un archivo de router y cuenta sus endpoints"""
        try:
            content = py_file.read_text(encoding='utf-8')

            # Contar decoradores de endpoint
            endpoint_patterns = ['@router.get', '@router.post', '@router.put',
                               '@router.delete', '@router.patch']
            endpoint_count = sum(content.count(p) for p in endpoint_patterns)

            if endpoint_count > 0 or 'APIRouter' in content:
                return (py_file.stem, str(py_file), endpoint_count)

        except Exception:
            pass
        return None

    # =========================================================================
    # AUDITORÍA 6: Schemas
    # =========================================================================

    def audit_schemas(self):
        """Verifica los schemas de Pydantic"""

        schemas_dir = self.app_dir / "schemas"
        if not schemas_dir.exists():
            self.report.warning("Schemas", "schemas/", "Directorio de schemas no existe")
            print("  WARNING: Directorio app/schemas no existe")
            return

        schemas_found = []

        for py_file in schemas_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Verificar si hereda de BaseModel o similar
                        bases = [b.id if isinstance(b, ast.Name) else
                                (b.attr if isinstance(b, ast.Attribute) else None)
                                for b in node.bases]

                        if any(b in ('BaseModel', 'Base') for b in bases if b):
                            schemas_found.append((py_file.stem, node.name))
                            self.report.ok("Schemas", f"{py_file.stem}:{node.name}", "Schema válido")

            except Exception as e:
                self.report.error("Schemas", py_file.name, f"Error analizando: {e}")

        print(f"  OK: {len(schemas_found)} schemas encontrados")
        if self.verbose:
            for file, schema in schemas_found:
                print(f"    - {schema} ({file}.py)")

    # =========================================================================
    # AUDITORÍA 7: Services
    # =========================================================================

    def audit_services(self):
        """Verifica los servicios"""

        services_dir = self.app_dir / "services"
        if not services_dir.exists():
            self.report.warning("Services", "services/", "Directorio de services no existe")
            print("  WARNING: Directorio app/services no existe")
            return

        services_found = []

        for py_file in services_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')

                if len(content.strip()) < 50:
                    self.report.warning("Services", py_file.name, "Servicio muy pequeño o vacío")
                    print(f"  WARNING: {py_file.name} muy pequeño")
                    continue

                tree = ast.parse(content)

                # Contar clases y funciones
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

                if classes or functions:
                    services_found.append((py_file.stem, len(classes), len(functions)))
                    self.report.ok("Services", py_file.stem,
                                  f"{len(classes)} clases, {len(functions)} funciones")
                else:
                    self.report.warning("Services", py_file.name, "Sin clases ni funciones")
                    print(f"  WARNING: {py_file.name} sin clases ni funciones")

            except Exception as e:
                self.report.error("Services", py_file.name, f"Error: {e}")

        print(f"  OK: {len(services_found)} servicios encontrados")
        if self.verbose:
            for name, classes, funcs in services_found:
                print(f"    - {name}: {classes} clases, {funcs} funciones")

    # =========================================================================
    # AUDITORÍA 8: Endpoints Registrados
    # =========================================================================

    def audit_registered_endpoints(self):
        """Lista todos los endpoints registrados en la aplicación"""

        try:
            from app.api.v1.router import api_router

            endpoints = []
            for route in api_router.routes:
                if hasattr(route, 'methods') and hasattr(route, 'path'):
                    for method in route.methods:
                        if method not in ('HEAD', 'OPTIONS'):
                            endpoints.append((method, route.path))
                            self.report.ok("Endpoints", f"{method} {route.path}", "Registrado")

            # Agrupar por prefijo
            prefixes = {}
            for method, path in endpoints:
                parts = path.split('/')
                prefix = parts[1] if len(parts) > 1 else 'root'
                prefixes[prefix] = prefixes.get(prefix, 0) + 1

            print(f"  OK: {len(endpoints)} endpoints registrados")
            for prefix, count in sorted(prefixes.items()):
                print(f"    - /{prefix}: {count} endpoints")

        except Exception as e:
            self.report.error("Endpoints", "api_router", f"Error cargando router: {e}")
            print(f"  ERROR: No se pudo cargar el router: {e}")

    # =========================================================================
    # AUDITORÍA 9: Configuración
    # =========================================================================

    def audit_config(self):
        """Verifica archivos de configuración"""

        config_files = [
            ('app/core/config.py', True),
            ('app/core/database.py', True),
            ('app/core/security.py', True),
            ('.env', False),
            ('.env.example', False),
            ('requirements.txt', False),
            ('alembic.ini', False),
        ]

        for filename, required in config_files:
            filepath = self.root_dir / filename

            if filepath.exists():
                try:
                    content = filepath.read_text(encoding='utf-8')
                    if len(content.strip()) > 0:
                        self.report.ok("Configuración", filename, "Existe y tiene contenido")
                        print(f"  ✓ {filename}")
                    else:
                        self.report.warning("Configuración", filename, "Archivo vacío")
                        print(f"  ? {filename} (vacío)")
                except Exception as e:
                    self.report.error("Configuración", filename, f"Error leyendo: {e}")
            else:
                if required:
                    self.report.error("Configuración", filename, "Archivo requerido no existe")
                    print(f"  ✗ {filename} (requerido, no existe)")
                else:
                    self.report.warning("Configuración", filename, "Archivo opcional no existe")
                    self.log(f"  - {filename} (opcional)")

    # =========================================================================
    # AUDITORÍA 10: Base de Datos
    # =========================================================================

    def audit_database(self):
        """Verifica conexión y tablas de la base de datos"""

        try:
            from app.core.database import engine
            from sqlalchemy import inspect

            inspector = inspect(engine)
            tables = inspector.get_table_names()

            if tables:
                self.report.ok("Base de Datos", "connection", f"Conectado, {len(tables)} tablas")
                print(f"  OK: Conectado a la base de datos")
                print(f"  OK: {len(tables)} tablas encontradas")

                if self.verbose:
                    for table in sorted(tables):
                        columns = inspector.get_columns(table)
                        print(f"    - {table}: {len(columns)} columnas")
            else:
                self.report.warning("Base de Datos", "tables", "No hay tablas en la BD")
                print("  WARNING: No hay tablas en la base de datos")

        except Exception as e:
            self.report.error("Base de Datos", "connection", f"Error conectando: {e}")
            print(f"  ERROR: No se pudo conectar a la BD: {e}")


def test_endpoints_live(base_url: str = "http://localhost:8000"):
    """Test de endpoints en vivo (requiere servidor corriendo)"""

    try:
        import httpx
    except ImportError:
        print("ERROR: httpx no instalado. Ejecute: pip install httpx")
        return

    print(f"\n[Test de Endpoints en Vivo]")
    print(f"Base URL: {base_url}")
    print("-" * 40)

    # Endpoints públicos a testear
    public_endpoints = [
        ("GET", "/api/v1/brands/"),
        ("GET", "/api/v1/instruments/"),
        ("GET", "/api/v1/stats/dashboard"),
        ("GET", "/docs"),
        ("GET", "/openapi.json"),
    ]

    # Endpoints que requieren auth
    auth_endpoints = [
        ("GET", "/api/v1/users/"),
        ("GET", "/api/v1/repairs/"),
        ("GET", "/api/v1/tools/"),
    ]

    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        print("\nEndpoints públicos:")
        for method, path in public_endpoints:
            try:
                resp = client.request(method, path)
                status_icon = "✓" if resp.status_code < 400 else "✗"
                print(f"  {status_icon} {method} {path} -> {resp.status_code}")
            except Exception as e:
                print(f"  ✗ {method} {path} -> ERROR: {e}")

        print("\nEndpoints con auth (esperado 401/403):")
        for method, path in auth_endpoints:
            try:
                resp = client.request(method, path)
                expected = resp.status_code in (401, 403, 200)
                status_icon = "✓" if expected else "?"
                print(f"  {status_icon} {method} {path} -> {resp.status_code}")
            except Exception as e:
                print(f"  ✗ {method} {path} -> ERROR: {e}")


def print_report(report: AuditReport):
    """Imprime el resumen del reporte"""

    summary = report.summary()

    print("\n" + "="*60)
    print("  RESUMEN DE AUDITORÍA")
    print("="*60)
    print(f"\n  Timestamp: {report.timestamp}")
    print(f"\n  Resultados:")
    print(f"    ✓ OK:       {summary['OK']}")
    print(f"    ? WARNING:  {summary['WARNING']}")
    print(f"    ✗ ERROR:    {summary['ERROR']}")
    print(f"\n  Total verificaciones: {sum(summary.values())}")

    # Mostrar errores si hay
    errors = [r for r in report.results if r.status == "ERROR"]
    if errors:
        print(f"\n  Errores encontrados ({len(errors)}):")
        for err in errors[:10]:
            print(f"    - [{err.category}] {err.item}: {err.message}")
        if len(errors) > 10:
            print(f"    ... y {len(errors)-10} errores más")

    # Mostrar warnings importantes
    warnings = [r for r in report.results if r.status == "WARNING"]
    if warnings and len(warnings) <= 10:
        print(f"\n  Advertencias ({len(warnings)}):")
        for warn in warnings:
            print(f"    - [{warn.category}] {warn.item}: {warn.message}")
    elif warnings:
        print(f"\n  Advertencias: {len(warnings)} (use --verbose para ver todas)")

    print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Auditoría del Sistema CDS")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar más detalles")
    parser.add_argument("--test-endpoints", action="store_true",
                       help="Testear endpoints en vivo (requiere servidor)")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="URL base para test de endpoints")

    args = parser.parse_args()

    # Cambiar al directorio del backend
    os.chdir(ROOT_DIR)

    # Ejecutar auditoría
    auditor = SystemAuditor(ROOT_DIR, verbose=args.verbose)
    report = auditor.run_all_audits()

    # Test de endpoints en vivo si se solicita
    if args.test_endpoints:
        test_endpoints_live(args.url)

    # Imprimir resumen
    print_report(report)

    # Exit code basado en errores
    summary = report.summary()
    sys.exit(1 if summary['ERROR'] > 0 else 0)


if __name__ == "__main__":
    main()
