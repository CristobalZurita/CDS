"""
Servicio para obtener catálogo de imágenes desde Cloudinary.
ADITIVO: Usa la API de Cloudinary para mapear nombres a URLs.
"""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Cache en memoria de las imágenes
_cloudinary_cache = {}


def _get_cloudinary_client():
    """Obtiene cliente Cloudinary configurado."""
    try:
        import cloudinary
        import cloudinary.api
        
        # Intentar usar CLOUDINARY_URL primero
        cloudinary_url = os.getenv("CLOUDINARY_URL")
        if cloudinary_url:
            # cloudinary.config() automáticamente detecta CLOUDINARY_URL
            os.environ.setdefault("CLOUDINARY_URL", cloudinary_url)
        else:
            # Fallback a variables separadas
            cloudinary.config(
                cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dgwwi77ic"),
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            )
        return cloudinary
    except Exception as e:
        logger.error(f"Error configurando Cloudinary: {e}")
        return None


def fetch_all_images() -> List[Dict]:
    """
    Obtiene todas las imágenes de Cloudinary con sus URLs.
    Retorna lista de dicts con: public_id, url, format, bytes
    """
    client = _get_cloudinary_client()
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
                    "bytes": resource.get("bytes"),
                    "width": resource.get("width"),
                    "height": resource.get("height"),
                })
            
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break
                
        # Guardar en cache
        global _cloudinary_cache
        _cloudinary_cache = {img["public_id"]: img for img in images}
        
        return images
        
    except Exception as e:
        logger.error(f"Error fetching Cloudinary resources: {e}")
        return []


def find_image_by_name(local_name: str) -> Optional[str]:
    """
    Busca una imagen en Cloudinary por nombre local.
    Ej: 'BOTON_GRANDE_B_MPC' → 'https://res.cloudinary.com/.../BOTON_GRANDE_B_MPC_os4tnj.webp'
    """
    global _cloudinary_cache
    
    # Si no hay cache, cargar
    if not _cloudinary_cache:
        fetch_all_images()
    
    # Buscar coincidencia parcial (ignorar hash y extensión)
    local_base = local_name.split(".")[0].lower()
    
    for public_id, img_data in _cloudinary_cache.items():
        # Quitar hash del final (ej: BOTON_GRANDE_B_MPC_os4tnj → BOTON_GRANDE_B_MPC)
        cloudinary_base = public_id.split("_")[:-1] if "_" in public_id else [public_id]
        cloudinary_name = "_".join(cloudinary_base).lower()
        
        if local_base == cloudinary_name:
            return img_data["url"]
    
    return None


def resolve_image_url(local_path: str) -> str:
    """
    Resuelve una ruta local a URL de Cloudinary.
    Ej: '/images/INVENTARIO/BOTON_GRANDE_B_MPC.webp' → 'https://res.cloudinary.com/...'
    """
    if not local_path:
        return ""
    
    # Si ya es URL, devolverla
    if local_path.startswith("http"):
        return local_path
    
    # Extraer nombre del archivo de la ruta local
    filename = local_path.split("/")[-1]
    name_without_ext = filename.rsplit(".", 1)[0]
    
    # Buscar en Cloudinary
    cloudinary_url = find_image_by_name(name_without_ext)
    
    if cloudinary_url:
        return cloudinary_url
    
    # Fallback: mantener ruta local si no se encuentra
    logger.warning(f"Image not found in Cloudinary: {local_path}")
    return local_path
