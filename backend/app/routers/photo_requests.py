from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import secrets

from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import require_permission
from app.models.photo_upload_request import PhotoUploadRequest
from app.models.repair import Repair
from app.models.repair_photo import RepairPhoto
from app.utils.uploads import validate_image, save_upload

router = APIRouter(prefix="/photo-requests", tags=["photo_requests"])


@router.post("/", status_code=201)
async def create_photo_request(
    repair_id: int,
    photo_type: str = "client",
    caption: str | None = None,
    expires_minutes: int = 30,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update")),
):
    repair = db.query(Repair).filter(Repair.id == repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    token = secrets.token_urlsafe(32)
    if expires_minutes < 1:
        expires_minutes = 1
    if expires_minutes > 10:
        expires_minutes = 10
    req = PhotoUploadRequest(
        repair_id=repair_id,
        token=token,
        status="pending",
        photo_type=photo_type,
        caption=caption,
        expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"id": req.id, "token": req.token, "status": req.status, "expires_at": req.expires_at}


@router.get("/token/{token}")
@limiter.limit("30/minute")
def get_photo_request(token: str, request: Request, response: Response, db: Session = Depends(get_db)):
    req = db.query(PhotoUploadRequest).filter(PhotoUploadRequest.token == token).first()
    if not req:
        raise HTTPException(status_code=404, detail="Token inválido")
    if req.expires_at and req.expires_at < datetime.utcnow():
        req.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Token expirado")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Solicitud no válida")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return {"id": req.id, "repair_id": req.repair_id, "status": req.status, "photo_type": req.photo_type}


@router.post("/submit")
@limiter.limit("10/minute")
async def submit_photo(
    request: Request,
    token: str = Form(...),
    file: UploadFile = File(...),
    caption: str | None = Form(None),
    db: Session = Depends(get_db),
):
    req = db.query(PhotoUploadRequest).filter(PhotoUploadRequest.token == token).first()
    if not req:
        raise HTTPException(status_code=404, detail="Token inválido")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Solicitud no válida")
    if req.expires_at and req.expires_at < datetime.utcnow():
        req.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="Token expirado")

    await validate_image(file)
    dest_dir = os.path.join("uploads", "repairs", f"repair-{req.repair_id}")
    file.filename = f"client-{int(datetime.utcnow().timestamp())}-{file.filename}"
    saved_path = await save_upload(file, dest_dir=dest_dir)
    photo = RepairPhoto(
        repair_id=req.repair_id,
        photo_url=saved_path,
        photo_type=req.photo_type or "client",
        caption=caption or req.caption,
        visible_to_client=1,
    )
    db.add(photo)
    req.status = "uploaded"
    # Rotate token after use to prevent replay
    req.token = secrets.token_urlsafe(32)
    db.commit()
    return {"ok": True, "photo_id": photo.id}
