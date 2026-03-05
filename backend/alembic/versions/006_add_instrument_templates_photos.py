"""add instrument template fields and instrument_photos table

Revision ID: 006_add_instrument_templates_photos
Revises: 005_aditivo
Create Date: 2026-01-29
"""

from alembic import op
import sqlalchemy as sa


revision = "006_add_instrument_templates_photos"
down_revision = "005_aditivo"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("instruments", sa.Column("photo_base_url", sa.String(length=512), nullable=True))
    op.add_column("instruments", sa.Column("template_json", sa.JSON(), nullable=True))
    op.add_column("instruments", sa.Column("mapping_status", sa.String(length=50), nullable=True))
    op.add_column("instruments", sa.Column("family", sa.String(length=50), nullable=True))

    op.create_table(
        "instrument_photos",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id"), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_instrument_photos_instrument_id", "instrument_photos", ["instrument_id"])


def downgrade():
    op.drop_index("ix_instrument_photos_instrument_id", table_name="instrument_photos")
    op.drop_table("instrument_photos")

    op.drop_column("instruments", "family")
    op.drop_column("instruments", "mapping_status")
    op.drop_column("instruments", "template_json")
    op.drop_column("instruments", "photo_base_url")
