"""Migration script template.

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
from alembic import context

def upgrade():
    # This initial migration will create all tables defined in models by calling
    # SQLAlchemy's Base.metadata.create_all(). This is a pragmatic initial step
    # to ensure tests and dev environments can apply schema quickly.
    from backend.app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)


def downgrade():
    from backend.app.core.database import Base, engine
    Base.metadata.drop_all(bind=engine)
