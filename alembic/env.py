from __future__ import with_statement
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app.core.database import Base
from backend.app.core.database import engine
from backend.app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging. Be tolerant of missing logger sections
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception:
        # Some environments (tests) may not have full logging sections in alembic.ini;
        # continue without applying file-based logging configuration.
        pass

# set sqlalchemy.url from settings at runtime
config.set_main_option('sqlalchemy.url', settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
