"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create all tables defined in SQLAlchemy metadata
    from backend.app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)


def downgrade():
    from backend.app.core.database import Base, engine
    Base.metadata.drop_all(bind=engine)
