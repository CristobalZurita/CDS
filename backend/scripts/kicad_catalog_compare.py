#!/usr/bin/env python3
"""
Compara catálogo KiCad (symbols) vs inventario Excel.
Salida:
  reports/kicad_symbols_index.txt
  reports/kicad_compare.json
Uso:
  PYTHONPATH=backend python backend/scripts/kicad_catalog_compare.py --excel /ruta/Inventario_Cirujanosintetizadores.xlsx --kicad /usr/share/kicad/symbols
"""
import argparse
import json
import re
from pathlib import Path

import pandas as pd


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def extract_excel_items(excel_path: Path) -> set[str]:
    df = pd.read_excel(excel_path, header=None)
    values = set()
    for col in df.columns:
        for val in df[col].dropna():
            text = str(val).strip()
            if not text or text.lower() in {"nan", "none"}:
                continue
            values.add(text)
    return values


def extract_kicad_symbols(kicad_dir: Path) -> set[str]:
    symbols = set()
    pattern = re.compile(r'\(symbol\s+"([^"]+)"')
    for path in kicad_dir.rglob("*.kicad_sym"):
        try:
            content = path.read_text(errors="ignore")
        except Exception:
            continue
        for match in pattern.finditer(content):
            symbols.add(match.group(1).strip())
    return symbols


def main_from_args(excel_path: str, kicad_path: str, out_dir: str = "reports") -> int:
    excel_path = Path(excel_path).expanduser()
    kicad_dir = Path(kicad_path).expanduser()
    out_dir = Path(out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not excel_path.exists():
        print(f"Excel no encontrado: {excel_path}")
        return 1
    if not kicad_dir.exists():
        print(f"KiCad symbols no encontrado: {kicad_dir}")
        return 1

    excel_items = extract_excel_items(excel_path)
    kicad_symbols = extract_kicad_symbols(kicad_dir)

    excel_norm = {normalize_token(x): x for x in excel_items}
    kicad_norm = {normalize_token(x): x for x in kicad_symbols}

    matches = sorted({excel_norm[k] for k in excel_norm.keys() & kicad_norm.keys()})
    excel_only = sorted({excel_norm[k] for k in excel_norm.keys() - kicad_norm.keys()})
    kicad_only = sorted({kicad_norm[k] for k in kicad_norm.keys() - excel_norm.keys()})

    (out_dir / "kicad_symbols_index.txt").write_text("\n".join(sorted(kicad_symbols)))
    (out_dir / "kicad_compare.json").write_text(
        json.dumps(
            {
                "excel_count": len(excel_items),
                "kicad_count": len(kicad_symbols),
                "matches_count": len(matches),
                "excel_only_count": len(excel_only),
                "kicad_only_count": len(kicad_only),
                "matches_sample": matches[:200],
                "excel_only_sample": excel_only[:200],
                "kicad_only_sample": kicad_only[:200]
            },
            indent=2,
            ensure_ascii=True
        )
    )

    print(f"Excel items: {len(excel_items)}")
    print(f"KiCad symbols: {len(kicad_symbols)}")
    print(f"Matches: {len(matches)}")
    print(f"Salida: {out_dir}/kicad_compare.json")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--excel", required=True, help="Ruta al Excel maestro")
    parser.add_argument("--kicad", required=True, help="Ruta a /usr/share/kicad/symbols")
    parser.add_argument("--out-dir", default="reports", help="Directorio de salida")
    args = parser.parse_args()
    raise SystemExit(main_from_args(excel_path=args.excel, kicad_path=args.kicad, out_dir=args.out_dir))
