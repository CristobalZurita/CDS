#!/usr/bin/env python3
"""
Script para reparar image-mapping.json con URLs correctas de Cloudinary
Obtiene las URLs reales con números de versión desde la API de Cloudinary
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuración
CLOUD_NAME = 'dgwwi77ic'
BASE_DIR = Path(__file__).parent.parent
IMAGE_MAPPING_PATH = BASE_DIR / "image-mapping.json"
IMAGE_MAPPING_BACKUP = BASE_DIR / f"image-mapping.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def get_cloudinary_client():
    """Obtiene cliente Cloudinary configurado."""
    try:
        import cloudinary
        import cloudinary.api
        
        cloudinary.config(
            cloud_name=CLOUD_NAME,
            api_key=os.getenv('CLOUDINARY_API_KEY', ''),
            api_secret=os.getenv('CLOUDINARY_API_SECRET', '')
        )
        return cloudinary
    except ImportError:
        print("❌ Error: pip install cloudinary")
        sys.exit(1)


def fetch_all_cloudinary_images():
    """Obtiene todas las imágenes de Cloudinary con sus URLs reales."""
    client = get_cloudinary_client()
    if not client:
        return {}
    
    import cloudinary.api
    
    images = {}
    next_cursor = None
    
    print("☁️  Obteniendo imágenes de Cloudinary...")
    
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
                # Guardar por public_id completo y por nombre de archivo
                images[public_id] = {
                    "url": resource.get("secure_url"),
                    "public_id": public_id,
                    "format": resource.get("format"),
                }
                
                # También indexar por nombre de archivo sin extensión
                filename = public_id.split("/")[-1] if "/" in public_id else public_id
                images[filename.lower()] = images[public_id]
            
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break
        
        print(f"   ✅ {len(images)} imágenes obtenidas")
        return images
        
    except Exception as e:
        print(f"❌ Error al obtener imágenes: {e}")
        return {}


def load_image_mapping():
    """Carga el mapeo actual."""
    try:
        with open(IMAGE_MAPPING_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar image-mapping.json: {e}")
        return []


def save_image_mapping(mapping):
    """Guarda el mapeo actualizado."""
    try:
        with open(IMAGE_MAPPING_PATH, 'w') as f:
            json.dump(mapping, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error al guardar image-mapping.json: {e}")
        return False


def extract_path_info(local_path):
    """Extrae información de la ruta local."""
    # Ejemplo: /images/INVENTARIO/BOTON_ARCADE_3_2MM_NEGRO.webp
    parts = local_path.strip('/').split('/')
    
    if len(parts) >= 3 and parts[0] == 'images':
        folder = '/'.join(parts[1:-1])  # INVENTARIO
        filename = parts[-1]  # BOTON_ARCADE_3_2MM_NEGRO.webp
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        return {
            'full_path': local_path,
            'folder': folder,
            'filename': filename,
            'name_without_ext': name_without_ext,
            'public_id_patterns': [
                f"images/{folder}/{name_without_ext}",  # images/INVENTARIO/BOTON_ARCADE_3_2MM_NEGRO
                f"{folder}/{name_without_ext}",  # INVENTARIO/BOTON_ARCADE_3_2MM_NEGRO
                name_without_ext,  # BOTON_ARCADE_3_2MM_NEGRO
            ]
        }
    
    return None


def find_cloudinary_url(path_info, cloudinary_images):
    """Busca la URL de Cloudinary correspondiente."""
    filename = path_info['filename'].lower()
    name_without_ext = path_info['name_without_ext'].lower()
    
    # Buscar coincidencias exactas primero
    for pattern in path_info['public_id_patterns']:
        pattern_lower = pattern.lower()
        if pattern_lower in cloudinary_images:
            return cloudinary_images[pattern_lower]['url']
    
    # Buscar por nombre de archivo
    for key, img_data in cloudinary_images.items():
        if '/' not in key:  # Solo nombres sin path
            key_lower = key.lower()
            if key_lower == name_without_ext:
                return img_data['url']
            # Buscar con underscore (Cloudinary a veces añade _xxxxx)
            if key_lower.startswith(name_without_ext + '_'):
                return img_data['url']
    
    return None


def repair_mapping():
    """Repara el mapeo de imágenes."""
    print("=" * 80)
    print("🔧 REPARACIÓN DE IMAGE-MAPPING.JSON")
    print("=" * 80)
    print()
    
    # Verificar credenciales
    api_key = os.getenv('CLOUDINARY_API_KEY', '')
    api_secret = os.getenv('CLOUDINARY_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("❌ ERROR: Se requieren credenciales de Cloudinary")
        print()
        print("Configura las variables de entorno:")
        print("  export CLOUDINARY_API_KEY=tu_api_key")
        print("  export CLOUDINARY_API_SECRET=tu_api_secret")
        print()
        print("Obtén las credenciales en: https://cloudinary.com/console")
        sys.exit(1)
    
    # Cargar datos
    print("📂 Cargando mapeo actual...")
    local_mapping = load_image_mapping()
    print(f"   {len(local_mapping)} entradas encontradas")
    print()
    
    # Hacer backup
    print("💾 Creando backup...")
    import shutil
    shutil.copy2(IMAGE_MAPPING_PATH, IMAGE_MAPPING_BACKUP)
    print(f"   Backup guardado en: {IMAGE_MAPPING_BACKUP.name}")
    print()
    
    # Obtener imágenes de Cloudinary
    cloudinary_images = fetch_all_cloudinary_images()
    if not cloudinary_images:
        print("❌ No se pudieron obtener imágenes de Cloudinary")
        sys.exit(1)
    
    # Reparar mapeo
    print("🔧 Reparando URLs...")
    print()
    
    updated_count = 0
    not_found = []
    
    for item in local_mapping:
        local_path = item.get('local', '')
        old_url = item.get('cloudinary', '')
        
        # Extraer información de la ruta
        path_info = extract_path_info(local_path)
        if not path_info:
            print(f"   ⚠️  Ruta no válida: {local_path}")
            not_found.append(local_path)
            continue
        
        # Buscar URL correcta
        new_url = find_cloudinary_url(path_info, cloudinary_images)
        
        if new_url:
            if old_url != new_url:
                item['cloudinary'] = new_url
                item['altUrl'] = new_url
                updated_count += 1
                print(f"   ✅ {path_info['filename']}")
                print(f"      Antes: {old_url[:60]}...")
                print(f"      Después: {new_url[:60]}...")
        else:
            not_found.append(local_path)
            print(f"   ❌ No encontrada: {path_info['filename']}")
    
    print()
    print("=" * 80)
    print("RESUMEN:")
    print(f"  - Total procesadas: {len(local_mapping)}")
    print(f"  - URLs actualizadas: {updated_count}")
    print(f"  - No encontradas: {len(not_found)}")
    print("=" * 80)
    print()
    
    # Guardar resultado
    if updated_count > 0:
        print("💾 Guardando mapeo actualizado...")
        if save_image_mapping(local_mapping):
            print("   ✅ Guardado exitosamente")
        else:
            print("   ❌ Error al guardar")
    
    # Mostrar no encontradas
    if not_found:
        print()
        print("⚠️  IMÁGENES NO ENCONTRADAS EN CLOUDINARY:")
        for path in not_found[:20]:  # Mostrar primeras 20
            print(f"   - {path}")
        if len(not_found) > 20:
            print(f"   ... y {len(not_found) - 20} más")
        print()
        print("Estas imágenes necesitan ser subidas a Cloudinary primero.")


if __name__ == "__main__":
    repair_mapping()
