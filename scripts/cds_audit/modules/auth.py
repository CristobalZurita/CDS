#!/usr/bin/env python3
"""Audit auth module evidence."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

checks = [
    ("JWT HS256 config", ROOT / "backend/app/core/security.py"),
    ("JWT secrets in config", ROOT / "backend/app/core/config.py"),
    ("Auth endpoints", ROOT / "backend/app/api/v1/endpoints/auth.py"),
    ("Login UI", ROOT / "src/vue/components/auth/LoginForm.vue"),
    ("Register UI", ROOT / "src/vue/components/auth/RegisterForm.vue"),
    ("Password reset", ROOT / "src/vue/content/pages/PasswordResetPage.vue"),
]

print("Item\tEstado\tEvidencia")
for label, path in checks:
    print(f"{label}\t{'EXISTE' if path.exists() else 'NO'}\t{path.relative_to(ROOT) if path.exists() else ''}")
