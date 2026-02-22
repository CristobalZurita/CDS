#!/usr/bin/env python3
"""
Normalize local SQLite schema for cirujano.db (aditivo).
Adds missing columns expected by the current models.

Uso: python backend/scripts/normalize_db.py
"""

import os
import sqlite3
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]


def _resolve_db_path() -> str:
    """
    Resuelve ruta DB privilegiando DATABASE_URL sqlite.
    Fallback seguro: backend/cirujano.db (DB operativa del backend).
    """
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url.startswith("sqlite:///"):
        raw_path = database_url.replace("sqlite:///", "", 1)
        if raw_path.startswith("/"):
            return raw_path
        return str((BACKEND_ROOT / raw_path).resolve())
    return str((BACKEND_ROOT / "cirujano.db").resolve())


DB_PATH = _resolve_db_path()


TABLE_COLUMNS = {
    "users": [
        ("two_factor_enabled", "INTEGER", "1"),
        ("two_factor_method", "TEXT", "'email'"),
    ],
    "clients": [
        ("customer_segment", "TEXT", "'regular'"),
        ("lifetime_value", "REAL", "0"),
        ("tax_id", "TEXT", None),
        ("company_name", "TEXT", None),
        ("billing_address", "TEXT", None),
        ("language_preference", "TEXT", "'es'"),
        ("service_preference", "TEXT", "'whatsapp'"),
        ("internal_notes", "TEXT", None),
    ],
    "repairs": [
        ("signature_ingreso_path", "TEXT", None),
        ("signature_retiro_path", "TEXT", None),
        ("archived_at", "TEXT", None),
        ("archived_by", "INTEGER", None),
        ("ot_parent_id", "INTEGER", None),
        ("ot_sequence", "INTEGER", None),
    ],
    "payments": [
        ("purchase_request_id", "INTEGER", None),
    ],
    "stock": [
        ("quantity_in_transit", "INTEGER", "0"),
        ("quantity_damaged", "INTEGER", "0"),
        ("quantity_in_work", "INTEGER", "0"),
        ("quantity_under_review", "INTEGER", "0"),
        ("quantity_internal_use", "INTEGER", "0"),
    ],
}

REPAIR_STATUSES = [
    (1, "ingreso", "Ingreso", "Ingreso del equipo", "#6c757d", 1),
    (2, "diagnostico", "Diagnóstico", "Diagnóstico inicial", "#17a2b8", 2),
    (3, "presupuesto", "Presupuesto", "Presupuesto informado", "#fd7e14", 3),
    (4, "aprobado", "Aprobado", "Presupuesto aprobado", "#28a745", 4),
    (5, "en_trabajo", "En trabajo", "Trabajo en curso", "#ff8c42", 5),
    (6, "listo", "Listo", "Listo para entrega", "#20c997", 6),
    (7, "entregado", "Entregado", "Entregado al cliente", "#198754", 7),
    (8, "noventena", "Noventena", "Garantía 90 días", "#4d77ff", 8),
    (9, "archivado", "Archivado", "Archivado", "#6f42c1", 9),
    (10, "rechazado", "Rechazado", "Rechazado por el cliente", "#dc3545", 10),
]

OT_CODE_PATTERN = re.compile(r"^CDS-\d{3}-OT-(\d{3})(?:-(\d{2}))?$")


def add_column(cur, table: str, name: str, col_type: str, default: str | None) -> None:
    if default is None:
        sql = f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"
    else:
        sql = f"ALTER TABLE {table} ADD COLUMN {name} {col_type} DEFAULT {default}"
    cur.execute(sql)


def ensure_index(cur, name: str, sql: str) -> None:
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='index' AND name=?", (name,))
    if cur.fetchone():
        return
    cur.execute(sql)
    print(f"✓ índice {name} creado")


def _derive_ot_group_assignment(repair_id: int, repair_number: str | None, valid_ids: set[int]) -> tuple[int, int]:
    """
    Deriva parent/sequence desde código OT legacy.
    Fallback: self + secuencia 1.
    """
    if repair_number:
        match = OT_CODE_PATTERN.match(str(repair_number).strip())
        if match:
            base_id = int(match.group(1))
            suffix = int(match.group(2)) if match.group(2) else 1
            if base_id in valid_ids:
                return base_id, max(suffix, 1)
    return repair_id, 1


