"""Add progress_last_viewed_at to repairs

Revision ID: 011_repair_progress_viewed
Revises: 010_store_checkout
Create Date: 2026-03-22

Cambios:
  repairs — progress_last_viewed_at (DateTime, nullable)
            Flag de lectura: cuándo el cliente vio por última vez el progreso de su OT.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "011_repair_progress_viewed"
down_revision: Union[str, None] = "010_store_checkout"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "repairs",
        sa.Column("progress_last_viewed_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("repairs", "progress_last_viewed_at")
