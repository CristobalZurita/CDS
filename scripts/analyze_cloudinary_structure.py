#!/usr/bin/env python3
"""
Análisis de la estructura real de imágenes en Cloudinary
ADITIVO: Solo diagnostica, no modifica nada
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

CLOUD_NAME = 'dgwwi77ic'
IMAGE_MAPPING_PATH = Path(__file__).parent.parent / "image-mapping.json"


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
        print("❌ pip install cloudinary")
        return None


def load_image_mapping():
    """Carga el mapeo actual."""
    try:
        with open(IMAGE_MAPPING_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  No se pudo cargar image-mapping.json: {e}")
        return []


def analyze_cloudinary_structure():
    """Analiza la estructura real de imágenes en Cloudinary."""
    client = get_cloudinary_client()
    if not client:
        print("⚠️  No se pudo conectar a Cloudinary (faltan credenciales)")
        return None
    
    import cloudinary.api
    
    print("☁️  Obteniendo imágenes de Cloudinary...")
    
    images = []
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
                url = resource.get("secure_url", "")
                public_id = resource.get("public_id", "")
                
                # Extraer versión de la URL
                # URL format: https://res.cloudinary.com/.../image/upload/v1234567890/path
                version = None
                if '/v' in url and '/upload/v' in url:
                    version_part = url.split('/upload/v')[1].split('/')[0]
                    if version_part.isdigit():
                        version = version_part
                
                images.append({
                    "public_id": public_id,
                    "url": url,
                    "version": version,
                    "format": resource.get("format"),
                })
            
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break
        
        return images
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_folders(images):
    """Analiza la estructura de carpetas."""
    folders = defaultdict(list)
    
    for img in images:
        public_id = img['public_id']
        if '/' in public_id:
            folder = public_id.rsplit('/', 1)[0]
        else:
            folder = '(root)'
        folders[folder].append(img)
    
    return folders


def compare_with_mapping(cloudinary_images, local_mapping):
    """Compara las imágenes de Cloudinary con el mapeo local."""
    print()
    print("=" * 80)
    print("COMPARACIÓN CON IMAGE-MAPPING.JSON")
    print("=" * 80)
    
    # Crear diccionario por nombre de archivo
    cloud_by_filename = {}
    for img in cloudinary_images:
        filename = img['public_id'].split('/')[-1]
        cloud_by_filename[filename.lower()] = img
    
    # Estadísticas
    stats = {
        'total_local': len(local_mapping),
        'total_cloud': len(cloudinary_images),
        'matched': 0,
        'missing': 0,
        'version_issues': 0,
    }
    
    print()
    print("📋 Análisis de coincidencias:")
    print("-" * 80)
    
    for item in local_mapping[:10]:  # Mostrar primeras 10
        local_path = item.get('local', '')
        local_url = item.get('cloudinary', '')
        
        # Extraer nombre de archivo
        filename = local_path.split('/')[-1] if local_path else ''
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Buscar en Cloudinary
        found = cloud_by_filename.get(name_without_ext.lower())
        
        if found:
            stats['matched'] += 1
            cloud_url = found['url']
            version = found['version']
            
            # Verificar si la URL local tiene versión
            has_version = '/v' in local_url and '/upload/v' in local_url
            
            if has_version:
                status = "✅"
            else:
                status = "⚠️  FALTA VERSIÓN"
                stats['version_issues'] += 1
            
            print(f"{status} {filename}")
            print(f"   Cloudinary: {cloud_url[:70]}...")
            print(f"   Versión: {version}")
            if local_url != cloud_url:
                print(f"   Local:      {local_url[:70]}...")
        else:
            stats['missing'] += 1
            print(f"❌ {filename} - No encontrada en Cloudinary")
    
    print()
    print("-" * 80)
    print(f"Estadísticas:")
    print(f"  - Locales: {stats['total_local']}")
    print(f"  - En Cloudinary: {stats['total_cloud']}")
    print(f"  - Coincidencias: {stats['matched']}")
    print(f"  - Faltan versión: {stats['version_issues']}")
    print(f"  - No encontradas: {stats['missing']}")
    
    return stats


def main():
    print("=" * 80)
    print("🔍 ANÁLISIS DE ESTRUCTURA CLOUDINARY")
    print("=" * 80)
    print()
    
    # Cargar mapeo local
    local_mapping = load_image_mapping()
    print(f"📂 image-mapping.json: {len(local_mapping)} entradas")
    print()
    
    # Analizar Cloudinary
    cloudinary_images = analyze_cloudinary_structure()
    
    if cloudinary_images:
        print(f"☁️  Cloudinary: {len(cloudinary_images)} imágenes")
        print()
        
        # Analizar carpetas
        folders = analyze_folders(cloudinary_images)
        print("📁 Estructura de carpetas:")
        for folder, images in sorted(folders.items()):
            print(f"   {folder}: {len(images)} imágenes")
        
        print()
        print("🔗 Ejemplos de URLs reales:")
        print("-" * 80)
        for img in cloudinary_images[:5]:
            print(f"Public ID: {img['public_id']}")
            print(f"URL:       {img['url']}")
            print(f"Versión:   {img['version']}")
            print()
        
        # Comparar con mapeo
        compare_with_mapping(cloudinary_images, local_mapping)
    else:
        print()
        print("💡 Para obtener datos de Cloudinary, configura:")
        print("   export CLOUDINARY_API_KEY=tu_api_key")
        print("   export CLOUDINARY_API_SECRET=tu_api_secret")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