def normalize_ot_group_fields(cur) -> None:
    """
    Completa ot_parent_id/ot_sequence en repairs de forma aditiva.
    """
    cur.execute(
        """
        SELECT id, repair_number, ot_parent_id, ot_sequence
        FROM repairs
        ORDER BY id ASC
        """
    )
    rows = cur.fetchall()
    valid_ids = {int(row[0]) for row in rows}
    used_sequences: dict[int, set[int]] = {}

    for row in rows:
        repair_id = int(row[0])
        repair_number = row[1]
        parent_id = row[2]
        sequence = row[3]

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
                repair_number=repair_number,
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
            cur.execute(
                """
                UPDATE repairs
                SET ot_parent_id = ?, ot_sequence = ?
                WHERE id = ?
                """,
                (candidate_parent, candidate_sequence, repair_id),
            )
            print(f"✓ repairs.id={repair_id} OT -> parent={candidate_parent}, seq={candidate_sequence}")


def bootstrap_stock_from_products(cur) -> None:
    """
    Crea filas stock faltantes para products (sin sobrescribir cantidades existentes).
    """
    cur.execute("SELECT id, quantity, min_quantity, price FROM products")
    products = cur.fetchall()
    created = 0
    updated = 0

    for product_id, quantity, min_quantity, price in products:
        cur.execute(
            """
            SELECT id, minimum_stock, unit_cost
            FROM stock
            WHERE component_table = 'products' AND component_id = ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (product_id,),
        )
        existing = cur.fetchone()
        if not existing:
            cur.execute(
                """
                INSERT INTO stock (
                    component_table,
                    component_id,
                    quantity,
                    quantity_reserved,
                    minimum_stock,
                    unit_cost
                ) VALUES ('products', ?, ?, 0, ?, ?)
                """,
                (
                    int(product_id),
                    int(quantity or 0),
                    int(min_quantity or 0),
                    float(price or 0),
                ),
            )
            created += 1
            continue

        stock_id, minimum_stock, unit_cost = existing
        patch_minimum = int(min_quantity or 0) if minimum_stock is None else minimum_stock
        patch_unit_cost = float(price or 0) if unit_cost is None else unit_cost
        if patch_minimum != minimum_stock or patch_unit_cost != unit_cost:
            cur.execute(
                """
                UPDATE stock
                SET minimum_stock = ?, unit_cost = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (patch_minimum, patch_unit_cost, stock_id),
            )
            updated += 1

    print(f"✓ stock bootstrap products: creados={created}, actualizados={updated}")


def normalize(db_path: str) -> None:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB no encontrada: {db_path}")

    print(f"DB objetivo: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for table, columns in TABLE_COLUMNS.items():
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cur.fetchone():
            print(f"⚠️  Tabla faltante: {table}")
            continue

        cur.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cur.fetchall()}
        for name, col_type, default in columns:
            if name in existing:
                continue
            add_column(cur, table, name, col_type, default)
            print(f"✓ {table}.{name} agregado")

    conn.commit()

    # Normalización OT group en repairs
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repairs'")
    if cur.fetchone():
        normalize_ot_group_fields(cur)
        conn.commit()

    # Índices OT/pagos/stock (aditivo)
    ensure_index(cur, "ix_repairs_ot_parent_id", "CREATE INDEX ix_repairs_ot_parent_id ON repairs (ot_parent_id)")
    ensure_index(
        cur,
        "uq_repairs_ot_parent_sequence",
        "CREATE UNIQUE INDEX uq_repairs_ot_parent_sequence ON repairs (ot_parent_id, ot_sequence)",
    )
    ensure_index(
        cur,
        "ix_payments_purchase_request_id",
        "CREATE INDEX ix_payments_purchase_request_id ON payments (purchase_request_id)",
    )
    ensure_index(
        cur,
        "ix_stock_component",
        "CREATE INDEX ix_stock_component ON stock (component_table, component_id)",
    )
    conn.commit()

    # Ensure repair_statuses exist (aditivo)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repair_statuses'")
    if cur.fetchone():
        for status in REPAIR_STATUSES:
            cur.execute(
                """
                INSERT OR IGNORE INTO repair_statuses (id, code, name, description, color, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                status
            )
        conn.commit()

    # Inicializar stock faltante para productos existentes
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    has_products = cur.fetchone() is not None
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock'")
    has_stock = cur.fetchone() is not None
    if has_products and has_stock:
        bootstrap_stock_from_products(cur)
        conn.commit()

    conn.close()


if __name__ == "__main__":
    normalize(DB_PATH)
    print("✅ Normalización completada")
