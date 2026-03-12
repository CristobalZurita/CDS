"""
Servicio Cloudinary para almacenamiento de imágenes.
ADITIVO: No modifica el comportamiento local existente.
Usa CLOUDINARY_URL desde variables de entorno.
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Variable global para el cliente (lazy loading)
_cloudinary_client = None


def _get_client():
    """Obtiene o inicializa el cliente de Cloudinary."""
    global _cloudinary_client
    
    if _cloudinary_client is not None:
        return _cloudinary_client
    
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    if not cloudinary_url:
        return None
    
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        # cloudinary.config() automáticamente lee CLOUDINARY_URL del env
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        )
        
        _cloudinary_client = cloudinary
        logger.info("Cloudinary client initialized")
        return _cloudinary_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Cloudinary: {e}")
        return None


def is_cloudinary_enabled() -> bool:
    """Verifica si Cloudinary está disponible y configurado."""
    return os.getenv("CLOUDINARY_URL") is not None and _get_client() is not None


def _get_folder_for_destination(destination: str) -> str:
    """Mapea destinos locales a carpetas en Cloudinary."""
    folder_base = os.getenv("CLOUDINARY_FOLDER_BASE", "cirujano")
    
    mapping = {
        "uploads": f"{folder_base}/general",
        "uploads/images": f"{folder_base}/general",
        "instrumentos": f"{folder_base}/instrumentos",
        "inventario": f"{folder_base}/inventario",
        "public/images/instrumentos": f"{folder_base}/instrumentos",
        "public/images/INVENTARIO": f"{folder_base}/inventario",
    }
    
    return mapping.get(destination, f"{folder_base}/general")


async def upload_image(
    file: UploadFile,
    destination: str = "uploads",
    public_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Sube una imagen a Cloudinary.
    
    Returns:
        {
            "path": str,           # URL completa de Cloudinary
            "public_path": str,    # URL pública para mostrar
            "filename": str,       # Nombre original
            "cloudinary_public_id": str,  # ID en Cloudinary
        }
    """
    client = _get_client()
    if not client:
        raise RuntimeError("Cloudinary not configured")
    
    import cloudinary.uploader
    
    folder = _get_folder_for_destination(destination)
    
    # Leer contenido del archivo
    content = await file.read()
    await file.seek(0)
    
    # Generar public_id si no se proporciona
    if not public_id and file.filename:
        # Limpiar nombre para usarlo como public_id
        base_name = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
        public_id = f"{folder}/{base_name}"
    else:
        public_id = f"{folder}/{public_id}"
    
    try:
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
            folder="",  # public_id ya incluye la carpeta
        )
        
        return {
            "path": result["secure_url"],
            "public_path": result["secure_url"],
            "filename": file.filename,
            "cloudinary_public_id": result["public_id"],
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "bytes": result.get("bytes"),
        }
        
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise


def get_optimized_url(public_id: str, width: Optional[int] = None, quality: str = "auto") -> str:
    """
    Genera URL optimizada con transformaciones de Cloudinary.
    
    Ejemplos:
        - get_optimized_url("cirujano/inventario/foto", width=800)
        - get_optimized_url("cirujano/inventario/foto", width=200, quality="low")
    """
    client = _get_client()
    if not client:
        return public_id  # Fallback
    
    from cloudinary.utils import cloudinary_url
    
    transformations = {
        "quality": quality,
        "fetch_format": "auto",  # WebP para Chrome, JPEG para Safari, etc.
    }
    
    if width:
        transformations["width"] = width
        transformations["crop"] = "limit"  # No escalar más grande que original
    
    url, options = cloudinary_url(
        public_id,
        **transformations
    )
    
    return url


def delete_image(public_id: str) -> bool:
    """Elimina una imagen de Cloudinary por su public_id."""
    client = _get_client()
    if not client:
        return False
    
    import cloudinary.api
    
    try:
        result = cloudinary.api.delete_resources([public_id])
        return result.get("deleted", {}).get(public_id) == "deleted"
    except Exception as e:
        logger.error(f"Failed to delete image {public_id}: {e}")
        return False


def generate_upload_signature(destination: str = "uploads") -> Optional[Dict[str, Any]]:
    """
    Genera firma para upload directo desde el frontend a Cloudinary.
    Evita que el archivo pase por el servidor.
    
    Returns:
        {
            "cloud_name": str,
            "api_key": str,
            "timestamp": int,
            "signature": str,
            "folder": str,
        }
    """
    client = _get_client()
    if not client:
        return None
    
    try:
        import cloudinary.utils
        
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        
        if not all([cloud_name, api_key, api_secret]):
            return None
        
        timestamp = int(time.time())
        folder = _get_folder_for_destination(destination)
        
        # Generar firma para upload con folder específico
        params_to_sign = {
            "timestamp": timestamp,
            "folder": folder,
        }
        
        signature = cloudinary.utils.api_sign_request(params_to_sign, api_secret)
        
        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "timestamp": timestamp,
            "signature": signature,
            "folder": folder,
        }
        
    except Exception as e:
        logger.error(f"Failed to generate upload signature: {e}")
        return None
