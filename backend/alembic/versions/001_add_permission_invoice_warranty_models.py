"""Add Permission, Invoice, and Warranty models

Revision ID: 001_aditivo
Revises: None
Create Date: 2026-01-20

ADITIVO: Solo agrega tablas nuevas, no modifica existentes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '001_aditivo'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === PERMISSIONS TABLE ===
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resource', sa.String(50), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)

    # === ROLES TABLE ===
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)

    # === ROLE_PERMISSIONS (Many-to-Many) ===
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), primary_key=True),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )

    # === USER_ROLE_ASSIGNMENTS (Many-to-Many) ===
    op.create_table(
        'user_role_assignments',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )

    # === INVOICE_SEQUENCES TABLE ===
    op.create_table(
        'invoice_sequences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prefix', sa.String(10), nullable=False, unique=True),
        sa.Column('last_number', sa.Integer(), default=0),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )

    # === INVOICES TABLE ===
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('invoice_type', sa.String(20), default='invoice'),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=True),
        sa.Column('repair_id', sa.Integer(), sa.ForeignKey('repairs.id'), nullable=True),
        
        # Montos (en centavos)
        sa.Column('subtotal', sa.Integer(), default=0),
        sa.Column('tax_rate', sa.Float(), default=19.0),
        sa.Column('tax_amount', sa.Integer(), default=0),
        sa.Column('discount', sa.Integer(), default=0),
        sa.Column('total', sa.Integer(), default=0),
        sa.Column('amount_paid', sa.Integer(), default=0),
        sa.Column('amount_due', sa.Integer(), default=0),
        
        # Fechas
        sa.Column('issue_date', sa.DateTime(), default=datetime.utcnow),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('viewed_at', sa.DateTime(), nullable=True),
        sa.Column('voided_at', sa.DateTime(), nullable=True),
        
        # Metadatos
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('payment_terms', sa.String(255), nullable=True),
        sa.Column('void_reason', sa.String(255), nullable=True),
        
        # Auditoría
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_client_id'), 'invoices', ['client_id'], unique=False)
    op.create_index(op.f('ix_invoices_repair_id'), 'invoices', ['repair_id'], unique=False)

    # === INVOICE_ITEMS TABLE ===
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('quantity', sa.Float(), default=1),
        sa.Column('unit', sa.String(20), default='u'),
        sa.Column('unit_price', sa.Integer(), default=0),
        sa.Column('discount', sa.Integer(), default=0),
        sa.Column('total', sa.Integer(), default=0),
        sa.Column('item_type', sa.String(20), default='service'),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('component_table', sa.String(50), nullable=True),
        sa.Column('component_id', sa.Integer(), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_items_invoice_id'), 'invoice_items', ['invoice_id'], unique=False)

    # === WARRANTIES TABLE ===
    op.create_table(
        'warranties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warranty_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('repair_id', sa.Integer(), sa.ForeignKey('repairs.id'), nullable=False, unique=True),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=True),
        
        # Tipo y duración
        sa.Column('warranty_type', sa.String(20), default='full'),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('duration_days', sa.Integer(), default=90),
        
        # Fechas
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('voided_at', sa.DateTime(), nullable=True),
        
        # Cobertura
        sa.Column('coverage_description', sa.Text(), nullable=True),
        sa.Column('exclusions', sa.Text(), nullable=True),
        sa.Column('max_claim_amount', sa.Integer(), default=0),
        sa.Column('max_claims', sa.Integer(), default=1),
        sa.Column('claims_used', sa.Integer(), default=0),
        
        # Auditoría
        sa.Column('void_reason', sa.String(255), nullable=True),
        sa.Column('voided_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warranties_id'), 'warranties', ['id'], unique=False)
    op.create_index(op.f('ix_warranties_repair_id'), 'warranties', ['repair_id'], unique=False)
    op.create_index(op.f('ix_warranties_client_id'), 'warranties', ['client_id'], unique=False)

    # === WARRANTY_CLAIMS TABLE ===
    op.create_table(
        'warranty_claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('claim_number', sa.String(50), unique=True, nullable=False),
        sa.Column('warranty_id', sa.Integer(), sa.ForeignKey('warranties.id'), nullable=False),
        sa.Column('status', sa.String(20), default='submitted'),
        
        # Detalles del reclamo
        sa.Column('problem_description', sa.Text(), nullable=False),
        sa.Column('fault_type', sa.String(50), nullable=True),
        sa.Column('is_covered', sa.Boolean(), nullable=True),
        sa.Column('rejection_reason', sa.String(500), nullable=True),
        
        # Evaluación
        sa.Column('evaluation_notes', sa.Text(), nullable=True),
        sa.Column('evaluated_at', sa.DateTime(), nullable=True),
        sa.Column('evaluated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        
        # Costos
        sa.Column('estimated_cost', sa.Integer(), default=0),
        sa.Column('actual_cost', sa.Integer(), default=0),
        sa.Column('customer_copay', sa.Integer(), default=0),
        
        # Reparación de garantía
        sa.Column('new_repair_id', sa.Integer(), sa.ForeignKey('repairs.id'), nullable=True),
        
        # Fechas
        sa.Column('submitted_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        
        # Auditoría
        sa.Column('submitted_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warranty_claims_warranty_id'), 'warranty_claims', ['warranty_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('warranty_claims')
    op.drop_table('warranties')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_table('invoice_sequences')
    op.drop_table('user_role_assignments')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions')
