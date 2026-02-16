"""
Script para actualizar y limpiar rutas de imágenes en el inventario.
Ejecutar después de la migración 007_add_image_url_to_products.

Establece image_url a NULL para todos los productos existentes.
Esto previene que el frontend intente mostrar fotos rotas.
"""

from sqlalchemy import text
from app.core.database import SessionLocal

def reset_product_images():
    """Establecer image_url a NULL para todos los productos"""
    db = SessionLocal()
    try:
        result = db.execute(text("UPDATE products SET image_url = NULL"))
        db.commit()
        print(f"✅ {result.rowcount} productos actualizados (image_url = NULL)")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_product_images()
