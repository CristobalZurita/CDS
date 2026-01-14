#!/usr/bin/env python3
"""Normalize Excel rows into a canonical JSON list ready for import.

Produces `reports/normalized_items.json` with an array of item objects.
"""
from __future__ import annotations
import os
import json
from datetime import datetime
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EXCEL = os.path.join(REPO_ROOT, 'Inventario_Cirujanosintetizadores.xlsx')
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
    normalized = {
        'source_row': source_row,
        'sku': str(row.get('N°') or idx),
        'name': name or f'row-{idx}',
        'category': category or 'unknown',
        'raw': {c: (None if pd.isna(row[c]) else str(row[c]).strip()) for c in row.index},
        'normalized_at': datetime.utcnow().isoformat() + 'Z'
    }
    return normalized


def main():
    if not os.path.exists(EXCEL):
        raise SystemExit(f'Excel not found: {EXCEL}')
    df = pd.read_excel(EXCEL, sheet_name=0, dtype=object, engine='openpyxl')
    items = []
    for idx, row in df.iterrows():
        items.append(normalize_row(idx + 1, row))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)
    print(f'Wrote normalized items to {OUT} ({len(items)} items)')


if __name__ == '__main__':
    main()
