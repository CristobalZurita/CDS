import os
import asyncio
import inspect
import functools
import uuid
from pathlib import Path
import logging
import pytest
import httpx
from alembic.config import Config
from alembic import command
import sqlalchemy
import anyio.to_thread
import fastapi.routing
import fastapi.concurrency
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
_ORIGINAL_ANYIO_RUN_SYNC = anyio.to_thread.run_sync
_ORIGINAL_FASTAPI_RUN_ENDPOINT_FUNCTION = fastapi.routing.run_endpoint_function
_ORIGINAL_FASTAPI_CONTEXTMANAGER_IN_THREADPOOL = fastapi.concurrency.contextmanager_in_threadpool
_COMPAT_THREADPOOL = ThreadPoolExecutor(max_workers=8)

ROOT = Path(__file__).resolve().parents[2]
TEST_DB_PATH = Path(os.getenv("TEST_DB_PATH", str(Path(__file__).resolve().parent / "test_cirujano.db")))
os.environ.setdefault("TEST_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_REFRESH_SECRET", "test-refresh-secret")
os.environ.setdefault("SKIP_MIGRATIONS", "1")


async def _run_sync_compat(func, *args, abandon_on_cancel=False, cancellable=None, limiter=None):
    loop = asyncio.get_running_loop()
    call = functools.partial(func, *args)
    return await loop.run_in_executor(_COMPAT_THREADPOOL, call)


async def _run_endpoint_function_compat(*, dependant, values, is_coroutine):
    assert dependant.call is not None, "dependant.call must be a function"
    if is_coroutine:
        return await dependant.call(**values)
    return dependant.call(**values)


@asynccontextmanager
async def _contextmanager_in_threadpool_compat(cm):
    try:
        yield cm.__enter__()
    except Exception as exc:
        ok = bool(cm.__exit__(type(exc), exc, exc.__traceback__))
        if not ok:
            raise
    else:
        cm.__exit__(None, None, None)


def _rebind_session(db_url: str):
    from sqlalchemy import create_engine
    from app.core import database as db_core

    engine = create_engine(
        db_url,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
    )
    db_core.engine = engine
    db_core.SessionLocal.configure(bind=engine)
    return engine


def _ensure_schema(db_url: str):
    from app.core.database import (
        Base,
        _ensure_appointments_schema,
        _ensure_instruments_schema,
        _ensure_payments_purchase_request_schema,
        _ensure_products_image_url_schema,
        _ensure_purchase_request_items_schema,
        _ensure_repairs_ot_schema,
    )
    from app import models  # noqa: F401

    engine = _rebind_session(db_url)
    Base.metadata.create_all(bind=engine)
    # Ajuste aditivo para DBs de test legacy que ya existían sin columnas OT/pagos.
    _ensure_repairs_ot_schema()
    _ensure_payments_purchase_request_schema()
    _ensure_products_image_url_schema()
    _ensure_appointments_schema()
    _ensure_instruments_schema()
    _ensure_purchase_request_items_schema()
    return engine


def _seed_roles(db_url: str):
    try:
        engine = _rebind_session(db_url)
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text("INSERT OR IGNORE INTO user_roles (id, name) VALUES (1, 'admin')"))
            conn.execute(sqlalchemy.text("INSERT OR IGNORE INTO user_roles (id, name) VALUES (2, 'technician')"))
            conn.execute(sqlalchemy.text("INSERT OR IGNORE INTO user_roles (id, name) VALUES (3, 'client')"))
    except Exception:
        logger.debug("Role seeding skipped")


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as asyncio")
    _install_fastapi_contextmanager_compat()
    _install_fastapi_endpoint_compat()
    _install_anyio_threadpool_compat()
    _install_testclient_compat()


def _install_testclient_compat():
    """
    Use an additive compatibility client in environments where
    starlette/fastapi TestClient blocks on AnyIO blocking portal.
    """
    if os.getenv("PYTEST_USE_NATIVE_TESTCLIENT", "0") == "1":
        logger.info("PYTEST_USE_NATIVE_TESTCLIENT=1 -> keeping native TestClient")
        return

    try:
        from tests.client_compat import CompatTestClient
        import fastapi.testclient as fastapi_testclient
        import starlette.testclient as starlette_testclient

        fastapi_testclient.TestClient = CompatTestClient
        starlette_testclient.TestClient = CompatTestClient
        logger.info("CompatTestClient activated for pytest runtime")
    except Exception as exc:
        logger.warning("Could not activate CompatTestClient: %s", exc)


