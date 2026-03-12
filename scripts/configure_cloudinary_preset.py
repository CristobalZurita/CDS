#!/usr/bin/env python3
"""
Configura upload preset de Cloudinary para no añadir hash único
Uso: python configure_cloudinary_preset.py
"""

import os
import sys

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

try:
    import cloudinary
    import cloudinary.api
except ImportError:
    print("❌ Error: pip install cloudinary")
    sys.exit(1)

# Configurar con variables de entorno
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dgwwi77ic"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def configure_preset():
    preset_name = "cds_unsigned_upload"  # Nombre del preset
    
    try:
        # Crear o actualizar upload preset
        result = cloudinary.api.create_upload_preset(
            name=preset_name,
            unsigned=True,
            unique_filename=False,  # No añadir hash
            overwrite=True,         # Permitir sobrescribir
            folder="cirujano",
            resource_type="image",
        )
        print(f"✅ Upload preset '{preset_name}' configurado:")
        print(f"   - unique_filename: False")
        print(f"   - overwrite: True")
        print(f"   - folder: cirujano")
        print()
        print(f"Usa este preset en el frontend: {preset_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Configura manualmente en:")
        print("https://cloudinary.com/console/settings/upload")

if __name__ == "__main__":
    configure_preset()
