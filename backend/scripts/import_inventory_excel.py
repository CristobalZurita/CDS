#!/usr/bin/env python3
"""
Importa inventario desde el Excel raíz y crea categorías + productos (aditivo).
Uso:
  PYTHONPATH=backend python backend/scripts/import_inventory_excel.py --excel /ruta/Inventario_Cirujanosintetizadores.xlsx --dry-run
  PYTHONPATH=backend python backend/scripts/import_inventory_excel.py --excel /ruta/Inventario_Cirujanosintetizadores.xlsx --apply
"""
import argparse
import re
from pathlib import Path

import pandas as pd

from app.core.database import SessionLocal
from app.models.category import Category
from app.models.inventory import Product


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().upper())
    return cleaned.strip("_") or "ITEM"


def normalize_cell(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return None
    return text


def main_from_args(excel_path: str, apply: bool = False) -> int:
    excel_path = Path(excel_path).expanduser()
    if not excel_path.exists():
        print(f"Excel no encontrado: {excel_path}")
        return 1
    dry_run = not apply
    df = pd.read_excel(excel_path)
    if df.empty:
        print("Excel vacío.")
        return 1

    db = SessionLocal()
    created_categories = 0
    created_products = 0
    skipped_products = 0
    seen_skus: set[str] = set()

    skip_columns = {"N°", "Nº", "NO", "NO.", "#"}
    try:
        for col_name in df.columns:
            category_name = str(col_name).strip()
            if not category_name:
                continue
            if category_name.upper() in skip_columns:
                continue

            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                category = Category(name=category_name, description=f"Importado desde Excel: {category_name}")
                if not dry_run:
                    db.add(category)
                    db.commit()
                    db.refresh(category)
                created_categories += 1

            for val in df[col_name].dropna():
                item_name = normalize_cell(val)
                if not item_name:
                    continue

                sku = f"{slugify(category_name)}-{slugify(item_name)}"
                if sku in seen_skus:
                    skipped_products += 1
                    continue
                seen_skus.add(sku)
                existing = db.query(Product).filter(Product.sku == sku).first()
                if existing:
                    skipped_products += 1
                    continue

                product = Product(
                    name=item_name,
                    sku=sku,
                    category_id=category.id if category and category.id else None,
                    description=f"Importado desde Excel ({category_name})",
                    price=0,
                    quantity=0,
                    min_quantity=0
                )
                if not dry_run:
                    db.add(product)
                created_products += 1

        if not dry_run:
            db.commit()
    finally:
        db.close()

    mode = "DRY RUN" if dry_run else "APLICADO"
    print(f"[{mode}] Categorías nuevas: {created_categories}")
    print(f"[{mode}] Productos nuevos: {created_products}")
    print(f"[{mode}] Productos omitidos (ya existen): {skipped_products}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True, help="Ruta al Excel maestro")
    parser.add_argument("--apply", action="store_true", help="Aplicar cambios en BD")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar conteo (default)")
    args = parser.parse_args()
    apply = args.apply and not args.dry_run
    raise SystemExit(main_from_args(excel_path=args.excel, apply=apply))
