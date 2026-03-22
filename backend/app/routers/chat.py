"""
Router del chat inteligente web.
- POST /api/v1/chat/message  — conversación con Gemini Flash
- POST /api/v1/chat/contact  — envío de email de contacto desde el chat (sin Turnstile)
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatTurn(BaseModel):
    role: str  # "user" | "model"
    text: str


class ChatRequest(BaseModel):
    history: list[ChatTurn] = []
    message: str


class ChatResponse(BaseModel):
    reply: str
    handoff: Optional[str] = None
    handoff_url: Optional[str] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="message no puede estar vacío")

    from app.services.chat_service import process_message

    history = [{"role": t.role, "text": t.text} for t in payload.history]
    result = process_message(history, payload.message)
    return ChatResponse(**result)


class ChatContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


@router.post("/contact", status_code=201)
async def chat_contact(payload: ChatContactRequest):
    """
    Envía un correo al negocio desde el formulario inline del chat.
    No requiere Turnstile — el contexto del chat actúa como filtro.
    """
    from app.services.email_service import EmailService, build_email_html

    if not payload.name.strip() or not payload.message.strip():
        raise HTTPException(status_code=422, detail="Nombre y mensaje son obligatorios")

    subject = f"Consulta web desde el chat — {payload.name}"
    html_body = build_email_html(f"""
        <h2>Nuevo mensaje desde el chat web</h2>
        <p><strong>Nombre:</strong> {payload.name}</p>
        <p><strong>Email de respuesta:</strong> {payload.email}</p>
        <p><strong>Mensaje:</strong></p>
        <p style="white-space:pre-wrap">{payload.message}</p>
    """)

    svc = EmailService()
    ok = svc.send_email(svc.from_email, subject, html_body)
    if not ok:
        raise HTTPException(status_code=502, detail="No se pudo enviar el correo. Intenta de nuevo.")
    return {"ok": True}
