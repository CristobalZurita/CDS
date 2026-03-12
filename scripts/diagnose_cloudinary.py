#!/usr/bin/env python3
"""
Script de diagnóstico para Cloudinary
Escanea las imágenes en Cloudinary y compara con el mapeo local
"""

import os
import sys
import json
from pathlib import Path

# Configuración
CLOUD_NAME = 'dgwwi77ic'
IMAGE_MAPPING_PATH = Path(__file__).parent.parent / "image-mapping.json"


def get_cloudinary_client():
    """Obtiene cliente Cloudinary configurado."""
    try:
        import cloudinary
        import cloudinary.api
        
        # Intentar usar variables de entorno
        cloudinary.config(
            cloud_name=CLOUD_NAME,
            api_key=os.getenv('CLOUDINARY_API_KEY', ''),
            api_secret=os.getenv('CLOUDINARY_API_SECRET', '')
        )
        return cloudinary
    except ImportError:
        print("❌ Error: pip install cloudinary")
        return None


def fetch_all_cloudinary_images():
    """Obtiene todas las imágenes de Cloudinary."""
    client = get_cloudinary_client()
    if not client:
        return []
    
    import cloudinary.api
    
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
                images.append({
                    "public_id": resource.get("public_id"),
                    "url": resource.get("secure_url"),
                    "format": resource.get("format"),
                })
            
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break
                
        return images
    except Exception as e:
        print(f"❌ Error al obtener imágenes de Cloudinary: {e}")
        return []


def load_image_mapping():
    """Carga el mapeo local de imágenes."""
    try:
        with open(IMAGE_MAPPING_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar image-mapping.json: {e}")
        return []


def analyze_urls(cloudinary_images, local_mapping):
    """Analiza y compara las URLs."""
    print("=" * 80)
    print("ANÁLISIS DE URLs DE CLOUDINARY")
    print("=" * 80)
    print()
    
    # Crear diccionario de imágenes de Cloudinary por public_id
    cloudinary_by_id = {img['public_id']: img for img in cloudinary_images}
    
    # Estadísticas
    stats = {
        'total_local': len(local_mapping),
        'total_cloudinary': len(cloudinary_images),
        'urls_correctas': 0,
        'urls_incorrectas': 0,
        'no_encontradas': 0,
    }
    
    # Analizar cada imagen local
    print("📋 COMPARACIÓN DE URLs:")
    print("-" * 80)
    
    for item in local_mapping[:20]:  # Mostrar primeras 20
        local_path = item.get('local', '')
        local_url = item.get('cloudinary', '')
        
        # Extraer nombre de archivo
        filename = local_path.split('/')[-1] if local_path else ''
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Buscar en Cloudinary
        found = None
        for pub_id, img_data in cloudinary_by_id.items():
            if name_without_ext.lower() in pub_id.lower():
                found = img_data
                break
        
        if found:
            url_real = found['url']
            if local_url == url_real:
                stats['urls_correctas'] += 1
                status = "✅ OK"
            else:
                stats['urls_incorrectas'] += 1
                status = "❌ DIFERENTE"
                print(f"\n{status} {filename}")
                print(f"   Local:    {local_url[:70]}...")
                print(f"   Cloud:    {url_real[:70]}...")
        else:
            stats['no_encontradas'] += 1
            status = "⚠️  NO ENCONTRADA"
            print(f"\n{status} {filename}")
    
    print()
    print("=" * 80)
    print("ESTADÍSTICAS:")
    print(f"  - Total imágenes locales: {stats['total_local']}")
    print(f"  - Total imágenes en Cloudinary: {stats['total_cloudinary']}")
    print(f"  - URLs correctas: {stats['urls_correctas']}")
    print(f"  - URLs incorrectas: {stats['urls_incorrectas']}")
    print(f"  - No encontradas: {stats['no_encontradas']}")
    print("=" * 80)
    
    return stats


def show_url_format_examples(cloudinary_images):
    """Muestra ejemplos de formato de URLs."""
    print()
    print("=" * 80)
    print("EJEMPLOS DE URLs REALES EN CLOUDINARY:")
    print("=" * 80)
    
    for img in cloudinary_images[:10]:
        print(f"  Public ID: {img['public_id']}")
        print(f"  URL:       {img['url']}")
        print()


def main():
    print("🔍 DIAGNÓSTICO DE CLOUDINARY")
    print()
    
    # Verificar credenciales
    api_key = os.getenv('CLOUDINARY_API_KEY', '')
    api_secret = os.getenv('CLOUDINARY_API_SECRET', '')
    
    if not api_key or not api_secret:
        print("⚠️  ADVERTENCIA: No se encontraron credenciales de Cloudinary")
        print("   Define CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET")
        print()
        print("   Puedes obtenerlas desde:")
        print("   https://cloudinary.com/console")
        print()
    
    # Cargar datos
    print("📂 Cargando image-mapping.json...")
    local_mapping = load_image_mapping()
    print(f"   Encontradas {len(local_mapping)} entradas locales")
    print()
    
    if api_key and api_secret:
        print("☁️  Conectando a Cloudinary...")
        cloudinary_images = fetch_all_cloudinary_images()
        print(f"   Encontradas {len(cloudinary_images)} imágenes en Cloudinary")
        print()
        
        if cloudinary_images:
            show_url_format_examples(cloudinary_images)
            analyze_urls(cloudinary_images, local_mapping)
    else:
        print("💡 Para escanear Cloudinary, configura las credenciales:")
        print("   export CLOUDINARY_API_KEY=tu_api_key")
        print("   export CLOUDINARY_API_SECRET=tu_api_secret")
        print()
        print("   O revisa las URLs manualmente en:")
        print("   https://cloudinary.com/console/media_library")


if __name__ == "__main__":
    main()
