#!/usr/bin/env python3
"""Import KiCad-oriented component catalog into products table (additive, schema-safe)."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = REPO_ROOT / "DE_PYTHON_NUEVO" / "json" / "kicad_component_catalog.json"
DEFAULT_DB = REPO_ROOT / "backend" / "cirujano.db"

FAMILY_TO_CATEGORY = {
    "resistors": "Resistencias",
    "capacitors_ceramic": "Capacitores Ceramicos",
    "capacitors_electrolytic": "Capacitores Electroliticos",
    "capacitors_misc": "Capacitores",
    "diodes": "Diodos",
    "transistors": "Transistores",
    "integrated_circuits": "Ic's",
    "sensors": "sensores",
    "connectors": "conectores",
    "power_control": "potencia_control",
    "magnetics_protection": "pasivos_potencia",
    "workshop_misc": "taller_misc",
    "manual_inventory": "otros",
}


def load_catalog(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Catalog not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "items" not in data:
        raise ValueError(f"Invalid catalog format: {path}")
    return data


def _column_names(cur: sqlite3.Cursor, table: str) -> list[str]:
    cur.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall()
    return [str(row[1]) for row in rows]


def ensure_category(cur: sqlite3.Cursor, category_columns: list[str], name: str) -> int:
    cur.execute("SELECT id FROM categories WHERE name = ? LIMIT 1", (name,))
    row = cur.fetchone()
    if row:
        return int(row[0])

    now = datetime.now(timezone.utc).isoformat()
    insert_columns = []
    insert_values: list[Any] = []
    if "name" in category_columns:
        insert_columns.append("name")
        insert_values.append(name)
    if "description" in category_columns:
        insert_columns.append("description")
        insert_values.append(f"Catalogo KiCad CDS: {name}")
    if "created_at" in category_columns:
        insert_columns.append("created_at")
        insert_values.append(now)
    if "updated_at" in category_columns:
        insert_columns.append("updated_at")
        insert_values.append(now)

    placeholders = ", ".join(["?"] * len(insert_columns))
    cur.execute(
        f"INSERT INTO categories ({', '.join(insert_columns)}) VALUES ({placeholders})",
        tuple(insert_values),
    )
    return int(cur.lastrowid)


def compact_metadata(item: dict[str, Any]) -> str:
    meta = {
        "origin_status": item.get("origin_status"),
        "enabled": bool(item.get("enabled")),
        "source": item.get("source"),
        "kicad_symbol": item.get("kicad_symbol"),
        "kicad_footprint_default": item.get("kicad_footprint_default"),
        "kicad_footprint_options": item.get("kicad_footprint_options", []),
        "specs": item.get("specs", {}),
    }
    return json.dumps(meta, ensure_ascii=True, separators=(",", ":"))


def run_import(
    catalog_path: Path,
    db_path: Path,
    include_catalog_only: bool = False,
    dry_run: bool = False,
) -> dict[str, int]:
    payload = load_catalog(catalog_path)
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError("Catalog 'items' must be a list")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    inserted = 0
    updated = 0
    skipped = 0

    category_columns = _column_names(cur, "categories")
    product_columns = _column_names(cur, "products")

    if "id" not in category_columns or "name" not in category_columns:
        raise RuntimeError("Table categories has no required columns (id, name)")
    if "id" not in product_columns or "sku" not in product_columns:
        raise RuntimeError("Table products has no required columns (id, sku)")

    insertable_columns = [
        column
        for column in (
            "category_id",
            "name",
            "sku",
            "description",
            "price",
            "quantity",
            "min_quantity",
            "created_at",
            "updated_at",
        )
        if column in product_columns
    ]

    try:
        for item in items:
            if not isinstance(item, dict):
                skipped += 1
                continue

            origin = item.get("origin_status")
            if origin == "CATALOGO_ONLY" and not include_catalog_only:
                skipped += 1
                continue

            family = str(item.get("family") or "").strip()
            category_name = FAMILY_TO_CATEGORY.get(family, "otros")
            category_id = ensure_category(cur, category_columns, category_name)

            sku = str(item.get("kicad_sku") or "").strip()
            if not sku:
                skipped += 1
                continue

            name = str(item.get("display_name") or sku).strip()
            description = compact_metadata(item)

            cur.execute("SELECT id FROM products WHERE sku = ? LIMIT 1", (sku,))
            row = cur.fetchone()
            if row:
                product_id = int(row[0])
                update_parts = []
                update_values: list[Any] = []
                if "name" in product_columns:
                    update_parts.append("name = ?")
                    update_values.append(name)
                if "category_id" in product_columns:
                    update_parts.append("category_id = ?")
                    update_values.append(category_id)
                if "description" in product_columns:
                    update_parts.append("description = ?")
                    update_values.append(description)
                if "updated_at" in product_columns:
                    update_parts.append("updated_at = ?")
                    update_values.append(datetime.now(timezone.utc).isoformat())
                if update_parts:
                    update_sql = f"UPDATE products SET {', '.join(update_parts)} WHERE id = ?"
                    update_values.append(product_id)
                    cur.execute(update_sql, tuple(update_values))
                updated += 1
            else:
                values_by_column = {
                    "category_id": category_id,
                    "name": name,
                    "sku": sku,
                    "description": description,
                    "price": 0,
                    "quantity": 0,
                    "min_quantity": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                placeholders = ", ".join(["?"] * len(insertable_columns))
                insert_sql = (
                    f"INSERT INTO products ({', '.join(insertable_columns)}) "
                    f"VALUES ({placeholders})"
                )
                insert_values = tuple(values_by_column[column] for column in insertable_columns)
                cur.execute(insert_sql, insert_values)
                inserted += 1

        if dry_run:
            conn.rollback()
        else:
            conn.commit()
    finally:
        conn.close()

    return {"inserted": inserted, "updated": updated, "skipped": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(description="Import KiCad catalog into products")
    parser.add_argument("--catalog", type=str, default=str(DEFAULT_CATALOG))
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB))
    parser.add_argument(
        "--include-catalog-only",
        action="store_true",
        help="Import also CATALOGO_ONLY entries (default imports only REAL).",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    summary = run_import(
        catalog_path=Path(args.catalog).expanduser(),
        db_path=Path(args.db).expanduser(),
        include_catalog_only=args.include_catalog_only,
        dry_run=args.dry_run,
    )
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(
        f"[{mode}] inserted={summary['inserted']} updated={summary['updated']} skipped={summary['skipped']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
