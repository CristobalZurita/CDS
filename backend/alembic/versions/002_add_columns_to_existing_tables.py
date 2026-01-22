"""Add columns to existing tables (Client, Appointment, Payment)

Revision ID: 002_aditivo
Revises: 001_aditivo
Create Date: 2026-01-20

ADITIVO: Solo agrega columnas, no modifica ni elimina existentes.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '002_aditivo'
down_revision: Union[str, None] = '001_aditivo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === CLIENTS TABLE - New columns ===
    # Solo añadir si no existen
    with op.batch_alter_table('clients') as batch_op:
        # Segmentación
        batch_op.add_column(sa.Column('customer_segment', sa.String(20), default='regular', nullable=True))
        batch_op.add_column(sa.Column('lifetime_value', sa.Float(), default=0.0, nullable=True))
        
        # Datos fiscales
        batch_op.add_column(sa.Column('tax_id', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('company_name', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('billing_address', sa.Text(), nullable=True))
        
        # Preferencias
        batch_op.add_column(sa.Column('language_preference', sa.String(10), default='es', nullable=True))
        batch_op.add_column(sa.Column('service_preference', sa.String(20), default='whatsapp', nullable=True))
        batch_op.add_column(sa.Column('internal_notes', sa.Text(), nullable=True))

    # === APPOINTMENTS TABLE - New columns ===
    with op.batch_alter_table('appointments') as batch_op:
        # Foreign keys
        batch_op.add_column(sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id', name='fk_appointments_client_id'), nullable=True))
        batch_op.add_column(sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id', name='fk_appointments_device_id'), nullable=True))
        batch_op.add_column(sa.Column('repair_id', sa.Integer(), sa.ForeignKey('repairs.id', name='fk_appointments_repair_id'), nullable=True))
        batch_op.add_column(sa.Column('technician_id', sa.Integer(), sa.ForeignKey('users.id', name='fk_appointments_technician_id'), nullable=True))
        
        # Tipo y duración
        batch_op.add_column(sa.Column('appointment_type', sa.String(30), default='reception', nullable=True))
        batch_op.add_column(sa.Column('duration_minutes', sa.Integer(), default=30, nullable=True))
        batch_op.add_column(sa.Column('fecha_fin', sa.DateTime(), nullable=True))
        
        # Recordatorios
        batch_op.add_column(sa.Column('reminder_sent_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('reminder_count', sa.Integer(), default=0, nullable=True))
        
        # Cancelación y reprogramación
        batch_op.add_column(sa.Column('cancellation_reason', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('cancelled_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('reschedule_count', sa.Integer(), default=0, nullable=True))
        batch_op.add_column(sa.Column('original_fecha', sa.DateTime(), nullable=True))
        
        # Metadata adicional
        batch_op.add_column(sa.Column('notes_internal', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('video_call_link', sa.String(500), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('status_history', sa.Text(), nullable=True))

    # === PAYMENTS TABLE - New columns ===
    with op.batch_alter_table('payments') as batch_op:
        # Invoice relation
        batch_op.add_column(sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id', name='fk_payments_invoice_id'), nullable=True))
        
        # Fechas
        batch_op.add_column(sa.Column('payment_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('payment_due_date', sa.DateTime(), nullable=True))
        
        # Reembolsos
        batch_op.add_column(sa.Column('refund_of_id', sa.Integer(), sa.ForeignKey('payments.id', name='fk_payments_refund_of_id'), nullable=True))
        
        # Procesador de pagos
        batch_op.add_column(sa.Column('payment_processor', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('processor_fee', sa.Integer(), default=0, nullable=True))
        
        # Moneda y pagos parciales
        batch_op.add_column(sa.Column('currency', sa.String(10), default='CLP', nullable=True))
        batch_op.add_column(sa.Column('partial_payment_of', sa.Integer(), nullable=True))

    # === Create indexes for new FKs ===
    op.create_index(op.f('ix_appointments_client_id'), 'appointments', ['client_id'], unique=False)
    op.create_index(op.f('ix_appointments_repair_id'), 'appointments', ['repair_id'], unique=False)
    op.create_index(op.f('ix_payments_invoice_id'), 'payments', ['invoice_id'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index(op.f('ix_payments_invoice_id'), table_name='payments')
    op.drop_index(op.f('ix_appointments_repair_id'), table_name='appointments')
    op.drop_index(op.f('ix_appointments_client_id'), table_name='appointments')

    # === PAYMENTS TABLE - Remove columns ===
    with op.batch_alter_table('payments') as batch_op:
        batch_op.drop_column('partial_payment_of')
        batch_op.drop_column('currency')
        batch_op.drop_column('processor_fee')
        batch_op.drop_column('payment_processor')
        batch_op.drop_column('refund_of_id')
        batch_op.drop_column('payment_due_date')
        batch_op.drop_column('payment_date')
        batch_op.drop_column('invoice_id')

    # === APPOINTMENTS TABLE - Remove columns ===
    with op.batch_alter_table('appointments') as batch_op:
        batch_op.drop_column('status_history')
        batch_op.drop_column('location')
        batch_op.drop_column('video_call_link')
        batch_op.drop_column('notes_internal')
        batch_op.drop_column('original_fecha')
        batch_op.drop_column('reschedule_count')
        batch_op.drop_column('cancelled_at')
        batch_op.drop_column('cancellation_reason')
        batch_op.drop_column('reminder_count')
        batch_op.drop_column('reminder_sent_at')
        batch_op.drop_column('fecha_fin')
        batch_op.drop_column('duration_minutes')
        batch_op.drop_column('appointment_type')
        batch_op.drop_column('technician_id')
        batch_op.drop_column('repair_id')
        batch_op.drop_column('device_id')
        batch_op.drop_column('client_id')

    # === CLIENTS TABLE - Remove columns ===
    with op.batch_alter_table('clients') as batch_op:
        batch_op.drop_column('internal_notes')
        batch_op.drop_column('service_preference')
        batch_op.drop_column('language_preference')
        batch_op.drop_column('billing_address')
        batch_op.drop_column('company_name')
        batch_op.drop_column('tax_id')
        batch_op.drop_column('lifetime_value')
        batch_op.drop_column('customer_segment')
