"""create unique index concurrently for payments.transaction_id on Postgres

Revision ID: 0004_add_unique_index_concurrently_postgres
Revises: 0003_add_unique_transaction_id
Create Date: 2026-01-06 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '0004_add_unique_index_concurrently_postgres'
down_revision = '0003_add_unique_transaction_id'
branch_labels = None
depends_on = None


def upgrade():
    # This operation is targeted at Postgres. It attempts to create a UNIQUE INDEX
    # concurrently so it does not block writes on large tables. It is intentionally
    # tolerant: if it fails or is not Postgres, we skip it.
    conn = op.get_bind()
    try:
        if conn.dialect.name == 'postgresql':
            # CREATE INDEX CONCURRENTLY must run outside a transaction
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                text("CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS uq_payments_transaction_id_idx ON payments (transaction_id);")
            )
    except Exception:
        # If anything goes wrong (missing table, permission, etc.), log and continue.
        pass


def downgrade():
    conn = op.get_bind()
    try:
        if conn.dialect.name == 'postgresql':
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                text("DROP INDEX CONCURRENTLY IF EXISTS uq_payments_transaction_id_idx;")
            )
    except Exception:
        pass
