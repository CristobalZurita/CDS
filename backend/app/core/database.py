"""
Database configuration and session management
SQLAlchemy async engine and session factory with connection pooling
"""

import re

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy base class for ORM models
Base = declarative_base()

# Create engine with connection pooling
# SQLite needs check_same_thread=False; PostgreSQL does not accept it.
_is_sqlite = settings.database_url.startswith("sqlite")
_connect_args: dict = {"check_same_thread": False, "timeout": 30} if _is_sqlite else {}
_pool_kwargs: dict = (
    {"poolclass": QueuePool, "pool_size": 10, "max_overflow": 20}
    if not _is_sqlite
    else {}
)

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args=_connect_args,
    **_pool_kwargs,
)

# TEMPO MAESTRO: Force UTC on every PostgreSQL connection.
# This ensures the DB "master clock" always ticks in UTC regardless of
# the server's local timezone setting.  SQLite ignores this (no SET).
if not _is_sqlite:
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _set_timezone_utc(dbapi_conn, connection_record):
        with dbapi_conn.cursor() as cur:
            cur.execute("SET timezone = 'UTC'")

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

_OT_CODE_PATTERN = re.compile(r"^CDS-\d{3}-OT-(\d{3})(?:-(\d{2}))?$")


def _derive_ot_group_assignment(repair_id: int, repair_number: str | None, valid_ids: set[int]) -> tuple[int, int]:
    """
    Deriva parent/sequence OT desde código legacy.
    Fallback seguro: self + secuencia 1.
    """
    if repair_number:
        match = _OT_CODE_PATTERN.match(str(repair_number).strip())
        if match:
            base_id = int(match.group(1))
            suffix = int(match.group(2)) if match.group(2) else 1
            if base_id in valid_ids:
                return base_id, max(suffix, 1)
    return repair_id, 1


