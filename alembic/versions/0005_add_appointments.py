"""Add Appointments table

Revision ID: 0005_add_appointments
Revises: 0004_add_unique_index_concurrently_postgres
Create Date: 2026-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '0005_add_appointments'
down_revision = '0004_add_unique_index_concurrently_postgres'
branch_labels = None
depends_on = None


def upgrade():
    # Create appointments table
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('telefono', sa.String(20), nullable=False),
        sa.Column('fecha', sa.DateTime(), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=True),
        sa.Column('estado', sa.String(50), default='pendiente', nullable=False),
        sa.Column('google_calendar_id', sa.String(255), nullable=True),
        sa.Column('notificacion_enviada', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_appointments_id', 'appointments', ['id'])
    op.create_index('ix_appointments_nombre', 'appointments', ['nombre'])
    op.create_index('ix_appointments_email', 'appointments', ['email'])
    op.create_index('ix_appointments_fecha', 'appointments', ['fecha'])
    op.create_index('ix_appointments_estado', 'appointments', ['estado'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_appointments_estado', table_name='appointments')
    op.drop_index('ix_appointments_fecha', table_name='appointments')
    op.drop_index('ix_appointments_email', table_name='appointments')
    op.drop_index('ix_appointments_nombre', table_name='appointments')
    op.drop_index('ix_appointments_id', table_name='appointments')
    
    # Drop table
    op.drop_table('appointments')
