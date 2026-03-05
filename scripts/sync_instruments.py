#!/usr/bin/env python3
"""
SYNC INSTRUMENTS - LITERAL + AUTO
Lee exactamente lo que existe en public/images/instrumentos/*.webp y genera:
- src/data/instruments.json (canónico)
- src/assets/data/instruments.json (compatibilidad front/back legado)
No inventa instrumentos: solo procesa fotos reales.
"""

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

DEFAULT_EXPECTED_FOTOS = 249
VARIANT_SUFFIXES = (
    "BACK2",
    "FRONT2",
    "BACK",
    "FRONT",
    "LATERAL",
    "LADO",
    "LADOS",
    "SIDE",
    "LEFT",
    "RIGHT",
    "TOP",
    "BOTTOM",
    "DETAIL",
    "CLOSEUP",
)
BRAND_CANONICAL_ALIASES = {
    "ACCES": "ACCESS",
}
BRAND_ID_ALIASES = {
    "ACCESS": "access",
    "AKAI": "akai",
    "ALESIS": "alesis",
    "ARTURIA": "arturia",
    "ASM": "asm",
    "BEHERINGER": "behringer",
    "BEHRINGER": "behringer",
    "CASIO": "casio",
    "KAWAI": "kawai",
    "KORG": "korg",
    "NOVATION": "novation",
    "ROLAND": "roland",
    "STUDIOLOGIC": "studiologic",
    "YAMAHA": "yamaha",
}
BRAND_NAME_OVERRIDES = {
    "access": "Access",
    "akai": "Akai",
    "alesis": "Alesis",
    "arturia": "Arturia",
    "behringer": "Behringer",
    "casio": "Casio",
    "kawai": "Kawai",
    "korg": "Korg",
    "novation": "Novation",
    "roland": "Roland",
    "yamaha": "Yamaha",
}
DEFAULT_COMPONENTS_TEMPLATE = {
    "encoders_rotativos": None,
    "botones": None,
    "lcd": None,
    "leds": None,
    "usb": None,
    "midi_din": True,
    "salidas_audio": 2,
    "faders": None,
    "aftertouch": None,
    "rueda_pitch": True,
    "pedal": True,
}
DEFAULT_FALLAS_COMUNES = [
    "POWER",
    "CONNECTOR_LOOSE",
    "COSMETIC_DAMAGE",
    "WATER_DAMAGE",
    "KEYBOARD_DEAD_KEY",
    "KEYBOARD_STUCK_KEY",
    "ENCODER_INTERMITTENT",
    "BUTTON_DEAD",
]
ASSETS_SYNC_SCHEMA_VERSION = "1.0.0"


def canonical_brand(brand: str) -> str:
    """Normaliza marca para evitar duplicados por typo."""
    return BRAND_CANONICAL_ALIASES.get(brand, brand)


