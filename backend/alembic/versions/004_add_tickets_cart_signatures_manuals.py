"""Add tickets, purchase requests, signatures, manuals (ADITIVO)

Revision ID: 004_aditivo
Revises: 003_aditivo
Create Date: 2026-01-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_aditivo"
down_revision: Union[str, None] = "003_aditivo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Add signature columns to repairs if missing
    repair_cols = [c["name"] for c in inspector.get_columns("repairs")]
    if "signature_ingreso_path" not in repair_cols:
        op.add_column("repairs", sa.Column("signature_ingreso_path", sa.Text(), nullable=True))
    if "signature_retiro_path" not in repair_cols:
        op.add_column("repairs", sa.Column("signature_retiro_path", sa.Text(), nullable=True))

    # signature_requests
    if "signature_requests" not in inspector.get_table_names():
        op.create_table(
            "signature_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("repair_id", sa.Integer(), sa.ForeignKey("repairs.id"), nullable=False),
            sa.Column("request_type", sa.String(length=20), nullable=False),
            sa.Column("token", sa.String(length=255), nullable=False, unique=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("signed_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("signed_ip", sa.String(length=64), nullable=True),
            sa.Column("signed_user_agent", sa.String(length=255), nullable=True),
        )
        op.create_index("ix_signature_requests_token", "signature_requests", ["token"], unique=True)

    # tickets
    if "tickets" not in inspector.get_table_names():
        op.create_table(
            "tickets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=True),
            sa.Column("repair_id", sa.Integer(), sa.ForeignKey("repairs.id"), nullable=True),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("subject", sa.String(length=255), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
            sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_tickets_client_id", "tickets", ["client_id"])
        op.create_index("ix_tickets_repair_id", "tickets", ["repair_id"])

    if "ticket_messages" not in inspector.get_table_names():
        op.create_table(
            "ticket_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id"), nullable=False),
            sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_ticket_messages_ticket_id", "ticket_messages", ["ticket_id"])

    # purchase_requests
    if "purchase_requests" not in inspector.get_table_names():
        op.create_table(
            "purchase_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=True),
            sa.Column("repair_id", sa.Integer(), sa.ForeignKey("repairs.id"), nullable=True),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_purchase_requests_client_id", "purchase_requests", ["client_id"])
        op.create_index("ix_purchase_requests_repair_id", "purchase_requests", ["repair_id"])

    if "purchase_request_items" not in inspector.get_table_names():
        op.create_table(
            "purchase_request_items",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("request_id", sa.Integer(), sa.ForeignKey("purchase_requests.id"), nullable=False),
            sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
            sa.Column("sku", sa.String(length=120), nullable=True),
            sa.Column("name", sa.String(length=255), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("unit_price", sa.Float(), nullable=False, server_default="0"),
            sa.Column("external_url", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="suggested"),
        )
        op.create_index("ix_purchase_request_items_request_id", "purchase_request_items", ["request_id"])

    # manuals
    if "manual_documents" not in inspector.get_table_names():
        op.create_table(
            "manual_documents",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("source", sa.String(length=50), nullable=False, server_default="internal"),
            sa.Column("url", sa.String(length=500), nullable=True),
            sa.Column("file_path", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_manual_documents_instrument_id", "manual_documents", ["instrument_id"])


def downgrade() -> None:
    # Drop tables if they exist
    for table in ["manual_documents", "purchase_request_items", "purchase_requests", "ticket_messages", "tickets", "signature_requests"]:
        if table in sa.inspect(op.get_bind()).get_table_names():
            op.drop_table(table)
