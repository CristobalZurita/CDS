#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

from app.core.database import SessionLocal
from app.models import Instrument

CSV_PATH = Path("/tmp/instruments_seed.csv")


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV no encontrado: {CSV_PATH}")

    db = SessionLocal()
    created = 0
    try:
        with CSV_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = f"{row['brand']} {row['model']}".strip()
                model = row["model"].strip() or "Unknown"
                instrument = Instrument(
                    name=name,
                    model=model,
                    type="synthesizer",
                    image={"url": row["photo_base_url"], "status": "loaded"},
                    photo_base_url=row["photo_base_url"],
                    mapping_status=row["status"] or "pending_map",
                )
                db.add(instrument)
                created += 1
        db.commit()
    finally:
        db.close()
    print(f"OK: {created} instrumentos cargados")


if __name__ == "__main__":
    main()
