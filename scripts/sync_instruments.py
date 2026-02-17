#!/usr/bin/env python3
"""
SYNC INSTRUMENTS - LITERAL + AUTO
Lee exactamente lo que existe en public/images/instrumentos/*.webp y genera src/data/instruments.json.
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

            nuevos, eliminados, cambio = self.detect_changes(all_names, metadata)
            if not cambio and not force_sync:
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
