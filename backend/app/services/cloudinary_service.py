"""
Fachada estable de Cloudinary.
Mantiene el contrato existente y delega por subdominio interno.
"""

from __future__ import annotations

from app.services.cloudinary_catalog_service import (
    fetch_all_images,
    find_image_by_name,
    resolve_image_url,
)
from app.services.cloudinary_support import (
    build_legacy_local_path,
    extract_filename_from_local_path,
    is_cloudinary_enabled,
    local_path_to_public_id,
    resolve_cloudinary_config,
)
from app.services.cloudinary_upload_service import (
    delete_image,
    generate_upload_signature,
    get_optimized_url,
    rename_image,
    upload_image,
)

__all__ = [
    "build_legacy_local_path",
    "delete_image",
    "extract_filename_from_local_path",
    "fetch_all_images",
    "find_image_by_name",
    "generate_upload_signature",
    "get_optimized_url",
    "is_cloudinary_enabled",
    "local_path_to_public_id",
    "rename_image",
    "resolve_cloudinary_config",
    "resolve_image_url",
    "upload_image",
]
