"""Add extra columns to clients table

Revision ID: 003_aditivo
Revises: 002_aditivo
Create Date: 2026-01-21

ADITIVO: Agrega columnas faltantes al modelo Client
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_aditivo'
down_revision: Union[str, None] = '002_aditivo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to clients table"""

    # Verificar y agregar cada columna solo si no existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('clients')]

    columns_to_add = [
        ('customer_segment', sa.String(20), 'regular'),
        ('lifetime_value', sa.Float, 0.0),
        ('tax_id', sa.String(50), None),
        ('company_name', sa.String(255), None),
        ('billing_address', sa.Text, None),
        ('language_preference', sa.String(10), 'es'),
        ('service_preference', sa.String(20), 'whatsapp'),
        ('internal_notes', sa.Text, None),
    ]

    for col_name, col_type, default_value in columns_to_add:
        if col_name not in existing_columns:
            if default_value is not None:
                op.add_column('clients', sa.Column(col_name, col_type, nullable=True, server_default=str(default_value)))
            else:
                op.add_column('clients', sa.Column(col_name, col_type, nullable=True))


def downgrade() -> None:
    """Remove added columns from clients table"""
    columns_to_remove = [
        'customer_segment',
        'lifetime_value',
        'tax_id',
        'company_name',
        'billing_address',
        'language_preference',
        'service_preference',
        'internal_notes',
    ]

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('clients')]

    for col_name in columns_to_remove:
        if col_name in existing_columns:
            op.drop_column('clients', col_name)