class InstrumentSyncer:
    """Sincroniza instrumentos desde archivos reales y mantiene metadatos."""

    def __init__(self, workspace_root: str, expected_fotos: int = DEFAULT_EXPECTED_FOTOS):
        self.workspace_root = Path(workspace_root)
        self.images_dir = self.workspace_root / "public" / "images" / "instrumentos"
        self.logos_dir = self.images_dir / "LOGOS"
        self.json_path = self.workspace_root / "src" / "data" / "instruments.json"
        self.assets_json_path = self.workspace_root / "src" / "assets" / "data" / "instruments.json"
        self.brands_json_path = self.workspace_root / "src" / "assets" / "data" / "brands.json"
        self.metadata_path = self.workspace_root / "src" / "data" / ".sync_metadata.json"
        self.expected_fotos = expected_fotos

    def get_metadata(self) -> Dict:
        """Carga metadatos previos de sincronización."""
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)

        return {
            "last_count": 0,
            "last_hash": None,
            "last_sync": None,
            "files_processed": [],
            "added_count": 0,
            "status": "virgin",
        }

    def save_metadata(self, metadata: Dict) -> None:
        """Guarda metadatos de sincronización."""
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def calculate_files_hash(self, all_names: List[str]) -> str:
        """Hash SHA256 estable de la lista de fotos."""
        files_str = "|".join(sorted(all_names))
        return hashlib.sha256(files_str.encode()).hexdigest()

    def detect_changes(self, all_names: List[str], metadata: Dict) -> Tuple[Set[str], Set[str], bool]:
        """Detecta nuevos, eliminados y si hubo cambio respecto al último estado."""
        current_hash = self.calculate_files_hash(all_names)
        last_hash = metadata.get("last_hash")
        last_count = metadata.get("last_count", 0)

        all_names_set = set(all_names)
        last_files = set(metadata.get("files_processed", []))

        nuevos = all_names_set - last_files
        eliminados = last_files - all_names_set

        cambio_detectado = (
            len(all_names) != last_count
            or current_hash != last_hash
            or len(nuevos) > 0
            or len(eliminados) > 0
        )

        return nuevos, eliminados, cambio_detectado

    def get_all_webp_files(self) -> Set[str]:
        """Obtiene todos los archivos .webp de instrumentos."""
        if not self.images_dir.exists():
            print(f"❌ Directorio no encontrado: {self.images_dir}")
            return set()

        return {webp_file.stem for webp_file in self.images_dir.glob("*.webp")}

    def get_logo_files(self) -> Dict[str, str]:
        """Obtiene marcas con logo y su ruta pública."""
        logos: Dict[str, str] = {}
        if not self.logos_dir.exists():
            return logos

        for ext in ("webp", "svg", "png", "jpg", "jpeg"):
            for logo_file in self.logos_dir.glob(f"LOGO_*.{ext}"):
                marca = logo_file.stem.replace("LOGO_", "")
                logos[marca] = f"/images/instrumentos/LOGOS/{logo_file.name}"
        return logos

    def resolve_variant_base(self, name: str, all_names_set: Set[str]) -> Tuple[str, str]:
        """
        Si name es variante de una base existente, retorna (base, suffix).
        Si no, retorna (name, "").
        """
        for suffix in sorted(VARIANT_SUFFIXES, key=len, reverse=True):
            token = f"_{suffix}"
            if name.endswith(token):
                base_name = name[: -len(token)]
                if base_name in all_names_set:
                    return base_name, suffix
        return name, ""

    def identify_bases_and_variants(self, all_names: List[str]) -> Tuple[Set[str], Dict[str, List[str]]]:
        """
        Agrupa variantes sobre su base:
        - AKAI_MPD_218 + AKAI_MPD_218_BACK => 1 base, 1 variante.
        """
        all_names_set = set(all_names)
        bases = set(all_names_set)
        variants_map: Dict[str, List[str]] = defaultdict(list)

        for name in all_names:
            base_name, suffix = self.resolve_variant_base(name, all_names_set)
            if suffix:
                variants_map[base_name].append(name)
                if name in bases:
                    bases.remove(name)

        for base_name in variants_map:
            bases.add(base_name)

        return bases, {k: sorted(v) for k, v in variants_map.items()}

    def extract_marca_modelo(self, instrument_name: str) -> Tuple[str, str]:
        """Extrae marca y modelo literal desde nombre de archivo."""
        parts = instrument_name.split("_")
        if len(parts) < 2:
            return instrument_name, instrument_name

        marca = canonical_brand(parts[0])
        modelo = "_".join(parts[1:])
        return marca, modelo

    def sync_and_generate_json(self, all_names: List[str], existing_data: Dict = None) -> Dict:
        """
        Genera JSON desde archivos reales.
        Mantiene campos extra preexistentes por instrumento (modo aditivo).
        """
        bases, variants_map = self.identify_bases_and_variants(all_names)
        logos_map = self.get_logo_files()

        existing_instruments: Dict[str, Dict] = {}
        if existing_data and isinstance(existing_data, dict):
            for inst in existing_data.get("instruments", []):
                inst_id = inst.get("id")
                if inst_id:
                    existing_instruments[inst_id] = inst

        instruments: List[Dict] = []
        detected_brands: Set[str] = set()
        enabled_brands: Set[str] = set()
        disabled_brands: Set[str] = set()

        for base_name in sorted(bases):
            marca, modelo = self.extract_marca_modelo(base_name)
            fotos_adicionales = sorted(variants_map.get(base_name, []))
            base_id = base_name.lower()
            logo_disponible = marca in logos_map

            detected_brands.add(marca)
            if logo_disponible:
                enabled_brands.add(marca)
            else:
                disabled_brands.add(marca)

            core_data = {
                "id": base_id,
                "marca": marca,
                "modelo": modelo,
                "foto_principal": base_name,
                "fotos_adicionales": fotos_adicionales,
                "tipos": ["sintetizador"],
                "marca_logo_disponible": logo_disponible,
                "marca_habilitada": logo_disponible,
                "marca_logo_url": logos_map.get(marca),
            }

            previous = existing_instruments.get(base_id, {})
            merged = dict(previous)
            merged.update(core_data)
            if "agregado_en" not in merged:
                merged["agregado_en"] = datetime.now().isoformat()
            instruments.append(merged)

        total_variantes = sum(len(v) for v in variants_map.values())
        total_fotos_json = sum(1 + len(i.get("fotos_adicionales", [])) for i in instruments)
        fotos_en_carpeta = len(all_names)

        data = {
            "version": "2.1.0",
            "generated_at": datetime.now().isoformat(),
            "total_instruments": len(instruments),
            "total_bases": len(bases),
            "total_variantes": total_variantes,
            "total_fotos": fotos_en_carpeta,
            "total_fotos_json": total_fotos_json,
            "marcas_detectadas": sorted(detected_brands),
            "marcas_con_logo": sorted(enabled_brands),
            "marcas_sin_logo": sorted(disabled_brands),
            "marcas_habilitadas": sorted(enabled_brands),
            "marcas_no_habilitadas": sorted(disabled_brands),
            "validacion": {
                "fotos_en_carpeta": fotos_en_carpeta,
                "fotos_en_json": total_fotos_json,
                "coinciden": fotos_en_carpeta == total_fotos_json,
                "esperado_dataset_base": self.expected_fotos,
                "coincide_con_esperado_dataset_base": fotos_en_carpeta == self.expected_fotos,
            },
            "instruments": instruments,
        }

        return data

    def save_json(self, data: Dict) -> None:
        """Guarda JSON generado."""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _normalize_lookup(value: str) -> str:
        return "".join(ch for ch in str(value or "").lower() if ch.isalnum())

    @staticmethod
    def _humanize_model(modelo: str) -> str:
        return str(modelo or "").replace("_", " ").strip()

    @staticmethod
    def _default_components() -> Dict:
        return dict(DEFAULT_COMPONENTS_TEMPLATE)

    def _to_brand_id(self, marca: str) -> str:
        canonical = canonical_brand(str(marca or "").upper())
        return BRAND_ID_ALIASES.get(canonical, canonical.lower().replace(" ", "-"))

    def sync_and_generate_assets_json(self, canonical_data: Dict, existing_assets_data: Dict = None) -> Dict:
        """
        Genera dataset compatible para consumidores legados (frontend/backend).
        Mantiene campos extra existentes por instrumento (modo aditivo).
        """
        existing_assets_instruments = []
        if existing_assets_data and isinstance(existing_assets_data, dict):
            existing_assets_instruments = existing_assets_data.get("instruments", []) or []

        existing_by_photo: Dict[str, Dict] = {}
        existing_by_brand_model: Dict[Tuple[str, str], Dict] = {}
        for inst in existing_assets_instruments:
            photo_key = inst.get("photo_key") or inst.get("foto_principal")
            if photo_key:
                existing_by_photo[photo_key] = inst
            brand_key = str(inst.get("brand", "")).lower()
            model_key = self._normalize_lookup(inst.get("model") or inst.get("modelo"))
            if brand_key and model_key and (brand_key, model_key) not in existing_by_brand_model:
                existing_by_brand_model[(brand_key, model_key)] = inst

        assets_instruments: List[Dict] = []
        matched_photo_keys: Set[str] = set()

        for canonical_inst in canonical_data.get("instruments", []):
            photo_key = canonical_inst.get("foto_principal")
            marca = canonical_brand(canonical_inst.get("marca", ""))
            modelo = canonical_inst.get("modelo", "")
            brand_id = self._to_brand_id(marca)
            model_human = self._humanize_model(modelo)

            previous = existing_by_photo.get(photo_key)
            if not previous:
                lookup_key = (brand_id, self._normalize_lookup(model_human))
                previous = existing_by_brand_model.get(lookup_key, {})

            previous_photo_key = previous.get("photo_key") or previous.get("foto_principal")
            if previous_photo_key:
                matched_photo_keys.add(previous_photo_key)

            merged = dict(previous)
            components = self._default_components()
            if isinstance(previous.get("components"), dict):
                components.update(previous["components"])

            image_payload = previous.get("image")
            if not isinstance(image_payload, dict):
                image_payload = {"url": None, "status": "pending"}
            else:
                image_payload = dict(image_payload)
                image_payload.setdefault("status", "pending")

            value_payload = previous.get("valor_estimado")
            if not isinstance(value_payload, dict):
                value_payload = {"min": 300000, "max": 1500000, "moneda": "CLP"}

            fallas_comunes = previous.get("fallas_comunes")
            if not isinstance(fallas_comunes, list) or not fallas_comunes:
                fallas_comunes = list(DEFAULT_FALLAS_COMUNES)

            merged.update(
                {
                    "id": previous.get("id") or canonical_inst.get("id"),
                    "brand": brand_id,
                    "model": previous.get("model") or model_human,
                    "type": previous.get("type") or "Keyboard / Synthesizer",
                    "year": previous.get("year", 1995),
                    "description": previous.get("description") or f"Sintetizador {model_human}",
                    "components": components,
                    "valor_estimado": value_payload,
                    "fallas_comunes": fallas_comunes,
                    "imagen_url": f"/images/instrumentos/{photo_key}.webp",
                    "manual_url": previous.get("manual_url"),
                    "image": image_payload,
                    "photo_key": photo_key,
                    # Campos canónicos expuestos también en salida legada
                    "marca": marca,
                    "modelo": modelo,
                    "foto_principal": photo_key,
                    "fotos_adicionales": canonical_inst.get("fotos_adicionales", []),
                    "marca_logo_disponible": canonical_inst.get("marca_logo_disponible"),
                    "marca_habilitada": canonical_inst.get("marca_habilitada"),
                    "marca_logo_url": canonical_inst.get("marca_logo_url"),
                    "tipos": canonical_inst.get("tipos", ["sintetizador"]),
                    "agregado_en": canonical_inst.get("agregado_en"),
                }
            )
            assets_instruments.append(merged)

        legacy_archived = []
        for inst in existing_assets_instruments:
            photo_key = inst.get("photo_key") or inst.get("foto_principal")
            if not photo_key or photo_key not in matched_photo_keys:
                legacy_archived.append(inst)

        return {
            "version": canonical_data.get("version", "2.1.0"),
            "sync_schema_version": ASSETS_SYNC_SCHEMA_VERSION,
            "generated_at": canonical_data.get("generated_at", datetime.now().isoformat()),
            "source": "scripts/sync_instruments.py",
            "total_instruments": len(assets_instruments),
            "total_fotos": canonical_data.get("total_fotos"),
            "total_fotos_json": canonical_data.get("total_fotos_json"),
            "validacion": canonical_data.get("validacion", {}),
            "marcas_habilitadas": canonical_data.get("marcas_habilitadas", []),
            "marcas_no_habilitadas": canonical_data.get("marcas_no_habilitadas", []),
            "legacy_archived_count": len(legacy_archived),
            "legacy_archived": legacy_archived,
            "instruments": assets_instruments,
        }

    def save_assets_json(self, data: Dict) -> None:
        self.assets_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.assets_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_and_generate_brands_json(self, canonical_data: Dict, existing_brands_data: Dict = None) -> Dict:
        """
        Genera brands.json usando SOLO marcas habilitadas (con logo real en carpeta LOGOS).
        Mantiene metadatos existentes de cada marca cuando ya existan.
        """
        previous_brands = []
        if existing_brands_data and isinstance(existing_brands_data, dict):
            previous_brands = existing_brands_data.get("brands", []) or []
        previous_map = {str(b.get("id")): b for b in previous_brands if b.get("id")}

        enabled_brands = canonical_data.get("marcas_habilitadas", []) or []
        canonical_instruments = canonical_data.get("instruments", []) or []
        logo_by_brand: Dict[str, str] = {}
        for inst in canonical_instruments:
            marca = str(inst.get("marca") or "").strip().upper()
            logo_url = inst.get("marca_logo_url")
            if marca and logo_url and marca not in logo_by_brand:
                logo_by_brand[marca] = str(logo_url)
        result = []

        for marca in sorted(enabled_brands):
            brand_id = self._to_brand_id(marca)
            previous = previous_map.get(brand_id, {})
            fallback_name = BRAND_NAME_OVERRIDES.get(brand_id) or str(marca).replace("_", " ").title()
            current_logo_url = logo_by_brand.get(str(marca).upper())
            previous_logo = previous.get("logo") if isinstance(previous.get("logo"), dict) else {}
            merged_logo_url = (
                previous_logo.get("url")
                or previous.get("logo_url")
                or current_logo_url
            )
            logo_status = "loaded" if merged_logo_url else "missing"

            merged = {
                "id": brand_id,
                "name": previous.get("name") or fallback_name,
                "tier": previous.get("tier") or "standard",
                "founded": previous.get("founded"),
                "country": previous.get("country"),
                "description": previous.get("description") or f"Marca habilitada por logo disponible ({marca})",
                "logo_url": merged_logo_url,
                "logo": {
                    "url": merged_logo_url,
                    "path": merged_logo_url,
                    "status": previous_logo.get("status") or logo_status,
                },
            }
            result.append(merged)

        return {"brands": sorted(result, key=lambda b: str(b.get("name", "")).lower())}

    def save_brands_json(self, data: Dict) -> None:
        self.brands_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.brands_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run(self, force_sync: bool = False) -> int:
        """
        Ejecuta sincronización inteligente:
        - Si no hay cambios y no hay force, no regenera.
        - Si hay cambios o force, regenera JSON y metadata.
        """
        print("\n" + "=" * 100)
        print("🎯 SYNC INSTRUMENTS - AUTOMATIC LITERAL + INTELLIGENT")
        print("=" * 100)
        print(f"\n📁 Leyendo de: {self.images_dir}")
        print(f"📝 Generando: {self.json_path}\n")

        try:
            all_webp = self.get_all_webp_files()
            all_names = sorted(list(all_webp))

            if not all_names:
                print("❌ No hay archivos .webp encontrados")
                return 1

            print(f"✅ {len(all_names)} archivos .webp encontrados")
            metadata = self.get_metadata()
            print(f"📊 Último conteo: {metadata['last_count']} archivos")
            print(f"📊 Conteo actual: {len(all_names)} archivos\n")

            assets_data_exists = False
            assets_needs_schema_sync = True
            if self.assets_json_path.exists():
                try:
                    with open(self.assets_json_path, "r", encoding="utf-8") as f:
                        existing_assets_snapshot = json.load(f)
                    assets_data_exists = True
                    assets_needs_schema_sync = (
                        existing_assets_snapshot.get("sync_schema_version") != ASSETS_SYNC_SCHEMA_VERSION
                    )
                except Exception:
                    assets_data_exists = False
                    assets_needs_schema_sync = True

            nuevos, eliminados, cambio = self.detect_changes(all_names, metadata)
            if not cambio and not force_sync and assets_data_exists and not assets_needs_schema_sync:
                print("✨ SIN CAMBIOS - Saltando sincronización (más rápido)")
                print("   Usa --force para forzar resincronización\n")
                return 0

            print("🔄 CAMBIOS DETECTADOS:")
            if nuevos:
                print(f"   ➕ NUEVOS: {len(nuevos)} archivo(s)")
                for name in sorted(nuevos)[:5]:
                    print(f"      • {name}")
                if len(nuevos) > 5:
                    print(f"      ... y {len(nuevos) - 5} más")

            if eliminados:
                print(f"   ❌ ELIMINADOS: {len(eliminados)} archivo(s)")
                for name in sorted(eliminados)[:5]:
                    print(f"      • {name}")
                if len(eliminados) > 5:
                    print(f"      ... y {len(eliminados) - 5} más")
            print()

            existing_data = None
            if self.json_path.exists():
                with open(self.json_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

            data = self.sync_and_generate_json(all_names, existing_data)
            self.save_json(data)

            existing_assets_data = None
            if self.assets_json_path.exists():
                with open(self.assets_json_path, "r", encoding="utf-8") as f:
                    existing_assets_data = json.load(f)
            assets_data = self.sync_and_generate_assets_json(data, existing_assets_data)
            self.save_assets_json(assets_data)

            existing_brands_data = None
            if self.brands_json_path.exists():
                with open(self.brands_json_path, "r", encoding="utf-8") as f:
                    existing_brands_data = json.load(f)
            brands_data = self.sync_and_generate_brands_json(data, existing_brands_data)
            self.save_brands_json(brands_data)

            old_ids = {i.get("id") for i in (existing_data or {}).get("instruments", []) if i.get("id")}
            new_ids = {i.get("id") for i in data.get("instruments", []) if i.get("id")}
            added_ids = sorted(new_ids - old_ids)
            removed_ids = sorted(old_ids - new_ids)

            current_hash = self.calculate_files_hash(all_names)
            metadata.update(
                {
                    "last_count": len(all_names),
                    "last_hash": current_hash,
                    "last_sync": datetime.now().isoformat(),
                    "files_processed": all_names,
                    "added_count": metadata.get("added_count", 0) + len(added_ids),
                    "new_ids_last_run": added_ids,
                    "removed_ids_last_run": removed_ids,
                    "total_bases": data["total_bases"],
                    "total_variantes": data["total_variantes"],
                    "total_fotos": data["total_fotos"],
                    "total_instruments": data["total_instruments"],
                    "marcas_habilitadas": data["marcas_habilitadas"],
                    "marcas_no_habilitadas": data["marcas_no_habilitadas"],
                    "assets_total_instruments": assets_data["total_instruments"],
                    "assets_legacy_archived_count": assets_data["legacy_archived_count"],
                    "brands_total_habilitadas": len(brands_data.get("brands", [])),
                    "status": "updated" if (added_ids or removed_ids or nuevos or eliminados) else "synced",
                }
            )
            self.save_metadata(metadata)

            print("=" * 100)
            print("✅ SINCRONIZACIÓN EXITOSA")
            print("=" * 100)
            print(f"\n✓ Bases identificados: {data['total_bases']}")
            print(f"✓ Variantes identificadas: {data['total_variantes']}")
            print(f"✓ Total de fotos procesadas: {data['total_fotos']}")
            print(f"✓ JSON generado con {len(data['instruments'])} instrumentos")
            print(f"✓ Marcas habilitadas (con logo): {len(data['marcas_habilitadas'])}")
            print(f"✓ Marcas NO habilitadas (sin logo): {len(data['marcas_no_habilitadas'])}")
            print(f"✓ Validación fotos JSON/carpeta: {data['validacion']['coinciden']}")
            print(f"✓ Dataset legado actualizado: {assets_data['total_instruments']} instrumentos")
            print(f"✓ Legacy archivado (no borrado): {assets_data['legacy_archived_count']}")
            print(f"✓ Marcas JSON actualizadas: {len(brands_data.get('brands', []))}")
            print(f"✓ Metadatos guardados (próxima ejecución será más rápida)\n")

            return 0
        except Exception as e:
            print(f"\n❌ ERROR: {e}", flush=True)
            import traceback

            traceback.print_exc()
            return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza instrumentos desde /public/images/instrumentos")
    parser.add_argument("--force", "-f", action="store_true", help="Forzar resincronización")
    parser.add_argument(
        "--expected-fotos",
        type=int,
        default=DEFAULT_EXPECTED_FOTOS,
        help="Cantidad base esperada de fotos para validación (informativa)",
    )
    args = parser.parse_args()

    workspace_root = Path(__file__).parent.parent
    syncer = InstrumentSyncer(str(workspace_root), expected_fotos=args.expected_fotos)
    return syncer.run(force_sync=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
