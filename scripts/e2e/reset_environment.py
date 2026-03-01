#!/usr/bin/env python3
"""Prepare an isolated runtime for Playwright E2E."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
RUNTIME_DIR = BACKEND_DIR / "tests" / "e2e_runtime"
SOURCE_DB = BACKEND_DIR / "cirujano.db"
TARGET_DB = RUNTIME_DIR / "e2e_cirujano.db"
UPLOADS_DIR = RUNTIME_DIR / "uploads"


def main() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if UPLOADS_DIR.exists():
        shutil.rmtree(UPLOADS_DIR, ignore_errors=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_DB, TARGET_DB)
    print(f"Prepared E2E DB at {TARGET_DB}")
    print(f"Prepared isolated uploads dir at {UPLOADS_DIR}")


if __name__ == "__main__":
    main()
