#!/usr/bin/env python3
"""
Script para sincronizar imágenes locales a Cloudinary
Uso: python sync_images_to_cloudinary.py
"""

import os
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    from app.services.cloudinary_service import upload_image, is_cloudinary_enabled
except ImportError:
    print("❌ Error: No se pudo importar cloudinary_service")
    sys.exit(1)

# Directorio base de imágenes
BASE_DIR = Path(__file__).parent.parent / "CDS_VUE3_ZERO" / "public" / "images"


def sync_images():
    if not is_cloudinary_enabled():
        print("❌ Cloudinary no está configurado")
        print("   Setea CLOUDINARY_URL en el .env")
        return
    
    print(f"📂 Buscando imágenes en: {BASE_DIR}")
    
    # Buscar todas las imágenes
    image_extensions = ['*.webp', '*.png', '*.jpg', '*.jpeg']
    images = []
    for ext in image_extensions:
        images.extend(BASE_DIR.rglob(ext))
    
    print(f"🖼️  Encontradas {len(images)} imágenes")
    print()
    
    # Subir cada imagen
    uploaded = 0
    failed = 0
    
    for img_path in images:
        # Calcular ruta relativa para la carpeta en Cloudinary
        rel_path = img_path.relative_to(BASE_DIR)
        destination = str(rel_path.parent).replace('\\', '/')
        
        print(f"⬆️  Subiendo: {rel_path} -> folder: {destination}")
        
        try:
            # TODO: Implementar upload real usando cloudinary.uploader
            # Por ahora solo mostramos qué se subiría
            print(f"   ✅ {rel_path} -> cirujano/{destination}/{rel_path.name}")
            uploaded += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    print()
    print(f"📊 Resumen: {uploaded} subidas, {failed} fallidas")
    print()
    print("⚠️  NOTA: Este es un preview. Para subir realmente:")
    print("   1. Instalar: pip install cloudinary")
    print("   2. Configurar CLOUDINARY_URL en backend/.env")
    print("   3. Ejecutar script con --upload")


if __name__ == "__main__":
    sync_images()
