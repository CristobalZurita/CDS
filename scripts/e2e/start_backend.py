#!/usr/bin/env python3
"""Bootstrap an isolated backend runtime for Playwright E2E."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
PYTHON_BIN = BACKEND_DIR / ".venv" / "bin" / "python"
UVICORN_BIN = BACKEND_DIR / ".venv" / "bin" / "uvicorn"
RUNTIME_DIR = BACKEND_DIR / "tests" / "e2e_runtime"
DB_PATH = RUNTIME_DIR / "e2e_cirujano.db"


def run_python(script: Path, env: dict[str, str]) -> None:
    subprocess.run([str(PYTHON_BIN), str(script)], cwd=ROOT, env=env, check=True)


def main() -> None:
    frontend_port = os.getenv("PLAYWRIGHT_FRONTEND_PORT", "5174")
    api_port = os.getenv("PLAYWRIGHT_API_PORT", "8001")
    api_origin = f"http://127.0.0.1:{api_port}"
    frontend_origin = f"http://127.0.0.1:{frontend_port}"

    base_env = os.environ.copy()
    run_python(ROOT / "scripts" / "e2e" / "reset_environment.py", base_env)
    run_python(
        ROOT / "scripts" / "e2e" / "seed_users.py",
        {
            **base_env,
            "E2E_DB_PATH": str(DB_PATH),
        },
    )

    runtime_env = {
        **base_env,
        "DATABASE_URL": f"sqlite:///{DB_PATH}",
        "ENVIRONMENT": "testing",
        "TURNSTILE_DISABLE": "true",
        "ENABLE_FULL_STARTUP_IN_TESTS": "true",
        "ENABLE_INSTRUMENT_AUTO_SYNC": "false",
        "INSTRUMENT_SYNC_ON_STARTUP": "false",
        "PUBLIC_BASE_URL": api_origin,
        "ALLOWED_ORIGINS": f"{frontend_origin},http://localhost:{frontend_port}",
    }

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(RUNTIME_DIR)
    os.execve(
        str(PYTHON_BIN),
        [
            str(PYTHON_BIN),
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            str(BACKEND_DIR),
            "--host",
            "127.0.0.1",
            "--port",
            api_port,
        ],
        runtime_env,
    )


if __name__ == "__main__":
    main()
