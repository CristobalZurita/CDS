#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
checks = [
    ("Frontend vitest config", ROOT / "vitest.config.js"),
    ("Frontend tests dir", ROOT / "tests"),
    ("Backend tests dir", ROOT / "backend/tests"),
]
print("Item\tEstado\tEvidencia")
for label, path in checks:
    print(f"{label}\t{'EXISTE' if path.exists() else 'NO'}\t{path.relative_to(ROOT) if path.exists() else ''}")