def _ensure_repairs_ot_schema() -> None:
    """
    Ajuste aditivo para DBs existentes sin columnas OT.
    Evita romper entornos legacy que usan create_all sin migraciones.
    """
    inspector = inspect(engine)
    if "repairs" not in inspector.get_table_names():
        return

    current_columns = {column["name"] for column in inspector.get_columns("repairs")}

    with engine.begin() as conn:
        if "ot_parent_id" not in current_columns:
            conn.execute(text("ALTER TABLE repairs ADD COLUMN ot_parent_id INTEGER"))
        if "ot_sequence" not in current_columns:
            conn.execute(text("ALTER TABLE repairs ADD COLUMN ot_sequence INTEGER"))

    inspector = inspect(engine)
    current_columns = {column["name"] for column in inspector.get_columns("repairs")}
    if "ot_parent_id" not in current_columns or "ot_sequence" not in current_columns:
        return

    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, repair_number, ot_parent_id, ot_sequence
                FROM repairs
                ORDER BY id ASC
                """
            )
        ).mappings().all()

        valid_ids = {int(row["id"]) for row in rows}
        used_sequences: dict[int, set[int]] = {}

        for row in rows:
            repair_id = int(row["id"])
            parent_id = row.get("ot_parent_id")
            sequence = row.get("ot_sequence")

            if parent_id is not None and sequence is not None:
                try:
                    candidate_parent = int(parent_id)
                    candidate_sequence = int(sequence)
                except (TypeError, ValueError):
                    candidate_parent = repair_id
                    candidate_sequence = 1
            else:
                candidate_parent, candidate_sequence = _derive_ot_group_assignment(
                    repair_id=repair_id,
                    repair_number=row.get("repair_number"),
                    valid_ids=valid_ids,
                )

            if candidate_parent not in valid_ids:
                candidate_parent = repair_id
            if candidate_sequence <= 0:
                candidate_sequence = 1

            reserved = used_sequences.setdefault(candidate_parent, set())
            while candidate_sequence in reserved:
                candidate_sequence += 1
            reserved.add(candidate_sequence)

            if parent_id != candidate_parent or sequence != candidate_sequence:
                conn.execute(
                    text(
                        """
                        UPDATE repairs
                        SET ot_parent_id = :parent_id,
                            ot_sequence = :ot_sequence
                        WHERE id = :repair_id
                        """
                    ),
                    {
                        "parent_id": candidate_parent,
                        "ot_sequence": candidate_sequence,
                        "repair_id": repair_id,
                    },
                )

    inspector = inspect(engine)
    existing_indexes = {index["name"] for index in inspector.get_indexes("repairs")}

    with engine.begin() as conn:
        if "ix_repairs_ot_parent_id" not in existing_indexes:
            conn.execute(text("CREATE INDEX ix_repairs_ot_parent_id ON repairs (ot_parent_id)"))
        if "uq_repairs_ot_parent_sequence" not in existing_indexes:
            conn.execute(
                text(
                    """
                    CREATE UNIQUE INDEX uq_repairs_ot_parent_sequence
                    ON repairs (ot_parent_id, ot_sequence)
                    """
                )
            )


def _ensure_payments_purchase_request_schema() -> None:
    """
    Ajuste aditivo para alinear payments legacy con el modelo actual.
    Compatible con DBs existentes sin migraciones.
    """
    inspector = inspect(engine)
    if "payments" not in inspector.get_table_names():
        return

    current_columns = {column["name"] for column in inspector.get_columns("payments")}
    additions = {
        "invoice_id": "INTEGER",
        "purchase_request_id": "INTEGER",
        "payment_date": "DATETIME",
        "payment_due_date": "DATETIME",
        "refund_of_id": "INTEGER",
        "payment_processor": "VARCHAR(50)",
        "processor_fee": "INTEGER DEFAULT 0",
        "currency": "VARCHAR(3) DEFAULT 'CLP'",
        "partial_payment_of": "INTEGER",
    }
    with engine.begin() as conn:
        for column_name, column_def in additions.items():
            if column_name not in current_columns:
                conn.execute(text(f"ALTER TABLE payments ADD COLUMN {column_name} {column_def}"))

    inspector = inspect(engine)
    existing_indexes = {index["name"] for index in inspector.get_indexes("payments")}
    with engine.begin() as conn:
        if "ix_payments_invoice_id" not in existing_indexes:
            conn.execute(text("CREATE INDEX ix_payments_invoice_id ON payments (invoice_id)"))
        if "ix_payments_purchase_request_id" not in existing_indexes:
            conn.execute(text("CREATE INDEX ix_payments_purchase_request_id ON payments (purchase_request_id)"))


def _ensure_products_image_url_schema() -> None:
    """
    Ajuste aditivo para DBs legacy sin products.image_url.
    Evita que el ORM falle al seleccionar Product en inventario/stats.
    """
    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        return

    current_columns = {column["name"] for column in inspector.get_columns("products")}
    if "image_url" in current_columns:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)"))


def _ensure_appointments_schema() -> None:
    """
    Ajuste aditivo para DBs legacy sin columnas nuevas en appointments.
    Evita que el ORM falle al cargar el módulo admin de citas.
    """
    inspector = inspect(engine)
    if "appointments" not in inspector.get_table_names():
        return

    current_columns = {column["name"] for column in inspector.get_columns("appointments")}
    additions = {
        "client_id": "INTEGER",
        "device_id": "INTEGER",
        "repair_id": "INTEGER",
        "technician_id": "INTEGER",
        "appointment_type": "VARCHAR(30) DEFAULT 'consultation'",
        "duration_minutes": "INTEGER DEFAULT 30",
        "fecha_fin": "DATETIME",
        "reminder_sent_at": "DATETIME",
        "reminder_count": "INTEGER DEFAULT 0",
        "cancellation_reason": "TEXT",
        "cancelled_at": "DATETIME",
        "reschedule_count": "INTEGER DEFAULT 0",
        "original_fecha": "DATETIME",
        "notes_internal": "TEXT",
        "video_call_link": "VARCHAR(500)",
        "location": "VARCHAR(255)",
        "status_history": "TEXT",
    }

    with engine.begin() as conn:
        for column_name, column_ddl in additions.items():
            if column_name in current_columns:
                continue
            conn.execute(text(f"ALTER TABLE appointments ADD COLUMN {column_name} {column_ddl}"))


def _ensure_instruments_schema() -> None:
    """
    Ajuste aditivo para DBs legacy sin columnas nuevas en instruments.
    Evita que el módulo admin/manuales falle al consultar el catálogo.
    """
    inspector = inspect(engine)
    if "instruments" not in inspector.get_table_names():
        return

    current_columns = {column["name"] for column in inspector.get_columns("instruments")}
    additions = {
        "photo_base_url": "VARCHAR(512)",
        "template_json": "JSON",
        "mapping_status": "VARCHAR(50)",
        "family": "VARCHAR(50)",
    }

    with engine.begin() as conn:
        for column_name, column_ddl in additions.items():
            if column_name in current_columns:
                continue
            conn.execute(text(f"ALTER TABLE instruments ADD COLUMN {column_name} {column_ddl}"))


def _ensure_purchase_request_items_schema() -> None:
    """
    Ajuste aditivo para DBs legacy sin columnas de reserva en purchase_request_items.
    Permite conectar tienda/inventario sin migraciones destructivas.
    """
    inspector = inspect(engine)
    if "purchase_request_items" not in inspector.get_table_names():
        return

    current_columns = {column["name"] for column in inspector.get_columns("purchase_request_items")}
    additions = {
        "reserved_quantity": "INTEGER DEFAULT 0",
    }

    with engine.begin() as conn:
        for column_name, column_ddl in additions.items():
            if column_name in current_columns:
                continue
            conn.execute(text(f"ALTER TABLE purchase_request_items ADD COLUMN {column_name} {column_ddl}"))

async def get_db():
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
        # Ensure models are imported so SQLAlchemy registers tables
        from app import models  # noqa: F401
        # Create all tables from models (sync operation)
        Base.metadata.create_all(bind=engine)
        _ensure_repairs_ot_schema()
        _ensure_payments_purchase_request_schema()
        _ensure_products_image_url_schema()
        _ensure_appointments_schema()
        _ensure_instruments_schema()
        _ensure_purchase_request_items_schema()
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
