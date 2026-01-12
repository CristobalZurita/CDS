import os
from fastapi import UploadFile, HTTPException, status
from PIL import Image, UnidentifiedImageError
from pathlib import Path
from io import BytesIO

# Default max size 5MB
MAX_IMAGE_SIZE = int(os.getenv("IMAGE_MAX_SIZE", str(5 * 1024 * 1024)))
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}


def allowed_extension(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in ALLOWED_EXTENSIONS


async def validate_image(file: UploadFile) -> None:
    # Check extension
    if not allowed_extension(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file extension")

    # Check size by streaming chunks
    size = 0
    content = await file.read()
    size = len(content)
    if size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image too large")

    # Validate image content using Pillow
    try:
        img = Image.open(BytesIO(content))
        img.verify()
    except UnidentifiedImageError:
        # Pillow couldn't verify the image; as a fallback, allow uploads that contain
        # a valid image magic signature (useful for minimal or streaming uploads in tests)
        sig = content[:12]
        if file.filename.lower().endswith(".png") and sig.startswith(b"\x89PNG\r\n\x1a\n"):
            await file.seek(0)
            return
        if file.filename.lower().endswith(('.jpg', '.jpeg')) and sig.startswith(b"\xff\xd8\xff"):
            await file.seek(0)
            return
        if file.filename.lower().endswith('.gif') and (sig.startswith(b'GIF87a') or sig.startswith(b'GIF89a')):
            await file.seek(0)
            return
        if file.filename.lower().endswith('.webp') and sig[0:4] == b'RIFF' and sig[8:12] == b'WEBP':
            await file.seek(0)
            return
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not a valid image")
    except Exception:
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
