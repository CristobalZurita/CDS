#!/usr/bin/env python3
"""
Configura un upload preset base para Cloudinary sin hardcodes de carpeta.

Este helper no reemplaza el contrato canónico del repo:
el public_id final debe seguir viniendo explícito desde ZERO/backend.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

try:
    import cloudinary
    import cloudinary.api
except ImportError:
    print("❌ Error: pip install cloudinary")
    sys.exit(1)


def _load_env() -> None:
    backend_env = BACKEND_ROOT / ".env"
    root_env = ROOT / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
    elif root_env.exists():
        load_dotenv(root_env)


def _configure_cloudinary() -> None:
    _load_env()
    from app.services.cloudinary_service import resolve_cloudinary_config

    config = resolve_cloudinary_config()
    if not config:
        print("❌ Configura CLOUDINARY_URL o CLOUDINARY_CLOUD_NAME/CLOUDINARY_API_KEY/CLOUDINARY_API_SECRET")
        sys.exit(1)

    cloudinary.config(
        cloud_name=config["cloud_name"],
        api_key=config["api_key"],
        api_secret=config["api_secret"],
    )


def configure_preset() -> None:
    _configure_cloudinary()

    preset_name = os.getenv("CLOUDINARY_PRESET_NAME", "cds_media_library")
    payload = {
        "unsigned": False,
        "use_filename": True,
        "unique_filename": False,
        "overwrite": True,
        "invalidate": True,
        "resource_type": "image",
    }

    try:
        cloudinary.api.create_upload_preset(name=preset_name, **payload)
        action = "creado"
    except Exception:
        cloudinary.api.update_upload_preset(preset_name, **payload)
        action = "actualizado"

    print(f"✅ Upload preset '{preset_name}' {action}")
    print("   - signed")
    print("   - use_filename: true")
    print("   - unique_filename: false")
    print("   - overwrite: true")
    print("   - invalidate: true")
    print()
    print("Recuerda: el contrato final del repo depende del public_id explícito o de la ruta inicial, no de una carpeta fija del preset.")


if __name__ == "__main__":
    configure_preset()
