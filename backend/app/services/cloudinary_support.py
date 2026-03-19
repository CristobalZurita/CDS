from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse

logger = logging.getLogger(__name__)

LEGACY_IMAGE_PREFIX = "/images/"
DESTINATION_PUBLIC_ID_PREFIXES = {
    "uploads": "general",
    "uploads/images": "general",
    "instrumentos": "instrumentos",
    "inventario": "INVENTARIO",
    "public/images/instrumentos": "instrumentos",
    "public/images/INVENTARIO": "INVENTARIO",
}

_cloudinary_client = None
_cloudinary_cache: dict[str, dict[str, Any]] = {}


def _normalize_public_id_candidate(value: str) -> str:
    normalized = str(value or "").replace("\\", "/").strip().strip("/")
    if not normalized:
        return ""
    parts = normalized.split("/")
    parts[-1] = Path(parts[-1]).stem
    return "/".join(part for part in parts if part)


def local_path_to_public_id(local_path: str) -> str:
    normalized = str(local_path or "").strip()
    if not normalized:
        return ""
    if normalized.startswith("http"):
        return normalized
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    candidate = (
        normalized[len(LEGACY_IMAGE_PREFIX) :]
        if normalized.startswith(LEGACY_IMAGE_PREFIX)
        else normalized.lstrip("/")
    )
    return _normalize_public_id_candidate(candidate)


def build_legacy_local_path(relative_path: str) -> str:
    normalized = str(relative_path or "").replace("\\", "/").strip().strip("/")
    if not normalized:
        return LEGACY_IMAGE_PREFIX.rstrip("/")
    return f"{LEGACY_IMAGE_PREFIX}{normalized}"


def extract_filename_from_local_path(
    local_path: str,
    expected_relative_prefix: Optional[str] = None,
) -> str:
    value = str(local_path or "").strip()
    if not value:
        return ""

    if expected_relative_prefix:
        prefix = build_legacy_local_path(expected_relative_prefix).rstrip("/") + "/"
        if value.startswith(prefix):
            return value.split(prefix, 1)[1].strip()

    return Path(value).name.strip()


def _canonical_prefix_for_destination(destination: str) -> str:
    target = (destination or "uploads").strip()
    return DESTINATION_PUBLIC_ID_PREFIXES.get(target, "general")


def resolve_upload_target(
    destination: str,
    filename: Optional[str] = None,
    public_id: Optional[str] = None,
) -> tuple[str, str]:
    prefix = _canonical_prefix_for_destination(destination)
    candidate = _normalize_public_id_candidate(public_id or filename or "")
    if not candidate:
        raise RuntimeError("Could not determine Cloudinary public_id")
    full_public_id = candidate if "/" in candidate else f"{prefix}/{candidate}"
    asset_folder = full_public_id.rsplit("/", 1)[0] if "/" in full_public_id else prefix
    return full_public_id, asset_folder


def resolve_cloudinary_config() -> Optional[Dict[str, str]]:
    cloud_name = str(os.getenv("CLOUDINARY_CLOUD_NAME") or "").strip()
    api_key = str(os.getenv("CLOUDINARY_API_KEY") or "").strip()
    api_secret = str(os.getenv("CLOUDINARY_API_SECRET") or "").strip()

    if cloud_name and api_key and api_secret:
        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
        }

    cloudinary_url = str(os.getenv("CLOUDINARY_URL") or "").strip()
    if not cloudinary_url:
        return None

    parsed = urlparse(cloudinary_url)
    if parsed.scheme != "cloudinary":
        return None

    parsed_api_key = unquote(parsed.username or "").strip()
    parsed_api_secret = unquote(parsed.password or "").strip()
    parsed_cloud_name = unquote(parsed.hostname or "").strip()

    if not parsed_cloud_name or not parsed_api_key or not parsed_api_secret:
        return None

    return {
        "cloud_name": cloud_name or parsed_cloud_name,
        "api_key": api_key or parsed_api_key,
        "api_secret": api_secret or parsed_api_secret,
    }


def get_cloudinary_client():
    global _cloudinary_client
    if _cloudinary_client is not None:
        return _cloudinary_client

    config = resolve_cloudinary_config()
    if not config:
        return None

    try:
        import cloudinary
        import cloudinary.api  # noqa: F401
        import cloudinary.uploader  # noqa: F401

        cloudinary.config(
            cloud_name=config["cloud_name"],
            api_key=config["api_key"],
            api_secret=config["api_secret"],
        )
        _cloudinary_client = cloudinary
        logger.info("Cloudinary client initialized")
        return _cloudinary_client
    except Exception as exc:
        logger.error(f"Failed to initialize Cloudinary: {exc}")
        return None


def is_cloudinary_enabled() -> bool:
    return resolve_cloudinary_config() is not None and get_cloudinary_client() is not None


def get_cached_images() -> dict[str, dict[str, Any]]:
    return _cloudinary_cache


def replace_cached_images(images: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    global _cloudinary_cache
    _cloudinary_cache = {img["public_id"]: img for img in images}
    return _cloudinary_cache
