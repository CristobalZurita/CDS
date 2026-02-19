#!/usr/bin/env python3
"""
Valida consistencia entre:
- src/data/instruments.json (canonico)
- src/assets/data/instruments.json (compatibilidad legado)
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _required_legacy_keys() -> List[str]:
    return [
        "id",
        "brand",
        "model",
        "type",
        "components",
        "imagen_url",
        "photo_key",
        "marca",
        "modelo",
        "foto_principal",
        "fotos_adicionales",
        "marca_habilitada",
    ]


def validate(workspace_root: Path, expected_fotos: int) -> int:
    canonical_path = workspace_root / "src" / "data" / "instruments.json"
    assets_path = workspace_root / "src" / "assets" / "data" / "instruments.json"

    if not canonical_path.exists():
        print(f"❌ No existe archivo canónico: {canonical_path}")
        return 1
    if not assets_path.exists():
        print(f"❌ No existe archivo legado: {assets_path}")
        return 1

    canonical = _load_json(canonical_path)
    assets = _load_json(assets_path)

    canonical_instruments = canonical.get("instruments", [])
    assets_instruments = assets.get("instruments", [])

    errors: List[str] = []

    if canonical.get("total_instruments") != len(canonical_instruments):
        errors.append(
            f"total_instruments canónico inconsistente: header={canonical.get('total_instruments')} "
            f"len={len(canonical_instruments)}"
        )
    if assets.get("total_instruments") != len(assets_instruments):
        errors.append(
            f"total_instruments legado inconsistente: header={assets.get('total_instruments')} "
            f"len={len(assets_instruments)}"
        )

    canonical_validation = canonical.get("validacion", {})
    if not canonical_validation.get("coinciden"):
        errors.append("validacion.canónico.coinciden es false")
    if canonical_validation.get("fotos_en_carpeta") != expected_fotos:
        errors.append(
            f"fotos_en_carpeta distinto al esperado: {canonical_validation.get('fotos_en_carpeta')} != {expected_fotos}"
        )
    if canonical_validation.get("fotos_en_json") != expected_fotos:
        errors.append(
            f"fotos_en_json distinto al esperado: {canonical_validation.get('fotos_en_json')} != {expected_fotos}"
        )

    canonical_photo_keys = {inst.get("foto_principal") for inst in canonical_instruments}
    assets_photo_keys = {inst.get("photo_key") for inst in assets_instruments}
    if canonical_photo_keys != assets_photo_keys:
        missing = sorted(canonical_photo_keys - assets_photo_keys)
        extras = sorted(assets_photo_keys - canonical_photo_keys)
        errors.append(
            f"photo_key desalineado. missing={len(missing)} extras={len(extras)}"
        )
        if missing:
            errors.append(f"missing sample: {missing[:5]}")
        if extras:
            errors.append(f"extras sample: {extras[:5]}")

    required_keys = _required_legacy_keys()
    for inst in assets_instruments:
        for key in required_keys:
            if key not in inst:
                errors.append(f"instrumento legado sin key '{key}': {inst.get('id')}")
                break

    if errors:
        print("❌ VALIDACION FALLIDA")
        for err in errors:
            print(f" - {err}")
        return 1

    print("✅ VALIDACION OK")
    print(f"   Canonico: {len(canonical_instruments)} instrumentos")
    print(f"   Legado:   {len(assets_instruments)} instrumentos")
    print(f"   Fotos esperadas: {expected_fotos}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida consistencia de datasets de instrumentos")
    parser.add_argument("--expected-fotos", type=int, default=249, help="Cantidad esperada de fotos")
    args = parser.parse_args()

    workspace_root = Path(__file__).parent.parent
    return validate(workspace_root, args.expected_fotos)


if __name__ == "__main__":
    raise SystemExit(main())
