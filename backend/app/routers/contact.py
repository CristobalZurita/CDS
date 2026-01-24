from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.ratelimit import limiter
from app.core.dependencies import get_current_admin, require_permission
from app.models.contact_message import ContactMessage
from app.schemas.contact import ContactCreate, ContactMessageOut
from app.services.event_system import event_bus, Events

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/", status_code=201)
@limiter.limit("5/minute")
def send_contact(
    payload: ContactCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    from app.services.turnstile_service import verify_turnstile
    if not payload.turnstile_token or not verify_turnstile(payload.turnstile_token, request.client.host if request.client else None):
        raise HTTPException(status_code=400, detail="Captcha inválido")
    message = ContactMessage(
        name=payload.name,
        email=payload.email,
        subject=payload.subject,
        message=payload.message,
        source_url=payload.source_url,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status="new",
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    # Emitir evento para notificaciones
    try:
        event_bus.emit(Events.CONTACT_MESSAGE_RECEIVED, {
            'message_id': message.id,
            'name': message.name,
            'email': message.email,
            'subject': message.subject,
            'message': message.message
        })
    except Exception:
        pass  # Notificación no debe romper el flujo principal

    return {"ok": True, "message_id": message.id}


@router.get("/messages", response_model=List[ContactMessageOut])
def list_messages(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("contact_messages", "read")),
):
    messages = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()
    return messages


@router.get("/messages/{message_id}", response_model=ContactMessageOut)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("contact_messages", "read")),
):
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
