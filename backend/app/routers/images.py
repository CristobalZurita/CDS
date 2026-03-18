"""
Router legacy de compatibilidad para resolución de imágenes.

No es fuente de verdad de runtime:
- ZERO resuelve imágenes desde cloudinary.js/cloudinaryContract.js
- el dashboard gestiona assets/bindings desde /media

Este router se mantiene deprecated sólo para compatibilidad y diagnóstico.
"""

from fastapi import APIRouter, Query
from typing import List
from app.services.cloudinary_service import (
    fetch_all_images,
    resolve_image_url,
    find_image_by_name,
)

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/catalog", deprecated=True)
def get_image_catalog():
    """
    Endpoint legacy de diagnóstico.
    No debe usarse como catálogo principal de runtime.
    """
    images = fetch_all_images()
    return {
        "count": len(images),
        "images": images
    }


@router.get("/resolve", deprecated=True)
def resolve_image(
    path: str = Query(..., description="Ruta local de la imagen, ej: /images/INVENTARIO/foto.webp")
):
    """
    Wrapper deprecated de resolve_image_url().
    Se mantiene por compatibilidad externa; el front actual no depende de esta ruta.
    """
    url = resolve_image_url(path)
    return {
        "local_path": path,
        "cloudinary_url": url,
        "found": url != path and url != ""
    }


@router.post("/resolve-batch", deprecated=True)
def resolve_images_batch(paths: List[str]):
    """
    Wrapper deprecated por lotes.
    La resolución activa del front deriva el public_id localmente sin pasar por aquí.
    """
    results = {}
    for path in paths:
        results[path] = resolve_image_url(path)
    
    return {
        "count": len(results),
        "mappings": results
    }


@router.get("/search", deprecated=True)
def search_image(
    name: str = Query(..., description="Nombre base de la imagen sin extensión")
):
    """
    Búsqueda legacy por nombre.
    Útil sólo para diagnóstico o compatibilidad antigua.
    """
    url = find_image_by_name(name)
    return {
        "query": name,
        "found": url is not None,
        "url": url
    }
