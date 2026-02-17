#!/usr/bin/env python3
"""
🔄 Auto-Sync de Instrumentos - AUTOMÁTICO
Ejecuta sincronización automática varias veces al día
- Detecta fotos nuevas
- Detecta fotos eliminadas
- Regenera JSON
- Se ejecuta automáticamente varias veces al día
"""

import os
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Rutas
PHOTOS_DIR = Path("public/images/instrumentos")
LOGOS_DIR = PHOTOS_DIR / "LOGOS"
JSON_FILE = Path("src/data/instruments.json")
METADATA_FILE = Path("src/data/.sync_metadata.json")

# Marcas válidas (tienen LOGO)
VALID_BRANDS = {
    "ACCESS", "AKAI", "ALESIS", "ARP", "ARTURIA",
    "BEHERINGER", "BOSS",
    "CASIO",
    "DAVESMITH", "DOEPFER",
    "ELECTRO_HARMONIX", "ENSONIQ",
    "KAWAI", "KORG", "KURZWEIL",
    "M_AUDIO", "MOOG", "MXR",
    "NORD", "NOVATION",
    "OBERHEIM",
    "PEAVEY",
    "ROLAND",
    "SEQUENTIAL", "SIEL",
    "WALDORF",
    "YAMAHA"
}

def get_all_photos():
    """Leer todas las fotos disponibles"""
    photos = []
    if PHOTOS_DIR.exists():
        for file in sorted(PHOTOS_DIR.glob("*.webp")):
            photos.append(file.stem)
    return photos

def get_directory_hash(photos_list):
    """Calcular hash de la lista de fotos"""
    content = "\n".join(sorted(photos_list))
    return hashlib.sha256(content.encode()).hexdigest()

def group_instruments(photos):
    """Agrupar fotos por instrumento base"""
    instruments = defaultdict(list)
    
    for photo in photos:
        # Extraer base: todo antes de _BACK, _LATERAL, etc.
        if photo.endswith(("_BACK", "_LATERAL", "_FRONT", "_LADO", "_LADOS")):
            for suffix in ("_BACK", "_LATERAL", "_FRONT", "_LADO", "_LADOS"):
                if photo.endswith(suffix):
                    base = photo[:-len(suffix)]
                    instruments[base].append(photo)
                    break
        else:
            instruments[photo].append(photo)
    
    return dict(instruments)

def build_json(instruments):
    """Construir JSON final"""
    data = {
        "version": "2.0.0",
        "generated_at": datetime.now().isoformat(),
        "total_instruments": 0,
        "total_fotos": 0,
        "instruments": []
    }
    
    total_fotos = 0
    
    for base_name in sorted(instruments.keys()):
        photos = instruments[base_name]
        
        # Extraer marca
        parts = base_name.split("_")
        brand = parts[0]
        
        # Validar marca
        if brand not in VALID_BRANDS:
            logger.debug(f"Ignorando {base_name}: marca {brand} sin LOGO")
            continue
        
        # Validar foto_principal
        if base_name not in photos:
            logger.debug(f"Ignorando {base_name}: falta foto principal")
            continue
        
        # Construir entrada
        modelo = "_".join(parts[1:]) if len(parts) > 1 else base_name
        fotos_adicionales = sorted([p for p in photos if p != base_name])
        
        entry = {
            "id": base_name.lower(),
            "marca": brand,
            "modelo": modelo,
            "foto_principal": base_name,
            "fotos_adicionales": fotos_adicionales,
            "tipos": ["sintetizador"]
        }
        
        data["instruments"].append(entry)
        total_fotos += 1 + len(fotos_adicionales)
    
    data["total_instruments"] = len(data["instruments"])
    data["total_fotos"] = total_fotos
    
    return data

def load_metadata():
    """Cargar metadata anterior"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"last_hash": None, "last_count": 0, "last_sync": None}
    return {"last_hash": None, "last_count": 0, "last_sync": None}

def save_metadata(metadata):
    """Guardar metadata"""
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def sync(force=False):
    """
    Sincronizar instrumentos automáticamente.
    
    Retorna:
        {
            "synced": bool,
            "instruments": int,
            "fotos": int,
            "message": str
        }
    """
    logger.info("=" * 60)
    logger.info("🔄 INICIANDO SINCRONIZACIÓN AUTOMÁTICA")
    logger.info("=" * 60)
    
    # Validar directorios
    if not PHOTOS_DIR.exists():
        logger.error(f"❌ Directorio de fotos no existe: {PHOTOS_DIR}")
        return {"synced": False, "instruments": 0, "fotos": 0, "message": "Directorio no existe"}
    
    # Obtener fotos actuales
    all_photos = get_all_photos()
    current_hash = get_directory_hash(all_photos)
    logger.info(f"📷 {len(all_photos)} fotos detectadas")
    
    # Cargar metadata anterior
    metadata = load_metadata()
    last_hash = metadata.get("last_hash")
    last_count = metadata.get("last_count", 0)
    
    # Verificar si hay cambios
    if not force and current_hash == last_hash:
        logger.info(f"✓ Sin cambios detectados. Hash coincide.")
        logger.info(f"  Última sincronización: {metadata.get('last_sync', 'Nunca')}")
        return {
            "synced": False,
            "instruments": metadata.get("total_instruments", 0),
            "fotos": metadata.get("total_fotos", 0),
            "message": "Sin cambios"
        }
    
    # Detectar cambios
    if last_count != len(all_photos):
        difference = len(all_photos) - last_count
        if difference > 0:
            logger.info(f"➕ {difference} foto(s) nueva(s) detectada(s)!")
        else:
            logger.info(f"➖ {abs(difference)} foto(s) eliminada(s)!")
    
    logger.info(f"🔄 Regenerando JSON...")
    
    # Agrupar instrumentos
    instruments = group_instruments(all_photos)
    logger.info(f"🎹 {len(instruments)} instrumentos base identificados")
    
    # Construir JSON
    data = build_json(instruments)
    
    # Guardar JSON
    JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✅ JSON guardado: {JSON_FILE}")
    
    # Actualizar metadata
    metadata["last_hash"] = current_hash
    metadata["last_count"] = len(all_photos)
    metadata["total_instruments"] = data["total_instruments"]
    metadata["total_fotos"] = data["total_fotos"]
    metadata["last_sync"] = datetime.now().isoformat()
    save_metadata(metadata)
    
    logger.info(f"📊 Resultado final:")
    logger.info(f"   - Instrumentos: {data['total_instruments']}")
    logger.info(f"   - Fotos totales: {data['total_fotos']}")
    logger.info(f"   - Última sincronización: {metadata['last_sync']}")
    logger.info("=" * 60)
    
    return {
        "synced": True,
        "instruments": data["total_instruments"],
        "fotos": data["total_fotos"],
        "message": f"✅ Sincronizado: {data['total_instruments']} instrumentos, {data['total_fotos']} fotos"
    }

if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    result = sync(force=force)
    print(json.dumps(result, indent=2))
