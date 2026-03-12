#!/usr/bin/env python3
"""
Script para subir TODAS las fotos locales a Cloudinary
Mantiene la estructura de carpetas exacta
"""

import os
import sys
from pathlib import Path

# Configuración
CLOUD_NAME = 'dgwwi77ic'
API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')
UPLOAD_PRESET = 'cds_unsigned'  # Debe estar configurado sin sufijo único

BASE_DIR = Path(__file__).parent.parent / "CDS_VUE3_ZERO" / "public" / "images"

def upload_all():
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=CLOUD_NAME,
            api_key=API_KEY,
            api_secret=API_SECRET
        )
        
        print(f"📂 Buscando imágenes en: {BASE_DIR}")
        
        # Encontrar todas las imágenes
        images = list(BASE_DIR.rglob("*.webp")) + list(BASE_DIR.rglob("*.png")) + list(BASE_DIR.rglob("*.jpg"))
        print(f"🖼️  Encontradas {len(images)} imágenes")
        print()
        
        uploaded = 0
        failed = 0
        
        for img_path in sorted(images):
            # Calcular ruta relativa para la carpeta en Cloudinary
            rel_path = img_path.relative_to(BASE_DIR.parent)
            folder = str(rel_path.parent).replace('\\', '/')
            public_id = img_path.stem  # Nombre sin extensión
            
            print(f"⬆️  Subiendo: {rel_path}")
            print(f"   → Folder: {folder}")
            print(f"   → Public ID: {public_id}")
            
            try:
                result = cloudinary.uploader.upload(
                    str(img_path),
                    folder=folder,
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image",
                    use_filename=True,  # Usar nombre original
                    unique_filename=False,  # No añadir hash
                )
                print(f"   ✅ URL: {result['secure_url']}")
                uploaded += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
            
            print()
        
        print(f"📊 Resumen: {uploaded} subidas, {failed} fallidas")
        
    except ImportError:
        print("❌ Error: pip install cloudinary")
        sys.exit(1)

if __name__ == "__main__":
    if not API_KEY or not API_SECRET:
        print("❌ Configura CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET")
        print("   export CLOUDINARY_API_KEY='tu_key'")
        print("   export CLOUDINARY_API_SECRET='tu_secret'")
        sys.exit(1)
    
    upload_all()
