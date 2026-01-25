from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse
from datetime import datetime, timedelta
import asyncio
import base64
import os
import secrets

from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import require_permission
from app.models.signature_request import SignatureRequest
from app.models.repair import Repair
from app.schemas.signature import SignatureRequestCreate, SignatureSubmit, SignatureRequestOut

router = APIRouter(prefix="/signatures", tags=["signatures"])

# In-memory SSE channels (token -> list of queues)
_channels = {}


def _broadcast(token: str, payload: str) -> None:
    queues = _channels.get(token, [])
    for q in queues:
        try:
            q.put_nowait(payload)
        except Exception:
            pass


def _save_signature_png(base64_str: str, dest_dir: str, filename: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    data = base64.b64decode(base64_str)
    path = os.path.join(dest_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path


@router.post("/requests", response_model=SignatureRequestOut)
def create_signature_request(
    payload: SignatureRequestCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("signatures", "create")),
):
    repair = db.query(Repair).filter(Repair.id == payload.repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    token = secrets.token_urlsafe(32)
    expires_minutes = payload.expires_minutes or 15
    if expires_minutes < 1:
        expires_minutes = 1
    if expires_minutes > 5:
        expires_minutes = 5
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
    sig = SignatureRequest(
        repair_id=payload.repair_id,
        request_type=payload.request_type,
        token=token,
        status="pending",
        expires_at=expires_at,
    )
    db.add(sig)
    db.commit()
    db.refresh(sig)

    return sig


@router.get("/requests/{request_id}", response_model=SignatureRequestOut)
def get_signature_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("signatures", "read")),
):
    sig = db.query(SignatureRequest).filter(SignatureRequest.id == request_id).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signature request not found")
    return sig


@router.get("/requests/token/{token}", response_model=SignatureRequestOut)
@limiter.limit("30/minute")
def get_signature_request_by_token(
    token: str,
    response: Response,
    db: Session = Depends(get_db),
):
    sig = db.query(SignatureRequest).filter(SignatureRequest.token == token).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signature request not found")
    if sig.expires_at and sig.expires_at < datetime.utcnow():
        sig.status = "expired"
        db.commit()
        raise HTTPException(status_code=410, detail="Signature request expired")
    if sig.status != "pending":
        raise HTTPException(status_code=409, detail="Signature request is not pending")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return sig


@router.post("/submit")
@limiter.limit("10/minute")
def submit_signature(
    payload: SignatureSubmit,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    sig = db.query(SignatureRequest).filter(SignatureRequest.token == payload.token).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signature request not found")
    if sig.status != "pending":
        raise HTTPException(status_code=409, detail="Signature request is not pending")
    if sig.expires_at and sig.expires_at < datetime.utcnow():
        sig.status = "expired"
        db.commit()
        raise HTTPException(status_code=410, detail="Signature request expired")

    repair = db.query(Repair).filter(Repair.id == sig.repair_id).first()
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")

    dest_dir = os.path.join("uploads", "signatures", f"repair-{repair.id}")
    filename = f"signature-{sig.request_type}.png"
    path = _save_signature_png(payload.image_base64, dest_dir, filename)

    if sig.request_type == "ingreso":
        repair.signature_ingreso_path = path
    else:
        repair.signature_retiro_path = path

    old_token = sig.token
    sig.status = "signed"
    sig.signed_at = datetime.utcnow()
    sig.signed_ip = request.client.host if request.client else None
    sig.signed_user_agent = request.headers.get("user-agent")
    # Rotate token after use to prevent replay
    sig.token = secrets.token_urlsafe(32)

    db.commit()

    _broadcast(old_token, "signature_received")
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return {"ok": True, "path": path}


@router.post("/requests/{request_id}/cancel")
def cancel_signature_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("signatures", "create")),
):
    sig = db.query(SignatureRequest).filter(SignatureRequest.id == request_id).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signature request not found")
    sig.status = "cancelled"
    db.commit()
    _broadcast(sig.token, "signature_cancelled")
    return {"ok": True}


@router.get("/stream/{token}")
async def stream_signature_events(token: str, response: Response, db: Session = Depends(get_db)):
    sig = db.query(SignatureRequest).filter(SignatureRequest.token == token).first()
    if not sig:
        raise HTTPException(status_code=404, detail="Signature request not found")
    if sig.expires_at and sig.expires_at < datetime.utcnow():
        sig.status = "expired"
        db.commit()
        raise HTTPException(status_code=410, detail="Signature request expired")
    if sig.status != "pending":
        raise HTTPException(status_code=409, detail="Signature request is not pending")
    queue: asyncio.Queue = asyncio.Queue()
    _channels.setdefault(token, []).append(queue)

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {event}\n\n"
        finally:
            _channels[token].remove(queue)

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
