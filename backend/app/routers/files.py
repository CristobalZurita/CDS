from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.config import settings
from app.models.repair_photo import RepairPhoto
from app.utils.uploads import resolve_upload_path

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/repair-photos/{photo_id}")
def get_repair_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    photo = db.query(RepairPhoto).filter(RepairPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if not photo.photo_url:
        raise HTTPException(status_code=404, detail="Photo missing")

    if settings.enable_public_uploads:
        # Public uploads are enabled; allow direct access by URL instead.
        raise HTTPException(status_code=400, detail="Public uploads enabled; use photo_url")

    try:
        path = resolve_upload_path(photo.photo_url)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid photo path")

    if not path.exists():
        raise HTTPException(status_code=404, detail="Photo not found")

    return FileResponse(path)
