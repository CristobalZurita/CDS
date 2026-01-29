#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
checks = [
    ("Inventory model", ROOT / "backend/app/models/inventory.py"),
    ("Inventory endpoints", ROOT / "backend/app/api/v1/endpoints/inventory.py"),
    ("Inventory admin page", ROOT / "src/vue/content/pages/admin/InventoryPage.vue"),
    ("Inventory table", ROOT / "src/vue/components/admin/InventoryTable.vue"),
]
print("Item\tEstado\tEvidencia")
for label, path in checks:
    print(f"{label}\t{'EXISTE' if path.exists() else 'NO'}\t{path.relative_to(ROOT) if path.exists() else ''}")
