#!/usr/bin/env python3
"""Normalize Excel rows into a canonical JSON list ready for import.

Produces `reports/normalized_items.json` with an array of item objects.
"""
from __future__ import annotations
import os
import json
from datetime import datetime
import pandas as pd
import re
import hashlib

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MASTER_EXCEL = os.path.join(REPO_ROOT, 'Inventario_Cirujanosintetizadores.xlsx')
ALT_EXCEL = os.path.join(REPO_ROOT, 'DE_PYTHON_NUEVO', 'Inventario_Cirujanosintetizadores.xlsx')
EXCEL = os.getenv('INVENTORY_EXCEL_PATH') or MASTER_EXCEL
OUT = os.path.join(REPO_ROOT, 'reports', 'normalized_items.json')


def normalize_row(idx, row):
    # Choose primary name and category as in inventory POC
    priority = ["Ic's", 'Transistores', 'Resistencias', 'Diodos', 'Diodo Led', 'otros', 'herramientas taller', 'insumos taller']
    name = None
    category = None
    for col in priority:
        if col in row and str(row[col]).strip():
            name = str(row[col]).strip()
            category = col
            break
    if name is None:
        for c in row.index:
            if str(row[c]).strip():
                name = str(row[c]).strip()
                category = str(c)
                break

    # safe numeric conversion for source row (some rows may have NaN)
    try:
        source_row = int(row.get('N°')) if row.get('N°') not in (None, '') and not pd.isna(row.get('N°')) else idx
    except Exception:
        source_row = idx
    sku = build_sku(name, category)
    normalized = {
        'source_row': source_row,
        'sku': sku,
        'name': name or f'row-{idx}',
        'category': category or 'unknown',
        'raw': {c: (None if pd.isna(row[c]) else str(row[c]).strip()) for c in row.index},
        'normalized_at': datetime.utcnow().isoformat() + 'Z'
    }
    return normalized


def build_sku(name, category):
    if not name:
        return None
    cat = (category or '').strip().lower()
    code = normalize_code(name)
    prefix = {
        "resistencias": "RES",
        "capacitores ceramicos": "CAP-C",
        "capacitores electrolíticos": "CAP-E",
        "capacitores electroliticos": "CAP-E",
        "transistores": "Q",
        "ic's": "IC",
        "diodos": "DIO",
        "diodo led": "LED",
        "otros": "OTH",
        "herramientas taller": "TOOL",
        "insumos taller": "INS"
    }.get(cat, "OTH")
    if not code:
        code = slugify(name)
    return f"{prefix}-{code}"


def normalize_code(value):
    if value is None:
        return None
    raw = str(value).strip().upper()
    if not raw:
        return None
    raw = raw.replace("Ω", "").replace("OHM", "").replace("OHMS", "").replace(" ", "")
    raw = raw.replace(",", ".")

    # Keep common part numbers intact
    if re.match(r"^[A-Z]{1,4}[0-9A-Z]+$", raw):
        return raw

    # Capacitor numeric codes (104/105/106...)
    digits = re.sub(r"[^0-9]", "", raw)
    if digits:
        return digits

    # Try to parse resistance values
    try:
        num = float(raw)
        if num >= 1_000_000:
            return f"{int(num/1_000_000)}M"
        if num >= 1000:
            k = num / 1000
            if k.is_integer():
                return f"{int(k)}K"
            k_str = f"{k:.1f}".rstrip("0").rstrip(".")
            return k_str.replace(".", "K")
        if num >= 10:
            return f"{int(num)}R"
        r_str = f"{num:.1f}".rstrip("0").rstrip(".")
        return r_str.replace(".", "R")
    except Exception:
        return slugify(raw)


def slugify(text):
    return re.sub(r"[^A-Z0-9\\-]+", "", str(text).upper().replace(" ", "-"))


def _sha256_of_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def main():
    excel_path = os.path.abspath(os.path.expanduser(EXCEL))
    if not os.path.exists(excel_path):
        raise SystemExit(f'Excel not found: {excel_path}')

    master_hash = _sha256_of_file(MASTER_EXCEL)
    alt_hash = _sha256_of_file(ALT_EXCEL)
    selected_hash = _sha256_of_file(excel_path)

    if master_hash and alt_hash and master_hash != alt_hash:
        print(
            "WARNING: Inventario maestro y copia DE_PYTHON_NUEVO tienen hash distinto. "
            f"usando={excel_path}"
        )

    df = pd.read_excel(excel_path, sheet_name=0, dtype=object, engine='openpyxl')
    items = []
    for idx, row in df.iterrows():
        items.append(normalize_row(idx + 1, row))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)
    print(f'Wrote normalized items to {OUT} ({len(items)} items)')
    print(f'Excel source: {excel_path}')
    print(f'Excel hash: {selected_hash}')


if __name__ == '__main__':
    main()
