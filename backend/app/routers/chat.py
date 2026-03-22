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

    try:
        history = [{"role": t.role, "text": t.text} for t in payload.history]
        result = process_message(history, payload.message)
        return ChatResponse(**result)
    except Exception as e:
        from app.core.llm_cascade import AllModelsExhaustedError
        from app.core.chat_context import get_handoff_url
        if isinstance(e, AllModelsExhaustedError):
            return ChatResponse(
                reply="El asistente está temporalmente saturado. Para seguir, escríbenos directamente.",
                handoff="email",
                handoff_url=get_handoff_url("email"),
            )
        raise HTTPException(status_code=502, detail=str(e))


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


# ── Asistente de ingreso ──────────────────────────────────────────────────────

class IntakeAssistRequest(BaseModel):
    marca: str
    modelo: str
    falla: str = ""


class IntakeAssistResponse(BaseModel):
    valor_usd_min: int
    valor_usd_max: int
    opciones_cobro: list[int]
    fallas_conocidas: list[str]
    tiempo_estimado: str
    complejidad: str
    notas: str


_INTAKE_SYSTEM_PROMPT = """
Eres el asistente técnico interno del taller "Cirujano de Sintetizadores" (CDS), Valparaíso, Chile.
El técnico trabaja SOLO. No hay equipo ni ayudantes.

REGLAS DE TIEMPO REALISTAS:
- Solo desmontar/montar un sintetizador puede tomar 20-60 minutos.
- Jornada efectiva real = 4-6 horas diarias (el técnico tiene vida: come, duerme, pasea perros, estudia).
- Un trabajo "de 1 día" según internet = 3-5 días reales en este taller.
- Nunca subestimes tiempos. Multiplica estimaciones de internet × 3.
- Fallas de teclado (contactos, sensores) suelen ser varios días solo de diagnóstico.

POLÍTICA DE COBROS (derecho a revisión en CLP):
- Es el costo por abrir y diagnosticar. Si el cliente acepta presupuesto, es abono al total.
- Si el cliente rechaza, queda en el taller. Nunca se cobran porcentajes anticipados.
- Mínimo siempre: 20000 CLP.
- Básico (equipo simple, falla conocida): 20000
- Medio (gama media): 35000
- Complejo (raro, difícil acceso): 60000
- Muy complejo/valioso: 90000
- Excepcional (alto valor comercial, falla muy rara): 150000+

Responde SOLO con JSON válido, sin texto adicional, sin bloques markdown.
""".strip()


@router.post("/intake-assist", response_model=IntakeAssistResponse)
async def intake_assist(payload: IntakeAssistRequest):
    """Sugiere cobro y contexto técnico para el ingreso de una OT."""
    from app.core.llm_cascade import query_json, AllModelsExhaustedError

    falla_txt = payload.falla.strip() or "No especificada aún"
    user_prompt = (
        f"Equipo ingresado al taller:\n"
        f"- Marca: {payload.marca}\n"
        f"- Modelo: {payload.modelo}\n"
        f"- Falla reportada: {falla_txt}\n\n"
        f"Responde con este JSON exacto (solo JSON, sin nada más):\n"
        f'{{"valor_usd_min": <int>, "valor_usd_max": <int>, '
        f'"opciones_cobro": [<lista 3-5 montos CLP, primero siempre 20000>], '
        f'"fallas_conocidas": [<lista 3-5 fallas comunes para este modelo>], '
        f'"tiempo_estimado": "<rango realista técnico solo, ej: 3-7 días>", '
        f'"complejidad": "<baja|media|alta|muy_alta>", '
        f'"notas": "<observación breve útil para el técnico>"}}'
    )

    try:
        result = query_json(user_prompt, _INTAKE_SYSTEM_PROMPT)
        return IntakeAssistResponse(**result)
    except AllModelsExhaustedError:
        raise HTTPException(status_code=503, detail="Asistente IA temporalmente no disponible")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
