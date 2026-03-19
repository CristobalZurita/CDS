from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from fastapi import UploadFile

from app.services.cloudinary_support import (
    get_cloudinary_client,
    resolve_cloudinary_config,
    resolve_upload_target,
)

logger = logging.getLogger(__name__)


async def upload_image(
    file: UploadFile,
    destination: str = "uploads",
    public_id: Optional[str] = None,
) -> Dict[str, Any]:
    client = get_cloudinary_client()
    if not client:
        raise RuntimeError("Cloudinary not configured")

    import cloudinary.uploader

    content = await file.read()
    await file.seek(0)

    resolved_public_id, asset_folder = resolve_upload_target(
        destination=destination,
        filename=file.filename,
        public_id=public_id,
    )

    try:
        result = cloudinary.uploader.upload(
            content,
            public_id=resolved_public_id,
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
    except Exception as exc:
        logger.error(f"Cloudinary upload failed: {exc}")
        raise


def get_optimized_url(public_id: str, width: Optional[int] = None, quality: str = "auto") -> str:
    client = get_cloudinary_client()
    if not client:
        return public_id

    from cloudinary.utils import cloudinary_url

    transformations = {
        "quality": quality,
        "fetch_format": "auto",
    }
    if width:
        transformations["width"] = width
        transformations["crop"] = "limit"

    url, _ = cloudinary_url(public_id, **transformations)
    return url


def delete_image(public_id: str) -> bool:
    client = get_cloudinary_client()
    if not client:
        return False

    import cloudinary.api

    try:
        result = cloudinary.api.delete_resources([public_id])
        return result.get("deleted", {}).get(public_id) == "deleted"
    except Exception as exc:
        logger.error(f"Failed to delete image {public_id}: {exc}")
        return False


def generate_upload_signature(
    destination: str = "uploads",
    filename: Optional[str] = None,
    public_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    client = get_cloudinary_client()
    if not client:
        return None

    try:
        import cloudinary.utils

        config = resolve_cloudinary_config()
        if not config:
            return None

        timestamp = int(time.time())
        resolved_public_id, asset_folder = resolve_upload_target(
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
        signature = cloudinary.utils.api_sign_request(params_to_sign, config["api_secret"])

        return {
            "cloud_name": config["cloud_name"],
            "api_key": config["api_key"],
            "timestamp": timestamp,
            "signature": signature,
            "public_id": resolved_public_id,
            "asset_folder": asset_folder,
            "overwrite": True,
            "invalidate": True,
        }
    except Exception as exc:
        logger.error(f"Failed to generate upload signature: {exc}")
        return None
