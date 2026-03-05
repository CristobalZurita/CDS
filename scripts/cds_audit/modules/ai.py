#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
checks = [
    ("AI endpoints", ROOT / "backend/app/api/v1/endpoints/ai.py"),
    ("Diagnostics endpoints", ROOT / "backend/app/api/v1/endpoints/diagnostics.py"),
    ("AI page", ROOT / "src/vue/content/pages/CotizadorIAPage.vue"),
    ("AI components", ROOT / "src/vue/components/ai/AIAnalysisResult.vue"),
]
print("Item\tEstado\tEvidencia")
for label, path in checks:
    print(f"{label}\t{'EXISTE' if path.exists() else 'NO'}\t{path.relative_to(ROOT) if path.exists() else ''}")