def _install_anyio_threadpool_compat():
    """
    Python 3.13 + AnyIO/portal stack may block when FastAPI executes sync
    endpoints in tests. This keeps behavior equivalent while using a per-call
    executor that does not deadlock event loop shutdown.
    """
    if os.getenv("PYTEST_USE_NATIVE_ANYIO_THREADPOOL", "0") == "1":
        logger.info("PYTEST_USE_NATIVE_ANYIO_THREADPOOL=1 -> keeping native anyio.to_thread.run_sync")
        return

    anyio.to_thread.run_sync = _run_sync_compat
    logger.info("AnyIO run_sync compatibility patch activated for pytest runtime")


def _install_fastapi_endpoint_compat():
    """
    Avoid deadlock in this runtime when FastAPI dispatches sync endpoints via
    run_in_threadpool. In tests we execute sync endpoint callables directly.
    """
    if os.getenv("PYTEST_USE_NATIVE_FASTAPI_ENDPOINT_DISPATCH", "0") == "1":
        logger.info("PYTEST_USE_NATIVE_FASTAPI_ENDPOINT_DISPATCH=1 -> keeping native FastAPI endpoint dispatch")
        return

    fastapi.routing.run_endpoint_function = _run_endpoint_function_compat
    logger.info("FastAPI endpoint dispatch compatibility patch activated for pytest runtime")


def _install_fastapi_contextmanager_compat():
    """
    Avoid threadpool usage for sync context-manager dependencies in tests
    (e.g. get_db) to reduce sqlite + thread contention in this runtime.
    """
    if os.getenv("PYTEST_USE_NATIVE_FASTAPI_CONTEXTMANAGER", "0") == "1":
        logger.info("PYTEST_USE_NATIVE_FASTAPI_CONTEXTMANAGER=1 -> keeping native FastAPI contextmanager_in_threadpool")
        return

    fastapi.concurrency.contextmanager_in_threadpool = _contextmanager_in_threadpool_compat
    logger.info("FastAPI contextmanager compatibility patch activated for pytest runtime")


def pytest_pyfunc_call(pyfuncitem):
    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        sig = inspect.signature(testfunction)
        kwargs = {name: pyfuncitem.funcargs[name] for name in sig.parameters.keys() if name in pyfuncitem.funcargs}
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(testfunction(**kwargs))
        finally:
            loop.close()
            asyncio.set_event_loop(None)
        return True


def pytest_unconfigure(config):
    anyio.to_thread.run_sync = _ORIGINAL_ANYIO_RUN_SYNC
    fastapi.routing.run_endpoint_function = _ORIGINAL_FASTAPI_RUN_ENDPOINT_FUNCTION
    fastapi.concurrency.contextmanager_in_threadpool = _ORIGINAL_FASTAPI_CONTEXTMANAGER_IN_THREADPOOL
    _COMPAT_THREADPOOL.shutdown(wait=True, cancel_futures=False)


@pytest.fixture(autouse=True)
def _enforce_anyio_threadpool_patch():
    if os.getenv("PYTEST_USE_NATIVE_ANYIO_THREADPOOL", "0") != "1":
        anyio.to_thread.run_sync = _run_sync_compat
    yield


@pytest.fixture(autouse=True)
def _enforce_fastapi_endpoint_patch():
    if os.getenv("PYTEST_USE_NATIVE_FASTAPI_ENDPOINT_DISPATCH", "0") != "1":
        fastapi.routing.run_endpoint_function = _run_endpoint_function_compat
    yield


