"""initial_baseline_empty

Revision ID: 78b5056b2086
Revises:
Create Date: 2026-01-16 12:40:10.966659

Initial baseline migration for existing database.
This migration represents the state of the database schema
as of FASE 8 implementation. The database was created manually
and this migration serves as the starting point for Alembic
to track future schema changes.

All existing tables are assumed to be present:
- users, user_roles
- instruments, brands, categories
- repairs, diagnostics, payments
- products, stock, stock_movements
- clients, devices, quotes
- tools, storage_locations
- appointments, audit_logs
- And various lookup tables (device_brands, device_types, etc.)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78b5056b2086'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
