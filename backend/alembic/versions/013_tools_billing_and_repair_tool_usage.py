"""Add billing fields to tools and create repair_tool_usage

Revision ID: 013_tools_billing
Revises: 012_clockify_project_id
Create Date: 2026-03-22
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = "013_tools_billing"
down_revision: Union[str, None] = "012_clockify_project_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar campos de cobro a tools
    with op.batch_alter_table("tools") as batch_op:
        batch_op.add_column(sa.Column("rate_type", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("rate_value_clp", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("watts", sa.Float(), nullable=True))

    # Crear tabla de uso de herramientas por OT
    op.create_table(
        "repair_tool_usage",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("repair_id", sa.Integer(), sa.ForeignKey("repairs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("usage_minutes", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("unit_cost_clp", sa.Float(), nullable=True),
        sa.Column("charged_amount_clp", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_repair_tool_usage_repair_id", "repair_tool_usage", ["repair_id"])
    op.create_index("ix_repair_tool_usage_tool_id", "repair_tool_usage", ["tool_id"])


def downgrade() -> None:
    op.drop_index("ix_repair_tool_usage_tool_id", "repair_tool_usage")
    op.drop_index("ix_repair_tool_usage_repair_id", "repair_tool_usage")
    op.drop_table("repair_tool_usage")

    with op.batch_alter_table("tools") as batch_op:
        batch_op.drop_column("watts")
        batch_op.drop_column("rate_value_clp")
        batch_op.drop_column("rate_type")
