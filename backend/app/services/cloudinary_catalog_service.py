from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.services.cloudinary_support import (
    get_cached_images,
    get_cloudinary_client,
    is_cloudinary_enabled,
    local_path_to_public_id,
    replace_cached_images,
)
from app.services.cloudinary_upload_service import get_optimized_url

logger = logging.getLogger(__name__)


def fetch_all_images() -> List[Dict]:
    client = get_cloudinary_client()
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
                next_cursor=next_cursor,
            )

            for resource in result.get("resources", []):
                images.append(
                    {
                        "public_id": resource.get("public_id"),
                        "url": resource.get("secure_url"),
                        "format": resource.get("format"),
                        "bytes": resource.get("bytes"),
                        "width": resource.get("width"),
                        "height": resource.get("height"),
                    }
                )

            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break

        replace_cached_images(images)
        return images
    except Exception as exc:
        logger.error(f"Error fetching Cloudinary resources: {exc}")
        return []


def find_image_by_name(local_name: str) -> Optional[str]:
    cache = get_cached_images()
    if not cache:
        fetch_all_images()
        cache = get_cached_images()

    local_base = local_name.split(".")[0].lower()
    for public_id, image_data in cache.items():
        cloudinary_base = public_id.split("_")[:-1] if "_" in public_id else [public_id]
        cloudinary_name = "_".join(cloudinary_base).lower()
        if local_base == cloudinary_name:
            return image_data["url"]
    return None


def resolve_image_url(local_path: str) -> str:
    if not local_path:
        return ""
    if local_path.startswith("http"):
        return local_path

    public_id = local_path_to_public_id(local_path)
    if public_id and not public_id.startswith("http"):
        if is_cloudinary_enabled():
            return get_optimized_url(public_id)
        return local_path

    filename = local_path.split("/")[-1]
    name_without_ext = filename.rsplit(".", 1)[0]
    cloudinary_url = find_image_by_name(name_without_ext)
    if cloudinary_url:
        return cloudinary_url

    logger.warning(f"[cloudinary] Image not found: {local_path}")
    return local_path
