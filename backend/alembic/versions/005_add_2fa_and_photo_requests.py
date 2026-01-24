"""Add 2FA and photo upload requests (ADITIVO)

Revision ID: 005_aditivo
Revises: 004_aditivo
Create Date: 2026-01-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005_aditivo"
down_revision: Union[str, None] = "004_aditivo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # user 2fa columns
    user_cols = [c["name"] for c in inspector.get_columns("users")]
    if "two_factor_enabled" not in user_cols:
        op.add_column("users", sa.Column("two_factor_enabled", sa.Integer(), nullable=True, server_default="1"))
    if "two_factor_method" not in user_cols:
        op.add_column("users", sa.Column("two_factor_method", sa.String(length=20), nullable=True, server_default="email"))

    # two_factor_codes table
    if "two_factor_codes" not in inspector.get_table_names():
        op.create_table(
            "two_factor_codes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("code", sa.String(length=10), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_two_factor_codes_user_id", "two_factor_codes", ["user_id"])

    # photo_upload_requests table
    if "photo_upload_requests" not in inspector.get_table_names():
        op.create_table(
            "photo_upload_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("repair_id", sa.Integer(), sa.ForeignKey("repairs.id"), nullable=False),
            sa.Column("token", sa.String(length=255), nullable=False, unique=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("photo_type", sa.String(length=30), nullable=True),
            sa.Column("caption", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_photo_upload_requests_token", "photo_upload_requests", ["token"], unique=True)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "photo_upload_requests" in inspector.get_table_names():
        op.drop_table("photo_upload_requests")
    if "two_factor_codes" in inspector.get_table_names():
        op.drop_table("two_factor_codes")
