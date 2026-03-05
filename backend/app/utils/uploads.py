import os
from fastapi import UploadFile, HTTPException, status
from PIL import Image, UnidentifiedImageError
from pathlib import Path
from io import BytesIO
from pathlib import Path

# Default max size 5MB
MAX_IMAGE_SIZE = int(os.getenv("IMAGE_MAX_SIZE", str(5 * 1024 * 1024)))
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def allowed_extension(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


def _matches_image_signature(filename: str, content: bytes) -> bool:
    sig = content[:12]
    lower_name = str(filename or "").lower()
    if lower_name.endswith(".png") and sig.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if lower_name.endswith((".jpg", ".jpeg")) and sig.startswith(b"\xff\xd8\xff"):
        return True
    if lower_name.endswith(".gif") and (sig.startswith(b"GIF87a") or sig.startswith(b"GIF89a")):
        return True
    if lower_name.endswith(".webp") and sig[0:4] == b"RIFF" and sig[8:12] == b"WEBP":
        return True
    return False


async def validate_image(file: UploadFile) -> None:
    # Check extension
    if not allowed_extension(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file extension")

    # Check size by streaming chunks
    size = 0
    content = await file.read()
    size = len(content)
    if size <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image file")
    if size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image too large")

    # Validate image content using Pillow
    try:
        img = Image.open(BytesIO(content))
        img.verify()
    except UnidentifiedImageError:
        # Pillow couldn't verify the image; fallback to signature validation.
        if _matches_image_signature(file.filename, content):
            await file.seek(0)
            return
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not a valid image")
    except Exception:
        # Some valid small/borderline files may trigger generic parser errors.
        if _matches_image_signature(file.filename, content):
            await file.seek(0)
            return
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file")

    # reset the file pointer for further processing
    await file.seek(0)


async def save_upload(file: UploadFile, dest_dir: str = "uploads/images") -> str:
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name
    dest = Path(dest_dir) / safe_name
    with open(dest, "wb") as f:
        while True:
            chunk = await file.read(1024 * 64)
            if not chunk:
                break
            f.write(chunk)
    return str(dest)


def resolve_upload_path(path_value: str, uploads_root: str = "uploads") -> Path:
    """Resolve and validate an uploads path to prevent path traversal."""
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = Path(uploads_root) / candidate
    resolved = candidate.resolve()
    root = Path(uploads_root).resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError("Invalid uploads path")
    return resolved
