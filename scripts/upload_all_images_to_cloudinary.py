#!/usr/bin/env python3
"""
Sube imágenes locales a Cloudinary respetando el contrato canónico del repo.

Regla:
    /images/carpeta/nombre.ext -> public_id = carpeta/nombre

No depende del panel de Cloudinary ni de presets manuales.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend"
BASE_DIR = ROOT / "CDS_VUE3_ZERO" / "public" / "images"
SUPPORTED_EXTENSIONS = (".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".avif")

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.cloudinary_service import local_path_to_public_id  # type: ignore  # noqa: E402


def _load_env() -> None:
    backend_env = BACKEND_ROOT / ".env"
    root_env = ROOT / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
    elif root_env.exists():
        load_dotenv(root_env)


def _configure_cloudinary():
    _load_env()
    try:
        import cloudinary
    except ImportError:
        print("❌ Error: pip install cloudinary")
        sys.exit(1)
    from app.services.cloudinary_service import resolve_cloudinary_config  # type: ignore  # noqa: E402

    config = resolve_cloudinary_config()
    if not config:
        print("❌ Configura CLOUDINARY_URL o CLOUDINARY_CLOUD_NAME/CLOUDINARY_API_KEY/CLOUDINARY_API_SECRET")
        sys.exit(1)

    cloudinary.config(
        cloud_name=config["cloud_name"],
        api_key=config["api_key"],
        api_secret=config["api_secret"],
    )

    return cloudinary


def _iter_images(base_dir: Path) -> list[Path]:
    images: list[Path] = []
    for extension in SUPPORTED_EXTENSIONS:
        images.extend(base_dir.rglob(f"*{extension}"))
    return sorted(path for path in images if path.is_file())


def _canonical_public_id(base_dir: Path, image_path: Path) -> str:
    relative_path = image_path.relative_to(base_dir).as_posix()
    local_path = f"/images/{relative_path}"
    return local_path_to_public_id(local_path)


def upload_all(base_dir: Path, dry_run: bool = False) -> int:
    cloudinary = _configure_cloudinary()
    import cloudinary.uploader

    if not base_dir.exists():
        print(f"❌ No existe la carpeta base: {base_dir}")
        return 1

    print(f"📂 Buscando imágenes en: {base_dir}")
    images = _iter_images(base_dir)
    print(f"🖼️  Encontradas {len(images)} imágenes")
    print()

    uploaded = 0
    failed = 0

    for image_path in images:
        relative_path = image_path.relative_to(base_dir).as_posix()
        public_id = _canonical_public_id(base_dir, image_path)
        asset_folder = public_id.rsplit("/", 1)[0] if "/" in public_id else ""

        print(f"⬆️  Subiendo: /images/{relative_path}")
        print(f"   → Public ID: {public_id}")
        if asset_folder:
            print(f"   → Asset folder: {asset_folder}")

        if dry_run:
            print("   → Dry run: sin upload")
            print()
            continue

        try:
            options = {
                "public_id": public_id,
                "overwrite": True,
                "invalidate": True,
                "resource_type": "image",
            }
            if asset_folder:
                options["asset_folder"] = asset_folder

            result = cloudinary.uploader.upload(str(image_path), **options)
            print(f"   ✅ URL: {result['secure_url']}")
            uploaded += 1
        except Exception as exc:
            print(f"   ❌ Error: {exc}")
            failed += 1

        print()

    print(f"📊 Resumen: {uploaded} subidas, {failed} fallidas")
    return 0 if failed == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-dir",
        default=str(BASE_DIR),
        help="Carpeta raíz de imágenes locales. Default: CDS_VUE3_ZERO/public/images",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra los public_id canónicos sin subir nada.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(upload_all(Path(args.base_dir).resolve(), dry_run=args.dry_run))
