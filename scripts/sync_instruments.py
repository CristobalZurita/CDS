#!/usr/bin/env python3
"""
Sincronizador automático de instrumentos - ADITIVO
Audita /public/images/instrumentos/ y actualiza instruments.json
Diseñado para auto-cargar nuevos instrumentos sin intervención manual
IMPORTANTE: Solo AÑADE nuevos, NUNCA elimina existentes (aditivo puro)
"""

import json
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

class InstrumentSyncer:
    """Sincroniza instrumentos de forma aditiva (solo añade, nunca quita)"""
    
    # Variantes de fotos (orden importa: más específicas primero)
    VARIANTS = [
        '_BACK', '_FRONT', '_TOP', '_LATERAL', '_SIDE',
        '_MK1', '_MK2', '_MK3', '_MK4', '_MK5',
        '_XL', '_S', '_PLUS', '_PRO', '_LITE',
        '_DELUXE', '_STANDARD', '_COMPACT',
        '_V1', '_V2', '_V3', '_VINTAGE', '_MODERN',
        '_BLACK', '_WHITE', '_SILVER', '_GOLD',
        '_RACK', '_A', '_B', '_C', '_D', '_E', '_F', '_2A', '_2R'
    ]
    
    # Template para nuevos instrumentos
    INSTRUMENT_TEMPLATE = {
        "type": "Keyboard / Synthesizer",
        "year": 2024,
        "description": "Sintetizador",
        "components": {
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
            "pedal": True
        },
        "valor_estimado": {
            "min": 300000,
            "max": 1500000,
            "moneda": "CLP"
        },
        "fallas_comunes": [
            "POWER",
            "CONNECTOR_LOOSE",
            "COSMETIC_DAMAGE",
            "WATER_DAMAGE",
            "KEYBOARD_DEAD_KEY",
            "KEYBOARD_STUCK_KEY",
            "ENCODER_INTERMITTENT",
            "BUTTON_DEAD"
        ],
        "manual_url": None,
        "image": {
            "url": None,
            "status": "pending"
        }
    }

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.images_dir = self.workspace_root / "public" / "images" / "instrumentos"
        self.json_path = self.workspace_root / "src" / "assets" / "data" / "instruments.json"

    def extract_base_instrument(self, filename: str) -> str:
        """
        Extrae nombre base eliminando variantes
        Ej: KORG_MICROKORG_MK1.webp → KORG_MICROKORG
        """
        name = filename.upper()
        
        for variant in sorted(self.VARIANTS, key=len, reverse=True):
            if name.endswith(variant):
                return name[:-len(variant)]
        
        return name

    def get_photo_files(self) -> Set[str]:
        """Obtiene todos los archivos .webp base únicos (sin variantes)"""
        if not self.images_dir.exists():
            print(f"❌ Directorio no encontrado: {self.images_dir}")
            return set()
        
        files = set()
        for webp_file in self.images_dir.glob("*.webp"):
            # Excluir logos
            if "logo" not in webp_file.name.lower():
                base_name = self.extract_base_instrument(webp_file.name)
                files.add(base_name)
        
        return files

    def get_json_instruments(self) -> Dict[str, dict]:
        """Carga instrumentos del JSON actual"""
        if not self.json_path.exists():
            return {}
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            inst.get('photo_key'): inst
            for inst in data.get('instruments', [])
            if inst.get('photo_key')
        }

    @staticmethod
    def photo_key_to_id(photo_key: str) -> str:
        """Convierte BRAND_MODEL a brand-model"""
        return photo_key.lower().replace('_', '-')

    @staticmethod
    def photo_key_to_brand_model(photo_key: str) -> Tuple[str, str]:
        """Extrae (brand, model) de photo_key"""
        parts = photo_key.split('_', 1)
        if len(parts) == 2:
            return parts[0].lower(), parts[1]
        return photo_key.lower(), photo_key

    def create_new_instrument(self, photo_key: str) -> dict:
        """Crea nuevo instrumento para una photo_key"""
        brand, model = self.photo_key_to_brand_model(photo_key)
        
        instrument = self.INSTRUMENT_TEMPLATE.copy()
        instrument.update({
            "id": self.photo_key_to_id(photo_key),
            "brand": brand,
            "model": model,
            "imagen_url": f"/images/instrumentos/{photo_key}.webp",
            "photo_key": photo_key
        })
        
        return instrument

    def sync_instruments(self) -> Tuple[int, int, list]:
        """
        Sincroniza instrumentos (ADITIVO):
        - Mantiene TODOS los existentes
        - Añade SOLO los nuevos no en JSON
        - NUNCA elimina nada
        
        Retorna: (mantenidos, añadidos, lista_de_nuevos)
        """
        photo_files = self.get_photo_files()
        json_instruments = self.get_json_instruments()
        
        # ADITIVO: mantener todo
        synced = dict(json_instruments)
        
        new_instruments = []
        for photo_key in sorted(photo_files):
            if photo_key not in json_instruments:
                synced[photo_key] = self.create_new_instrument(photo_key)
                new_instruments.append(photo_key)
        
        # Guardar JSON actualizado
        instruments_list = list(synced.values())
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(
                {"instruments": instruments_list},
                f,
                indent=2,
                ensure_ascii=False
            )
        
        return len(json_instruments), len(new_instruments), new_instruments

    def generate_report(self):
        """Genera reporte detallado de sincronización"""
        photo_files = self.get_photo_files()
        json_instruments = self.get_json_instruments()
        
        print("\n" + "="*80)
        print("📊 SINCRONIZADOR AUTOMÁTICO DE INSTRUMENTOS")
        print("="*80)
        
        print(f"\n📷 Archivos WEBP base en disco: {len(photo_files)}")
        print(f"📋 Instrumentos en JSON: {len(json_instruments)}")
        
        # Analizar diferencias
        in_disk = set(photo_files)
        in_json = set(json_instruments.keys())
        
        new_in_disk = in_disk - in_json
        missing_in_disk = in_json - in_disk
        
        # Realizar sincronización
        kept, added, new_list = self.sync_instruments()
        
        print(f"\n✨ Operación ADITIVA:")
        print(f"   ✅ Instrumentos mantenidos: {kept}")
        print(f"   ➕ Instrumentos añadidos: {added}")
        print(f"   📊 Total final: {kept + added}")
        
        if new_list and len(new_list) <= 20:
            print(f"\n📝 Nuevos instrumentos añadidos:")
            for item in new_list:
                print(f"   • {item}")
        elif new_list:
            print(f"\n📝 Primeros 10 nuevos instrumentos:")
            for item in new_list[:10]:
                print(f"   • {item}")
            print(f"   ... y {len(new_list) - 10} más")
        
        if missing_in_disk:
            print(f"\n⚠️  Instrumentos en JSON sin foto en disco ({len(missing_in_disk)}):")
            for item in sorted(missing_in_disk):
                print(f"   - {item}")
        
        print("\n" + "="*80 + "\n")

def main():
    workspace_root = Path(__file__).parent.parent
    syncer = InstrumentSyncer(str(workspace_root))
    
    print("🔄 Sincronizando instrumentos (ADITIVO)...")
    syncer.generate_report()

if __name__ == "__main__":
    main()
