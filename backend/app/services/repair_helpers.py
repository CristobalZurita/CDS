"""
Helpers compartidos para routers de reparaciones.

Estas funciones estaban duplicadas en repair.py, client.py, clients.py y
purchase_requests.py. Se extraen aquí para un único punto de verdad.
"""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.services.ot_code_service import repair_code as _repair_code


def auto_archive_repairs(db: Session) -> None:
    """Archiva automáticamente reparaciones entregadas hace más de 90 días."""
    cutoff = datetime.utcnow() - timedelta(days=90)
    to_archive = (
        db.query(Repair)
        .filter(Repair.delivery_date.isnot(None))
        .filter(Repair.archived_at.is_(None))
        .filter(Repair.delivery_date <= cutoff)
        .all()
    )
    if not to_archive:
        return
    for repair in to_archive:
        repair.archived_at = datetime.utcnow()
        repair.status_id = 9
    db.commit()


def resolved_repair_code(repair: Repair | None, client_id: int | None) -> str | None:
    """Devuelve el código OT legible del objeto Repair.

    Prioriza el repair_number cuando no es un código automático «R-…».
    Si hay ot_parent_id y ot_sequence construye el código jerárquico.
    """
    if not repair:
        return None
    if repair.repair_number and not str(repair.repair_number).startswith("R-"):
        return repair.repair_number
    if not client_id:
        return repair.repair_number

    if repair.ot_parent_id and repair.ot_sequence:
        if repair.ot_parent_id == repair.id:
            if int(repair.ot_sequence) <= 1:
                return _repair_code(client_id, repair.id)
            return _repair_code(client_id, repair.id, int(repair.ot_sequence))
        return _repair_code(client_id, int(repair.ot_parent_id), int(repair.ot_sequence))

    return _repair_code(client_id, repair.id)


def safe_pdf_filename(value: str) -> str:
    """Sanitiza un string para usarlo como nombre de archivo PDF."""
    text = str(value or "OT").strip()
    if not text:
        text = "OT"
    sanitized = []
    for char in text:
        if char.isalnum() or char in ("-", "_", "."):
            sanitized.append(char)
        else:
            sanitized.append("_")
    return "".join(sanitized)
