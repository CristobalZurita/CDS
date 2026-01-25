#!/usr/bin/env python3
"""
Normalize local SQLite schema for cirujano.db (aditivo).
Adds missing columns expected by the current models.

Uso: python backend/scripts/normalize_db.py
"""

import os
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = os.getenv("DATABASE_URL", "").replace("sqlite:///", "") or str(PROJECT_ROOT / "cirujano.db")


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


def add_column(cur, table: str, name: str, col_type: str, default: str | None) -> None:
    if default is None:
        sql = f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"
    else:
        sql = f"ALTER TABLE {table} ADD COLUMN {name} {col_type} DEFAULT {default}"
    cur.execute(sql)


def normalize(db_path: str) -> None:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB no encontrada: {db_path}")

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
    conn.close()


if __name__ == "__main__":
    normalize(DB_PATH)
    print("✅ Normalización completada")
