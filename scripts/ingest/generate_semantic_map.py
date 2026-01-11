#!/usr/bin/env python3
"""Generate a semantic map CSV from the validation report.

Reads `reports/validation_report.json` and produces `docs/semantic_map.csv` with suggested
semantic category and destination table for each column to guide ETAPA 3.
"""
from __future__ import annotations
import json
import os
import csv

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT_PATH = os.path.join(REPO_ROOT, 'reports', 'validation_report.json')
OUT_DIR = os.path.join(REPO_ROOT, 'docs')
OUT_CSV = os.path.join(OUT_DIR, 'semantic_map.csv')

DEFAULT_MAPPING = {
    "Resistencias": ("resistor", "items"),
    "Capacitores Ceramicos": ("capacitor_ceramic", "items"),
    "Capacitores Electrolíticos": ("capacitor_electrolytic", "items"),
    "Transistores": ("transistor", "items"),
    "Ic's": ("ic", "items"),
    "Diodos": ("diode", "items"),
    "Diodo Led": ("led", "items"),
    "otros": ("other", "items"),
    "herramientas taller": ("tool", "items"),
    "insumos taller": ("supply", "items"),
    "N°": ("source_row", "imports")
}


def load_report(path=REPORT_PATH):
    if not os.path.exists(path):
        raise SystemExit(f'Validation report not found: {path}. Run validate_excel first.')
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def generate_map(report):
    rows = []
    total_rows = report.get('row_count', 0)
    for col in report.get('columns', []):
        name = col['name']
        detected = '|'.join(col.get('detected_types', []))
        nulls = col.get('null_count', 0)
        null_ratio = round(nulls / max(1, total_rows), 3)
        suggested_semantic, suggested_table = DEFAULT_MAPPING.get(name, ('unknown', 'items'))
        notes = []
        if len(col.get('detected_types', [])) > 1:
            notes.append('mixed_types')
        if col.get('multi_value'):
            notes.append('multi_value')
        if null_ratio > 0.5:
            notes.append('high_null_ratio')
        rows.append({
            'excel_column': name,
            'suggested_semantic': suggested_semantic,
            'suggested_table': suggested_table,
            'detected_types': detected,
            'null_ratio': null_ratio,
            'notes': ','.join(notes)
        })
    return rows


def save_csv(rows, path=OUT_CSV):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['excel_column', 'suggested_semantic', 'suggested_table', 'detected_types', 'null_ratio', 'notes'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f'Wrote semantic map to {path}')


def main():
    report = load_report()
    rows = generate_map(report)
    save_csv(rows)


if __name__ == '__main__':
    main()
