#!/usr/bin/env python3
"""
Sincronizador EXACTO de Instrumentos
- Lee SOLO las fotos que existen en la carpeta
- Filtra SOLO marcas con LOGO
- Genera JSON limpio y correcto
"""

import os
import json
from pathlib import Path
from collections import defaultdict

# Rutas
PHOTOS_DIR = Path("public/images/instrumentos")
LOGOS_DIR = PHOTOS_DIR / "LOGOS"
JSON_FILE = Path("src/data/instruments.json")

# Marcas válidas (tienen LOGO)
VALID_BRANDS = {
    "ACCESS", "AKAI", "ALESIS", "ARP", "ARTURIA", "ASM",
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
    "SEQUENTIAL", "SIEL", "STUDIOLOGIC",
    "WALDORF",
    "YAMAHA"
}

def get_valid_logos():
    """Leer logos disponibles"""
    logos = set()
    if LOGOS_DIR.exists():
        for file in LOGOS_DIR.glob("LOGO_*.webp"):
            match = file.stem.replace("LOGO_", "")
            logos.add(match)
        for file in LOGOS_DIR.glob("LOGO_*.svg"):
            match = file.stem.replace("LOGO_", "")
            logos.add(match)
    return logos

def get_all_photos():
    """Leer todas las fotos disponibles"""
    photos = []
    if PHOTOS_DIR.exists():
        for file in sorted(PHOTOS_DIR.glob("*.webp")):
            photos.append(file.stem)
    return photos

def group_instruments(photos):
    """
    Agrupar fotos por instrumento base.
    
    CASIO_CZ_101.webp + CASIO_CZ_101_BACK.webp 
    → instrumento: CASIO_CZ_101, fotos: [CASIO_CZ_101, CASIO_CZ_101_BACK]
    """
    instruments = defaultdict(list)
    
    for photo in photos:
        # Extraer base: todo antes de _BACK, _LATERAL, etc.
        if photo.endswith(("_BACK", "_LATERAL", "_FRONT", "_LADO", "_LADOS")):
            # Foto de variante
            for suffix in ("_BACK", "_LATERAL", "_FRONT", "_LADO", "_LADOS"):
                if photo.endswith(suffix):
                    base = photo[:-len(suffix)]
                    instruments[base].append(photo)
                    break
        else:
            # Foto base
            instruments[photo].append(photo)
    
    return dict(instruments)

def build_json(instruments, valid_logos):
    """Construir JSON final"""
    data = {
        "version": "2.0.0",
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
        
        # Validar marca tiene LOGO
        if brand not in valid_logos:
            print(f"⚠️  Ignorando {base_name}: marca {brand} sin LOGO")
            continue
        
        # Validar que existe foto_principal
        if base_name not in photos:
            print(f"⚠️  Ignorando {base_name}: falta foto principal")
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

def main():
    print("🔄 Sincronizando instrumentos...")
    
    # Obtener logos válidos
    valid_logos = get_valid_logos()
    print(f"📍 {len(valid_logos)} marcas con LOGO encontradas")
    
    # Obtener todas las fotos
    all_photos = get_all_photos()
    print(f"📷 {len(all_photos)} fotos encontradas")
    
    # Agrupar por instrumento
    instruments = group_instruments(all_photos)
    print(f"🎹 {len(instruments)} instrumentos (base) identificados")
    
    # Construir JSON
    data = build_json(instruments, valid_logos)
    
    # Guardar
    JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Listo!")
    print(f"   - Instrumentos: {data['total_instruments']}")
    print(f"   - Fotos totales: {data['total_fotos']}")
    print(f"   - Archivo: {JSON_FILE}")

if __name__ == "__main__":
    main()
