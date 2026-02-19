#!/usr/bin/env python3
"""
Auditoría rápida de fuente maestra de inventario.

Objetivo:
- Confirmar estado del Excel maestro vs copia alternativa.
- Comparar JSONs de DE_PYTHON_NUEVO raíz vs subcarpeta json/.
- Mostrar estado de categorías/SKU en backend/cirujano.db.

Uso:
  python scripts/ingest/audit_inventory_source.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER_EXCEL = REPO_ROOT / "Inventario_Cirujanosintetizadores.xlsx"
ALT_EXCEL = REPO_ROOT / "DE_PYTHON_NUEVO" / "Inventario_Cirujanosintetizadores.xlsx"
DB_PATH = REPO_ROOT / "backend" / "cirujano.db"

JSON_PAIRS = [
    ("resistors.json", "display_value"),
    ("capacitors_ceramic.json", "display_value"),
    ("integrated_circuits.json", "part_number"),
    ("transistors.json", "part_number"),
]


def sha256_of_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def load_json_array(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else []


def compare_json_pair(filename: str, key: str) -> dict:
    root_file = REPO_ROOT / "DE_PYTHON_NUEVO" / filename
    nested_file = REPO_ROOT / "DE_PYTHON_NUEVO" / "json" / filename

    root_data = load_json_array(root_file)
    nested_data = load_json_array(nested_file)

    root_set = {str(item.get(key, "")).strip().upper() for item in root_data if item.get(key)}
    nested_set = {str(item.get(key, "")).strip().upper() for item in nested_data if item.get(key)}

    return {
        "filename": filename,
        "root_exists": root_file.exists(),
        "nested_exists": nested_file.exists(),
        "root_count": len(root_data),
        "nested_count": len(nested_data),
        "root_only": len(root_set - nested_set),
        "nested_only": len(nested_set - root_set),
        "same_hash": (sha256_of_file(root_file) == sha256_of_file(nested_file))
        if root_file.exists() and nested_file.exists()
        else None,
    }


def read_db_summary() -> dict:
    if not DB_PATH.exists():
        return {"db_exists": False}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM products")
        products_count = cur.fetchone()[0]
    except Exception:
        products_count = None

    try:
        cur.execute("SELECT COUNT(*) FROM categories")
        categories_count = cur.fetchone()[0]
    except Exception:
        categories_count = None

    prefix_distribution = []
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c,
                   CASE
                     WHEN INSTR(sku, '-') > 0 THEN SUBSTR(sku, 1, INSTR(sku, '-') - 1)
                     ELSE sku
                   END AS prefix
            FROM products
            GROUP BY prefix
            ORDER BY c DESC
            """
        )
        prefix_distribution = cur.fetchall()
    except Exception:
        prefix_distribution = []

    conn.close()
    return {
        "db_exists": True,
        "products_count": products_count,
        "categories_count": categories_count,
        "prefix_distribution": prefix_distribution,
    }


def main() -> int:
    master_hash = sha256_of_file(MASTER_EXCEL)
    alt_hash = sha256_of_file(ALT_EXCEL)

    print("=" * 72)
    print("AUDITORIA FUENTE INVENTARIO (MAESTRA)")
    print("=" * 72)
    print(f"Excel maestro: {MASTER_EXCEL}")
    print(f"  existe={MASTER_EXCEL.exists()} hash={master_hash}")
    print(f"Excel alterno: {ALT_EXCEL}")
    print(f"  existe={ALT_EXCEL.exists()} hash={alt_hash}")
    if master_hash and alt_hash:
        print(f"  master==alt: {master_hash == alt_hash}")
    print("-" * 72)

    print("Comparación JSON DE_PYTHON_NUEVO/")
    for filename, key in JSON_PAIRS:
        result = compare_json_pair(filename, key)
        print(
            f"- {result['filename']}: root={result['root_count']} nested={result['nested_count']} "
            f"root_only={result['root_only']} nested_only={result['nested_only']} "
            f"same_hash={result['same_hash']}"
        )
    print("-" * 72)

    db = read_db_summary()
    if not db.get("db_exists"):
        print(f"DB no encontrada: {DB_PATH}")
        return 0

    print(f"DB: {DB_PATH}")
    print(f"  products={db.get('products_count')} categories={db.get('categories_count')}")
    if db.get("prefix_distribution"):
        print("  prefijos SKU (top 12):")
        for count, prefix in db["prefix_distribution"][:12]:
            print(f"    {prefix}: {count}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

