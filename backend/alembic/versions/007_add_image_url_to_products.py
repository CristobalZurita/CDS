"""Add image_url field to products table for inventory photo management

Revision ID: 007_add_image_url_to_products
Revises: 006_add_instrument_templates_photos
Create Date: 2026-02-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '007_add_image_url_to_products'
down_revision = '006_add_instrument_templates_photos'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add image_url column to products table"""
    op.add_column('products', sa.Column('image_url', sa.String(500), nullable=True))
    op.create_index('ix_products_image_url', 'products', ['image_url'])


def downgrade() -> None:
    """Remove image_url column from products table"""
    op.drop_index('ix_products_image_url', table_name='products')
    op.drop_column('products', 'image_url')
