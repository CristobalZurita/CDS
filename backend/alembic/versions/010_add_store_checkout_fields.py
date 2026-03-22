"""Add store checkout fields to leads and purchase_requests

Revision ID: 010_store_checkout
Revises: 8dc1d435ed91
Create Date: 2026-03-21

Cambios:
  leads              — email_verified, verification_token, verification_token_expires_at
  purchase_requests  — lead_id FK
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "010_store_checkout"
down_revision: Union[str, None] = "8dc1d435ed91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # ── leads ────────────────────────────────────────────────────────────────
    lead_cols = [c["name"] for c in inspector.get_columns("leads")]

    if "email_verified" not in lead_cols:
        op.add_column("leads", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="0"))
    if "verification_token" not in lead_cols:
        op.add_column("leads", sa.Column("verification_token", sa.String(length=128), nullable=True))
    if "verification_token_expires_at" not in lead_cols:
        op.add_column("leads", sa.Column("verification_token_expires_at", sa.DateTime(), nullable=True))

    # Índice único en verification_token (puede ser NULL, solo indexa valores no nulos)
    existing_indexes = [i["name"] for i in inspector.get_indexes("leads")]
    if "ix_leads_verification_token" not in existing_indexes:
        op.create_index("ix_leads_verification_token", "leads", ["verification_token"], unique=True)

    # ── purchase_requests ────────────────────────────────────────────────────
    pr_cols = [c["name"] for c in inspector.get_columns("purchase_requests")]

    if "lead_id" not in pr_cols:
        # SQLite no soporta ADD COLUMN con FK constraint — se omite el constraint
        # (SQLite no enforza FKs a menos que se active PRAGMA foreign_keys, el modelo ORM lo maneja)
        op.add_column(
            "purchase_requests",
            sa.Column("lead_id", sa.Integer(), nullable=True),
        )
        op.create_index("ix_purchase_requests_lead_id", "purchase_requests", ["lead_id"], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    pr_cols = [c["name"] for c in inspector.get_columns("purchase_requests")]
    if "lead_id" in pr_cols:
        op.drop_index("ix_purchase_requests_lead_id", table_name="purchase_requests")
        op.drop_column("purchase_requests", "lead_id")

    lead_cols = [c["name"] for c in inspector.get_columns("leads")]
    existing_indexes = [i["name"] for i in inspector.get_indexes("leads")]
    if "ix_leads_verification_token" in existing_indexes:
        op.drop_index("ix_leads_verification_token", table_name="leads")
    if "verification_token_expires_at" in lead_cols:
        op.drop_column("leads", "verification_token_expires_at")
    if "verification_token" in lead_cols:
        op.drop_column("leads", "verification_token")
    if "email_verified" in lead_cols:
        op.drop_column("leads", "email_verified")