@pytest.fixture(autouse=True)
def _enforce_fastapi_contextmanager_patch():
    if os.getenv("PYTEST_USE_NATIVE_FASTAPI_CONTEXTMANAGER", "0") != "1":
        fastapi.concurrency.contextmanager_in_threadpool = _contextmanager_in_threadpool_compat
    yield


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply Alembic migrations before running tests."""
    if os.getenv("SKIP_MIGRATIONS") == "1":
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            _ensure_schema(db_url)
            _seed_roles(db_url)
        yield
        return
    here = Path(__file__).resolve().parents[1]  # backend/
    alembic_ini = here / "alembic.ini"
    script_location = here / "alembic"

    # Compatibilidad aditiva: fallback a estructura legacy si cambia layout.
    if not alembic_ini.exists():
        legacy_ini = here.parent / "alembic.ini"
        if legacy_ini.exists():
            alembic_ini = legacy_ini

    if not script_location.exists():
        legacy_script = here.parent / "alembic"
        if legacy_script.exists():
            script_location = legacy_script

    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option("script_location", str(script_location))
    # Ensure tests run against a fresh SQLite test database by default.
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # Use a local test DB file to avoid touching developer databases
        # Put the test DB inside the backend folder (where the app expects it)
        test_path = os.path.join(here, 'test_cirujano.db')
        test_url = f"sqlite:///{test_path}"
        os.environ['DATABASE_URL'] = test_url
        # remove any leftover test DB file from previous runs
        try:
            if os.path.exists(test_path):
                os.remove(test_path)
        except Exception:
            logger.warning("Could not remove existing test DB file; proceeding anyway")
        db_url = test_url

    # Reset automático de DB sqlite de test para evitar re-ejecutar migraciones
    # sobre esquemas ya existentes no idempotentes.
    if db_url.startswith("sqlite:///"):
        sqlite_path = Path(db_url.replace("sqlite:///", ""))
        should_reset = (
            os.getenv("KEEP_TEST_DB", "0") != "1"
            and "test" in sqlite_path.name.lower()
        )
        if should_reset and sqlite_path.exists():
            try:
                sqlite_path.unlink()
            except Exception:
                logger.warning("Could not reset sqlite test DB at %s", sqlite_path)

    # If pointing at a sqlite file that already has tables but no alembic version,
    # stamp the DB to head instead of trying to run the initial create_all migration
    # which will fail when tables already exist.
    if db_url.startswith("sqlite:///"):
        path = db_url.replace("sqlite:///", "")
        try:
            engine = sqlalchemy.create_engine(db_url)
            insp = sqlalchemy.inspect(engine)
            tables = insp.get_table_names()
            if 'alembic_version' not in tables and tables:
                # Schema exists but Alembic history does not: mark it as up-to-date
                command.stamp(alembic_cfg, 'head')
                yield
                return
        except Exception:
            # fall back to normal upgrade attempt
            logger.debug("Could not inspect sqlite DB; falling back to upgrade")

    # Use env vars / settings as configured by alembic/env.py
    command.upgrade(alembic_cfg, 'head')
    if db_url:
        _seed_roles(db_url)
    yield
    # No teardown: keep schema for inspection; tests should clean data if needed


@pytest.fixture(scope="session")
def app():
    from app.main import app as fastapi_app
    return fastapi_app


@pytest.fixture
def db():
    from app.core.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client(app):
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def live_api_url():
    return os.getenv("BACKEND_TEST_BASE_URL", "http://127.0.0.1:8002")


@pytest.fixture(scope="session")
def live_api_available(live_api_url):
    try:
        response = httpx.get(f"{live_api_url}/health", timeout=5.0)
        response.raise_for_status()
    except Exception as exc:
        pytest.skip(f"Live backend not available at {live_api_url}: {exc}")
    return live_api_url


@pytest.fixture
def api_client(live_api_available):
    with httpx.Client(base_url=live_api_available, timeout=20.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def disable_turnstile(monkeypatch):
    monkeypatch.setenv("TURNSTILE_DISABLE", "true")


def _build_user_payload(role_id: int) -> dict:
    slug = uuid.uuid4().hex[:10]
    role_name = "admin" if role_id == 1 else "client"
    return {
        "email": f"{role_name}.{slug}@example.com",
        "username": f"{role_name}_{slug}",
        "password": f"{role_name}pass123",
        "first_name": role_name.title(),
        "last_name": f"Fixture {slug[:4]}",
        "phone": f"+569{slug[:8]}",
    }


def _create_user(db, *, role_id: int):
    from app.core.security import hash_password
    from app.models.client import Client
    from app.models.user import User

    payload = _build_user_payload(role_id)
    user = User(
        email=payload["email"],
        username=payload["username"],
        hashed_password=hash_password(payload["password"]),
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        phone=payload["phone"],
        role_id=role_id,
        is_active=1,
        is_verified=1,
        two_factor_enabled=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    client = None
    if role_id == 3:
        client = Client(
            user_id=user.id,
            name=user.full_name,
            email=user.email,
            phone=user.phone,
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    return {
        "user": user,
        "client": client,
        "password": payload["password"],
        "email": payload["email"],
        "username": payload["username"],
    }


@pytest.fixture
def admin_account(db):
    return _create_user(db, role_id=1)


@pytest.fixture
def customer_account(db):
    return _create_user(db, role_id=3)


@pytest.fixture
def admin_token(admin_account):
    from app.core.security import create_access_token

    user = admin_account["user"]
    return create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
    )


@pytest.fixture
def customer_token(customer_account):
    from app.core.security import create_access_token

    user = customer_account["user"]
    return create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role,
        }
    )


@pytest.fixture
def sample_ot(db, customer_account):
    from app.services.repair_write_service import RepairWriteService

    slug = uuid.uuid4().hex[:8]
    client = customer_account["client"]
    repair = RepairWriteService(db).create_repair(
        {
            "client_id": client.id,
            "title": f"OT fixture {slug}",
            "description": f"Problema fixture {slug}",
            "payment_method": "transfer",
            "paid_amount": 15000,
        }
    )
    db.refresh(repair)
    return {
        "repair": repair,
        "repair_id": repair.id,
        "client": client,
        "user": customer_account["user"],
    }
