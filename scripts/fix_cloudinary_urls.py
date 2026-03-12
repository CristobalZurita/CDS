#!/usr/bin/env python3
"""
Repara image-mapping.json con URLs correctas de Cloudinary (con número de versión)
ADITIVO: Solo actualiza el JSON, no modifica código fuente
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import shutil

CLOUD_NAME = 'dgwwi77ic'
BASE_DIR = Path(__file__).parent.parent
IMAGE_MAPPING_PATH = BASE_DIR / "image-mapping.json"
BACKUP_PATH = BASE_DIR / f"image-mapping.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def get_cloudinary_client():
    """Obtiene cliente Cloudinary configurado."""
    try:
        import cloudinary
        import cloudinary.api
        
        api_key = os.getenv('CLOUDINARY_API_KEY', '')
        api_secret = os.getenv('CLOUDINARY_API_SECRET', '')
        
        if not api_key or not api_secret:
            return None, "Faltan CLOUDINARY_API_KEY o CLOUDINARY_API_SECRET"
        
        cloudinary.config(
            cloud_name=CLOUD_NAME,
            api_key=api_key,
            api_secret=api_secret
        )
        return cloudinary, None
    except ImportError:
        return None, "pip install cloudinary"


def fetch_cloudinary_images():
    """Obtiene todas las imágenes de Cloudinary."""
    client, error = get_cloudinary_client()
    if not client:
        return None, error
    
    import cloudinary.api
    
    images = {}
    next_cursor = None
    
    try:
        while True:
            result = cloudinary.api.resources(
                type="upload",
                resource_type="image",
                max_results=500,
                next_cursor=next_cursor
            )
            
            for resource in result.get("resources", []):
                public_id = resource.get("public_id", "")
                url = resource.get("secure_url", "")
                
                # Indexar por public_id completo
                images[public_id.lower()] = url
                
                # Indexar por nombre de archivo
                filename = public_id.split('/')[-1]
                images[filename.lower()] = url
            
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break
        
        return images, None
        
    except Exception as e:
        return None, str(e)


def load_mapping():
    """Carga el mapeo actual."""
    with open(IMAGE_MAPPING_PATH, 'r') as f:
        return json.load(f)


def save_mapping(mapping):
    """Guarda el mapeo actualizado."""
    with open(IMAGE_MAPPING_PATH, 'w') as f:
        json.dump(mapping, f, indent=2)


def find_cloudinary_url(local_path, cloudinary_images):
    """Busca la URL de Cloudinary para una ruta local."""
    # Extraer nombre de archivo
    filename = local_path.split('/')[-1] if '/' in local_path else local_path
    name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
    
    # Buscar por nombre de archivo
    if name_without_ext.lower() in cloudinary_images:
        return cloudinary_images[name_without_ext.lower()]
    
    # Buscar con variaciones de ruta
    path_variations = [
        local_path.lstrip('/'),  # images/instrumentos/ACCESS_VIRUS_A.webp
        local_path.lstrip('/').replace('/', '_'),  # images_instrumentos_ACCESS_VIRUS_A.webp
        name_without_ext,  # ACCESS_VIRUS_A
    ]
    
    for variation in path_variations:
        if variation.lower() in cloudinary_images:
            return cloudinary_images[variation.lower()]
    
    return None


def fix_urls():
    """Repara las URLs en el mapeo."""
    print("=" * 80)
    print("🔧 REPARACIÓN DE URLs CLOUDINARY")
    print("=" * 80)
    print()
    
    # Obtener imágenes de Cloudinary
    print("☁️  Conectando a Cloudinary...")
    cloudinary_images, error = fetch_cloudinary_images()
    
    if not cloudinary_images:
        print(f"❌ Error: {error}")
        print()
        print("Para reparar, necesitas:")
        print("  export CLOUDINARY_API_KEY=tu_api_key")
        print("  export CLOUDINARY_API_SECRET=tu_api_secret")
        return False
    
    print(f"   ✅ {len(cloudinary_images)} imágenes obtenidas")
    print()
    
    # Cargar mapeo
    print("📂 Cargando image-mapping.json...")
    mapping = load_mapping()
    print(f"   {len(mapping)} entradas")
    print()
    
    # Backup
    print("💾 Creando backup...")
    shutil.copy2(IMAGE_MAPPING_PATH, BACKUP_PATH)
    print(f"   {BACKUP_PATH.name}")
    print()
    
    # Reparar
    print("🔧 Reparando URLs...")
    fixed = 0
    not_found = []
    
    for item in mapping:
        local_path = item.get('local', '')
        old_url = item.get('cloudinary', '')
        
        # Buscar URL correcta
        correct_url = find_cloudinary_url(local_path, cloudinary_images)
        
        if correct_url:
            if old_url != correct_url:
                item['cloudinary'] = correct_url
                item['altUrl'] = correct_url
                fixed += 1
                
                # Mostrar cambio
                filename = local_path.split('/')[-1]
                print(f"   ✅ {filename}")
                print(f"      Antes:  {old_url[:65]}...")
                print(f"      Después: {correct_url[:65]}...")
        else:
            not_found.append(local_path)
            filename = local_path.split('/')[-1]
            print(f"   ⚠️  No encontrada: {filename}")
    
    print()
    print("-" * 80)
    print(f"Resultado: {fixed} URLs reparadas, {len(not_found)} no encontradas")
    print("-" * 80)
    print()
    
    # Guardar
    if fixed > 0:
        print("💾 Guardando...")
        save_mapping(mapping)
        print("   ✅ Guardado")
    
    if not_found:
        print()
        print("⚠️  Imágenes no encontradas en Cloudinary:")
        for path in not_found[:10]:
            print(f"   - {path}")
        if len(not_found) > 10:
            print(f"   ... y {len(not_found) - 10} más")
    
    return True


def main():
    try:
        fix_urls()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por usuario")
        sys.exit(1)


if __name__ == "__main__":
    main()
