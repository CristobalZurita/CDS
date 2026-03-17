"""
Router para resolver imágenes desde Cloudinary.
ADITIVO: No modifica la BD, solo consulta Cloudinary API.
"""

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.services.cloudinary_service import (
    fetch_all_images,
    resolve_image_url,
    find_image_by_name,
)

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/catalog")
def get_image_catalog():
    """
    Obtiene catálogo completo de imágenes desde Cloudinary.
    Cacheado en memoria para performance.
    """
    images = fetch_all_images()
    return {
        "count": len(images),
        "images": images
    }


@router.get("/resolve")
def resolve_image(
    path: str = Query(..., description="Ruta local de la imagen, ej: /images/INVENTARIO/foto.webp")
):
    """
    Resuelve una ruta local a URL de Cloudinary.
    Ej: /images/INVENTARIO/BOTON_GRANDE_B_MPC.webp → https://res.cloudinary.com/...
    """
    url = resolve_image_url(path)
    return {
        "local_path": path,
        "cloudinary_url": url,
        "found": url != path and url != ""
    }


@router.post("/resolve-batch")
def resolve_images_batch(paths: List[str]):
    """
    Resuelve múltiples rutas locales a URLs de Cloudinary.
    Útil para cargar muchas imágenes a la vez usando la convención canónica
    /images/... -> public_id.
    """
    results = {}
    for path in paths:
        results[path] = resolve_image_url(path)
    
    return {
        "count": len(results),
        "mappings": results
    }


@router.get("/search")
def search_image(
    name: str = Query(..., description="Nombre base de la imagen sin extensión")
):
    """
    Busca una imagen por nombre (sin hash ni extensión).
    """
    url = find_image_by_name(name)
    return {
        "query": name,
        "found": url is not None,
        "url": url
    }
