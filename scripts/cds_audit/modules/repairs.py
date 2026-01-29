#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
checks = [
    ("Repair model", ROOT / "backend/app/models/repair.py"),
    ("Repair endpoints", ROOT / "backend/app/api/v1/endpoints/repairs.py"),
    ("Repairs admin page", ROOT / "src/vue/content/pages/admin/RepairsAdminPage.vue"),
    ("Repairs user page", ROOT / "src/vue/content/pages/RepairsPage.vue"),
]
print("Item\tEstado\tEvidencia")
for label, path in checks:
    print(f"{label}\t{'EXISTE' if path.exists() else 'NO'}\t{path.relative_to(ROOT) if path.exists() else ''}")
