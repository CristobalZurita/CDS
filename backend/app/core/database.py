"""
Database configuration and session management
SQLAlchemy async engine and session factory with connection pooling
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy base class for ORM models
Base = declarative_base()

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
    poolclass=QueuePool,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def get_db():
    """
    Dependency to get database session
    Usage: from fastapi import Depends
           async def my_endpoint(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    try:
        # Create all tables from models (sync operation)
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"✗ Error creating database tables: {e}")
        raise


async def close_db():
    """
    Close database connection
    Call this on application shutdown
    """
    try:
        # Dispose of engine connections
        engine.dispose()
        logger.info("✓ Database connection closed")
    except Exception as e:
        logger.error(f"✗ Error closing database: {e}")
