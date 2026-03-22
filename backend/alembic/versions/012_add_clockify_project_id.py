"""Add clockify_project_id to repairs

Revision ID: 012_clockify_project_id
Revises: 011_repair_progress_viewed
Create Date: 2026-03-22
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "012_clockify_project_id"
down_revision: Union[str, None] = "011_repair_progress_viewed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "repairs",
        sa.Column("clockify_project_id", sa.String(), nullable=True),
    )
    with op.batch_alter_table("repairs") as batch_op:
        batch_op.create_index("ix_repairs_clockify_project_id", ["clockify_project_id"])


def downgrade() -> None:
    with op.batch_alter_table("repairs") as batch_op:
        batch_op.drop_index("ix_repairs_clockify_project_id")
    op.drop_column("repairs", "clockify_project_id")
