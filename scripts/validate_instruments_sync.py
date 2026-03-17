#!/usr/bin/env python3
"""
Valida consistencia del dataset real de instrumentos:
- backend/app/data/instruments.json
- backend/app/data/brands.json
- media_assets de instrumentos con fallback local
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from sync_instruments import InstrumentSyncer


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
    instruments_path = workspace_root / "backend" / "app" / "data" / "instruments.json"
    brands_path = workspace_root / "backend" / "app" / "data" / "brands.json"
    syncer = InstrumentSyncer(str(workspace_root), expected_fotos=expected_fotos)
    image_sources = syncer.get_instrument_image_sources()
    image_names = set(image_sources.keys())

    if not instruments_path.exists():
        print(f"❌ No existe dataset de instrumentos: {instruments_path}")
        return 1
    if not brands_path.exists():
        print(f"❌ No existe dataset de marcas: {brands_path}")
        return 1
    if not image_names:
        print("❌ No existen assets de instrumentos en media_assets ni en fallback local")
        return 1

    instruments_payload = _load_json(instruments_path)
    brands_payload = _load_json(brands_path)

    instruments = instruments_payload.get("instruments", [])
    brands = brands_payload.get("brands", [])

    errors: List[str] = []

    if instruments_payload.get("total_instruments") != len(instruments):
        errors.append(
            f"total_instruments inconsistente: header={instruments_payload.get('total_instruments')} "
            f"len={len(instruments)}"
        )
    if instruments_payload.get("total_fotos_json") != instruments_payload.get("total_fotos"):
        errors.append(
            f"total_fotos_json inconsistente: json={instruments_payload.get('total_fotos_json')} "
            f"fotos={instruments_payload.get('total_fotos')}"
        )

    validation = instruments_payload.get("validacion", {})
    if not validation.get("coinciden"):
        errors.append("validacion.coinciden es false")
    if validation.get("fotos_en_carpeta") != expected_fotos:
        errors.append(
            f"fotos_en_carpeta distinto al esperado: {validation.get('fotos_en_carpeta')} != {expected_fotos}"
        )
    if validation.get("fotos_en_json") != expected_fotos:
        errors.append(
            f"fotos_en_json distinto al esperado: {validation.get('fotos_en_json')} != {expected_fotos}"
        )

    referenced_photo_keys = set()
    for inst in instruments:
        main_photo = inst.get("photo_key") or inst.get("foto_principal")
        if main_photo:
            referenced_photo_keys.add(main_photo)
        for extra_photo in inst.get("fotos_adicionales") or []:
            if extra_photo:
                referenced_photo_keys.add(extra_photo)

    if referenced_photo_keys != image_names:
        missing = sorted(image_names - referenced_photo_keys)
        extras = sorted(referenced_photo_keys - image_names)
        errors.append(
            f"fotos referenciadas desalineadas con carpeta real. missing={len(missing)} extras={len(extras)}"
        )
        if missing:
            errors.append(f"missing sample: {missing[:5]}")
        if extras:
            errors.append(f"extras sample: {extras[:5]}")

    required_keys = _required_legacy_keys()
    for inst in instruments:
        for key in required_keys:
            if key not in inst:
                errors.append(f"instrumento sin key '{key}': {inst.get('id')}")
                break
        brand_id = str(inst.get("brand") or "").strip()
        if inst.get("marca_habilitada") and brand_id and all(str(brand.get("id")) != brand_id for brand in brands):
            errors.append(f"instrumento con brand inexistente '{brand_id}': {inst.get('id')}")
        image_url = str(inst.get("imagen_url") or "")
        if image_url and not image_url.startswith("/images/instrumentos/"):
            errors.append(f"imagen_url con prefijo inesperado: {inst.get('id')} -> {image_url}")

    if errors:
        print("❌ VALIDACION FALLIDA")
        for err in errors:
            print(f" - {err}")
        return 1

    print("✅ VALIDACION OK")
    print(f"   Instrumentos: {len(instruments)}")
    print(f"   Marcas:       {len(brands)}")
    print(f"   Assets fuente: {len(image_names)}")
    print(f"   Fotos esperadas: {expected_fotos}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida consistencia de datasets de instrumentos")
    parser.add_argument("--expected-fotos", type=int, default=273, help="Cantidad esperada de fotos")
    args = parser.parse_args()

    workspace_root = Path(__file__).parent.parent
    return validate(workspace_root, args.expected_fotos)


if __name__ == "__main__":
    raise SystemExit(main())
