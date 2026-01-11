from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("/")
def send_contact(payload: dict):
    # Aquí podrías validar y enviar email o guardar en DB
    # Por ahora solo retornamos OK
    if not payload.get('email') or not payload.get('message'):
        raise HTTPException(status_code=400, detail="Missing email or message")
    return {"ok": True, "received": payload}
