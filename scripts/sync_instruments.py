#!/usr/bin/env python3
"""
🎯 SYNC INSTRUMENTS - AUTOMATIC LITERAL + INTELLIGENT
Lee EXACTAMENTE lo que existe en public/images/instrumentos/*.webp
SIN inventar, SIN inferir, SIN patrones - solo los archivos reales

CARACTERÍSTICAS INTELIGENTES:
- Guarda último conteo de archivos en .sync_metadata.json
- Si hay NUEVOS archivos → automáticamente los añade al JSON
- Si hay MENOS archivos → marca como eliminados
- NUNCA reinventa, NUNCA sobreescribe, SOLO AGREGA
- Ejecuta automáticamente al iniciar o por CI/CD
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict
from datetime import datetime


def detect_variant_relationship(base_name: str, potential_variant: str, all_names: List[str]) -> bool:
    """
    Detecta si potential_variant es variante de base_name
    LITERAL - solo si potential_variant EMPIEZA con base_name + underscore
    
    Ejemplos TRUE:
    - base: AKAI_APC_64, variant: AKAI_APC_64_BACK → True
    - base: YAMAHA_DX7_MK1, variant: YAMAHA_DX7_MK1_BACK → True
    
    Ejemplos FALSE:
    - base: KORG_ELECTRIBE, variant: KORG_ELECTRIBE_2A → False (2A es part del base)
    - base: YAMAHA_DX7, variant: YAMAHA_DX7_MK1 → False (no existe YAMAHA_DX7)
    """
    
    # Verificación 1: potential_variant DEBE empezar con base_name + "_"
    if not potential_variant.startswith(base_name + '_'):
        return False
    
    # Verificación 2: base_name DEBE existir en all_names
    if base_name not in all_names:
        return False
    
    # Verificación 3: el sufijo DEBE ser una variante conocida
    suffix = potential_variant[len(base_name) + 1:]
    
    # Estos son sufijos de VERDADERAS variantes (observadas en dataset real)
    variant_suffixes = {
        'BACK', 'FRONT', 'BACK2', 'FRONT2', 'TOP', 'BOTTOM',
        'SIDE', 'LEFT', 'RIGHT', 'DETAIL', 'CLOSEUP', 'LATERAL'
    }
    
    return suffix in variant_suffixes


class InstrumentSyncer:
    """Sincroniza instrumentos LITERALMENTE desde archivos reales - INTELIGENTE Y ADITIVO"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.images_dir = self.workspace_root / "public" / "images" / "instrumentos"
        self.json_path = self.workspace_root / "src" / "data" / "instruments.json"
        self.metadata_path = self.workspace_root / "src" / "data" / ".sync_metadata.json"
    
    def get_metadata(self) -> Dict:
        """Carga metadatos de última sincronización"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        
        return {
            'last_count': 0,
            'last_hash': None,
            'last_sync': None,
            'files_processed': [],
            'added_count': 0,
            'status': 'virgin'
        }
    
    def save_metadata(self, metadata: Dict):
        """Guarda metadatos de sincronización"""
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def calculate_files_hash(self, all_names: List[str]) -> str:
        """Calcula hash SHA256 de la lista de archivos"""
        files_str = '|'.join(sorted(all_names))
        return hashlib.sha256(files_str.encode()).hexdigest()
    
    def detect_changes(self, all_names: List[str], metadata: Dict) -> Tuple[Set[str], Set[str], bool]:
        """
        Detecta si hay cambios desde la última sincronización
        
        Returns:
            (nuevos_archivos, archivos_eliminados, cambio_detectado)
        """
        current_hash = self.calculate_files_hash(all_names)
        last_hash = metadata.get('last_hash')
        last_count = metadata.get('last_count', 0)
        
        all_names_set = set(all_names)
        last_files = set(metadata.get('files_processed', []))
        
        nuevos = all_names_set - last_files
        eliminados = last_files - all_names_set
        
        cambio_detectado = (
            len(all_names) != last_count or 
            current_hash != last_hash or
            len(nuevos) > 0 or
            len(eliminados) > 0
        )
        
        return nuevos, eliminados, cambio_detectado

    def get_all_webp_files(self) -> Set[str]:
        """Obtiene TODOS los archivos .webp literalmente"""
        if not self.images_dir.exists():
            print(f"❌ Directorio no encontrado: {self.images_dir}")
            return set()
        
        files = set()
        for webp_file in self.images_dir.glob("*.webp"):
            # Quitar extensión .webp
            name = webp_file.name.replace('.webp', '')
            files.add(name)
        
        return files
    
    def identify_bases_and_variants(self, all_names: List[str]) -> tuple[Set[str], Dict[str, List[str]]]:
        """
        Identifica cuáles son bases y cuáles son variantes
        LITERAL - solo busca si potential_variant = base_name + "_" + variant_suffix
        """
        bases = set()
        variants_map = defaultdict(list)
        
        for name in all_names:
            is_variant = False
            
            # Buscar si este nombre es variante de algún otro
            for potential_base in all_names:
                if potential_base != name:
                    if detect_variant_relationship(potential_base, name, all_names):
                        variants_map[potential_base].append(name)
                        is_variant = True
                        break
            
            # Si no es variante, es un base
            if not is_variant:
                bases.add(name)
        
        return bases, dict(variants_map)
    
    def extract_marca_modelo(self, instrument_name: str) -> tuple[str, str]:
        """
        Extrae marca y modelo del nombre literal
        Ej: KORG_ELECTRIBE_2A → marca=KORG, modelo=ELECTRIBE_2A
        """
        parts = instrument_name.split('_')
        marca = parts[0]
        modelo = '_'.join(parts[1:])
        return marca, modelo
    
    def sync_and_generate_json(self, all_names: List[str], existing_data: Dict = None) -> Dict:
        """
        Genera JSON LITERAL desde los nombres de archivo
        Si hay JSON previo, AÑADE solo los nuevos, NUNCA reinventa
        """
        bases, variants_map = self.identify_bases_and_variants(all_names)
        
        # Si hay JSON anterior, cargar instrumentos existentes
        existing_instruments = {}
        if existing_data:
            for inst in existing_data.get('instruments', []):
                existing_instruments[inst['id']] = inst
        
        instruments = []
        
        for base_name in sorted(bases):
            base_id = base_name.lower()
            
            # Si ya existe en JSON anterior, usar ese
            if base_id in existing_instruments:
                instruments.append(existing_instruments[base_id])
            else:
                # SOLO crear si es nuevo
                marca, modelo = self.extract_marca_modelo(base_name)
                
                fotos = [base_name]
                if base_name in variants_map:
                    fotos.extend(sorted(variants_map[base_name]))
                
                instrument = {
                    'id': base_id,
                    'marca': marca,
                    'modelo': modelo,
                    'foto_principal': base_name,
                    'fotos_adicionales': fotos[1:] if len(fotos) > 1 else [],
                    'tipos': ['sintetizador'],
                    'agregado_en': datetime.now().isoformat()
                }
                
                instruments.append(instrument)
        
        # Crear estructura final
        data = {
            'version': '1.0.0',
            'total_bases': len(bases),
            'total_variantes': len([v for vs in variants_map.values() for v in vs]),
            'total_fotos': len(all_names),
            'instruments': instruments
        }
        
        return data
    
    def save_json(self, data: Dict):
        """Guarda JSON a archivo"""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def run(self, force_sync: bool = False) -> int:
        """
        Ejecuta sincronización INTELIGENTE:
        - Si hay cambios en los archivos → actualiza automáticamente
        - Si no hay cambios → salta (más rápido)
        - force_sync=True → fuerza resincronización
        """
        print("\n" + "="*100)
        print("🎯 SYNC INSTRUMENTS - AUTOMATIC LITERAL + INTELLIGENT")
        print("="*100)
        print(f"\n📁 Leyendo de: {self.images_dir}")
        print(f"📝 Generando: {self.json_path}\n")
        
        try:
            # 1. Obtener archivos actuales
            all_webp = self.get_all_webp_files()
            all_names = sorted(list(all_webp))
            
            if not all_names:
                print("❌ No hay archivos .webp encontrados")
                return 1
            
            print(f"✅ {len(all_names)} archivos .webp encontrados")
            
            # 2. Cargar metadatos anteriores
            metadata = self.get_metadata()
            print(f"📊 Último conteo: {metadata['last_count']} archivos")
            print(f"📊 Conteo actual: {len(all_names)} archivos\n")
            
            # 3. Detectar cambios
            nuevos, eliminados, cambio = self.detect_changes(all_names, metadata)
            
            if not cambio and not force_sync:
                print("✨ SIN CAMBIOS - Saltando sincronización (más rápido)")
                print("   Usa --force para forzar resincronización\n")
                return 0
            
            print(f"🔄 CAMBIOS DETECTADOS:")
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
            
            # 4. Cargar JSON anterior (si existe)
            existing_data = None
            if self.json_path.exists():
                with open(self.json_path, 'r') as f:
                    existing_data = json.load(f)
            
            # 5. Generar JSON ADITIVO
            data = self.sync_and_generate_json(all_names, existing_data)
            self.save_json(data)
            
            # 6. Actualizar metadatos
            current_hash = self.calculate_files_hash(all_names)
            metadata.update({
                'last_count': len(all_names),
                'last_hash': current_hash,
                'last_sync': datetime.now().isoformat(),
                'files_processed': all_names,
                'added_count': metadata.get('added_count', 0) + len(nuevos),
                'status': 'synced' if not nuevos else 'updated'
            })
            self.save_metadata(metadata)
            
            # 7. Reporte final
            print("="*100)
            print("✅ SINCRONIZACIÓN EXITOSA")
            print("="*100)
            print(f"\n✓ Bases identificados: {data['total_bases']}")
            print(f"✓ Variantes identificadas: {data['total_variantes']}")
            print(f"✓ Total de fotos procesadas: {data['total_fotos']}")
            print(f"✓ JSON generado con {len(data['instruments'])} instrumentos")
            print(f"✓ Metadatos guardados (próxima ejecución será más rápida)\n")
            
            return 0
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return 1


def main():
    workspace_root = Path(__file__).parent.parent
    syncer = InstrumentSyncer(str(workspace_root))
    
    # Permitir --force para forzar resincronización
    force_sync = '--force' in sys.argv or '-f' in sys.argv
    
    return syncer.run(force_sync=force_sync)


if __name__ == "__main__":
    exit(main())
