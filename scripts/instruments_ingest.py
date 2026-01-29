#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "public" / "images" / "instrumentos"
OUT_CSV = Path("/tmp/instruments_seed.csv")
OUT_JSON = Path("/tmp/instruments_seed.json")

VALID_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def parse_name(stem: str) -> tuple[str, str]:
    cleaned = stem.strip().replace("__", "_")
    parts = [p for p in cleaned.split("_") if p]
    if not parts:
        return ("Unknown", stem)
    brand = parts[0].title()
    model = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"
    model = model.replace("-", " ").strip()
    model = re.sub(r"\s+", " ", model)
    return (brand, model)


def main() -> None:
    rows = []
    for p in sorted(IMAGES_DIR.iterdir()):
        if not p.is_file() or p.suffix.lower() not in VALID_EXTS:
            continue
        brand, model = parse_name(p.stem)
        rows.append(
            {
                "brand": brand,
                "model": model,
                "photo_base_url": f"/images/instrumentos/{p.name}",
                "status": "pending_map",
                "template_json": "",
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [])
        if rows:
            w.writeheader()
            w.writerows(rows)

    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
