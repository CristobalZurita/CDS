import os
import pytest

from alembic.config import Config
from alembic import command
import sqlalchemy
import os
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """Apply Alembic migrations before running tests."""
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
    yield
    # No teardown: keep schema for inspection; tests should clean data if needed
