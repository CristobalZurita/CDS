import os
import asyncio
import inspect
from pathlib import Path
import logging
import pytest
from alembic.config import Config
from alembic import command
import sqlalchemy

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
TEST_DB_PATH = Path(os.getenv("TEST_DB_PATH", str(Path(__file__).resolve().parent / "test_cirujano.db")))
os.environ.setdefault("TEST_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_REFRESH_SECRET", "test-refresh-secret")


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
    from app.core.database import Base
    from app import models  # noqa: F401

    engine = _rebind_session(db_url)
    Base.metadata.create_all(bind=engine)
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
    here = os.path.dirname(os.path.dirname(__file__))
    alembic_cfg = Config(os.path.join(here, '..', 'alembic.ini'))
    alembic_cfg.set_main_option('script_location', os.path.join(here, '..', 'alembic'))
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
