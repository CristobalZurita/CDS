"""Add quote items and recipients tables (aditivo)

Revision ID: 009_add_quote_items_and_recipients
Revises: 008_add_ot_group_columns_to_repairs
Create Date: 2026-02-20 12:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "009_add_quote_items_and_recipients"
down_revision = "008_add_ot_group_columns_to_repairs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "quote_items" not in existing_tables:
        op.create_table(
            "quote_items",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column("quote_id", sa.Integer(), sa.ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("item_type", sa.String(length=32), nullable=False, server_default="service"),
            sa.Column("sku", sa.String(length=120), nullable=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("quantity", sa.Float(), nullable=False, server_default="1"),
            sa.Column("unit_price", sa.Float(), nullable=False, server_default="0"),
            sa.Column("line_total", sa.Float(), nullable=False, server_default="0"),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("source_table", sa.String(length=64), nullable=True),
            sa.Column("source_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )

    if "quote_recipients" not in existing_tables:
        op.create_table(
            "quote_recipients",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column("quote_id", sa.Integer(), sa.ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )

    inspector = sa.inspect(bind)
    quote_items_indexes = {idx["name"] for idx in inspector.get_indexes("quote_items")} if "quote_items" in inspector.get_table_names() else set()
    quote_recipients_indexes = {idx["name"] for idx in inspector.get_indexes("quote_recipients")} if "quote_recipients" in inspector.get_table_names() else set()

    if "ix_quote_items_quote_id" not in quote_items_indexes:
        op.create_index("ix_quote_items_quote_id", "quote_items", ["quote_id"], unique=False)
    if "ix_quote_recipients_quote_id" not in quote_recipients_indexes:
        op.create_index("ix_quote_recipients_quote_id", "quote_recipients", ["quote_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "quote_recipients" in existing_tables:
        try:
            op.drop_index("ix_quote_recipients_quote_id", table_name="quote_recipients")
        except Exception:
            pass
        op.drop_table("quote_recipients")

    if "quote_items" in existing_tables:
        try:
            op.drop_index("ix_quote_items_quote_id", table_name="quote_items")
        except Exception:
            pass
        op.drop_table("quote_items")
