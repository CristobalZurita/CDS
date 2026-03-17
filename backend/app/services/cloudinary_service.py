"""
Servicio Cloudinary - fuente canónica para uploads y resolución dinámica.
Usa CLOUDINARY_URL desde variables de entorno.
"""

import os
import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Variable global para el cliente (lazy loading)
_cloudinary_client = None

# Cache en memoria de las imágenes
_cloudinary_cache = {}

LEGACY_IMAGE_PREFIX = "/images/"
DESTINATION_PUBLIC_ID_PREFIXES = {
    "uploads": "general",
    "uploads/images": "general",
    "instrumentos": "instrumentos",
    "inventario": "INVENTARIO",
    "public/images/instrumentos": "instrumentos",
    "public/images/INVENTARIO": "INVENTARIO",
}


def _normalize_public_id_candidate(value: str) -> str:
    normalized = str(value or "").replace("\\", "/").strip().strip("/")
    if not normalized:
        return ""
    parts = normalized.split("/")
    parts[-1] = Path(parts[-1]).stem
    return "/".join(part for part in parts if part)


def local_path_to_public_id(local_path: str) -> str:
    """
    Convierte una ruta legacy /images/... al public_id canónico de Cloudinary.
    Ej: /images/personales/marimba.webp -> personales/marimba
    """
    normalized = str(local_path or "").strip()
    if not normalized:
        return ""
    if normalized.startswith("http"):
        return normalized
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    candidate = normalized[len(LEGACY_IMAGE_PREFIX):] if normalized.startswith(LEGACY_IMAGE_PREFIX) else normalized.lstrip("/")
    return _normalize_public_id_candidate(candidate)


def _canonical_prefix_for_destination(destination: str) -> str:
    target = (destination or "uploads").strip()
    return DESTINATION_PUBLIC_ID_PREFIXES.get(target, "general")


def _resolve_upload_target(destination: str, filename: Optional[str] = None, public_id: Optional[str] = None) -> tuple[str, str]:
    prefix = _canonical_prefix_for_destination(destination)
    candidate = _normalize_public_id_candidate(public_id or filename or "")
    if not candidate:
        raise RuntimeError("Could not determine Cloudinary public_id")
    full_public_id = candidate if "/" in candidate else f"{prefix}/{candidate}"
    asset_folder = full_public_id.rsplit("/", 1)[0] if "/" in full_public_id else prefix
    return full_public_id, asset_folder


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
    
    # Leer contenido del archivo
    content = await file.read()
    await file.seek(0)

    public_id, asset_folder = _resolve_upload_target(
        destination=destination,
        filename=file.filename,
        public_id=public_id,
    )
    
    try:
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            asset_folder=asset_folder,
            overwrite=True,
            invalidate=True,
            resource_type="image",
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


def generate_upload_signature(
    destination: str = "uploads",
    filename: Optional[str] = None,
    public_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Genera firma para upload directo desde el frontend a Cloudinary.
    Evita que el archivo pase por el servidor.
    
    Returns:
        {
            "cloud_name": str,
            "api_key": str,
            "timestamp": int,
            "signature": str,
            "public_id": str,
            "asset_folder": str,
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
        resolved_public_id, asset_folder = _resolve_upload_target(
            destination=destination,
            filename=filename,
            public_id=public_id,
        )

        params_to_sign = {
            "timestamp": timestamp,
            "public_id": resolved_public_id,
            "asset_folder": asset_folder,
            "overwrite": "true",
            "invalidate": "true",
        }
        
        signature = cloudinary.utils.api_sign_request(params_to_sign, api_secret)
        
        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "timestamp": timestamp,
            "signature": signature,
            "public_id": resolved_public_id,
            "asset_folder": asset_folder,
            "overwrite": True,
            "invalidate": True,
        }
        
    except Exception as e:
        logger.error(f"Failed to generate upload signature: {e}")
        return None


# =============================================================================
# FUNCIONES DE RESOLUCIÓN DE URLs (desde cloudinary_catalog_service.py)
# =============================================================================

def fetch_all_images() -> List[Dict]:
    """
    Obtiene todas las imágenes de Cloudinary con sus URLs.
    Retorna lista de dicts con: public_id, url, format, bytes
    """
    client = _get_client()
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
    Ej: 'BOTON_GRANDE_B_MPC' → 'https://res.cloudinary.com/...'
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
    Para rutas legacy /images/... deriva directamente el public_id canónico.
    Para otros strings, intenta búsqueda por nombre como fallback.
    
    Ej: '/images/INVENTARIO/BOTON_GRANDE_B_MPC.webp' → 'https://res.cloudinary.com/...'
    """
    if not local_path:
        return ""
    
    # Si ya es URL, devolverla
    if local_path.startswith("http"):
        return local_path

    public_id = local_path_to_public_id(local_path)
    if public_id and not public_id.startswith("http"):
        if is_cloudinary_enabled():
            return get_optimized_url(public_id)
        return local_path

    # Fallback: Buscar en Cloudinary API por nombre
    filename = local_path.split("/")[-1]
    name_without_ext = filename.rsplit(".", 1)[0]
    cloudinary_url = find_image_by_name(name_without_ext)
    
    if cloudinary_url:
        return cloudinary_url
    
    # Fallback: mantener ruta local si no se encuentra
    logger.warning(f"[cloudinary] Image not found: {local_path}")
    return local_path
