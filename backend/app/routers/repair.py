"""
Router de Reparaciones
======================
Endpoints para gestión de reparaciones.
Usa permisos granulares (require_permission).
"""

from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.services.pdf_generator import generate_repair_closure_pdf_bytes
from app.services.repair_helpers import safe_pdf_filename as _safe_pdf_filename
from app.models.repair import Repair as RepairModel
from app.services.clockify_service import ClockifyService
from app.services.repair_read_service import RepairReadService
from app.services.repair_service import RepairService
from app.services.repair_write_service import RepairWriteService

router = APIRouter(prefix="/repairs", tags=["repairs"])


@router.get("/{repair_id}/clockify")
def get_repair_clockify_progress(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    import re
    repair = db.query(RepairModel).filter(RepairModel.id == repair_id).first()
    if not repair or not repair.clockify_project_id:
        return {"ok": False, "detail": "No Clockify project linked to this OT."}
    clockify = ClockifyService()
    entries = clockify.get_project_time_entries(repair.clockify_project_id)
    total_seconds = 0
    for entry in entries:
        duration = entry.get("timeInterval", {}).get("duration") or ""
        m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", duration)
        if m:
            h, mi, s = m.group(1), m.group(2), m.group(3)
            total_seconds += int(h or 0) * 3600 + int(mi or 0) * 60 + int(float(s or 0))
    return {
        "ok": True,
        "clockify_project_id": repair.clockify_project_id,
        "entries": entries,
        "total_seconds": total_seconds,
        "total_hours": round(total_seconds / 3600, 2),
    }


@router.get("")
@router.get("/")
def list_repairs(
    limit: int | None = None,
    sort: str | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    return RepairReadService(db).list_active_payloads(limit=limit, sort=sort)


@router.get("/archived")
def list_archived_repairs(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    return RepairReadService(db).list_archived_payloads()


@router.get("/next-code")
def get_next_repair_code(
    client_id: int,
    ot_parent_id: int | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    """
    Entrega código OT sugerido usando la nomenclatura oficial backend.

    - Sin `ot_parent_id`: sugiere próximo OT base (`CDS-XXX-OT-NNN`).
    - Con `ot_parent_id`: sugiere próximo código agrupado (`...-NN`).
    """
    return RepairReadService(db).get_next_repair_code_payload(
        client_id=client_id,
        ot_parent_id=ot_parent_id,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_repair(
    repair: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "create"))
):
    return RepairWriteService(db).create_repair_with_audit(repair, user)


@router.get("/{repair_id}")
def get_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    return RepairReadService(db).get_repair_detail_payload(repair_id)


@router.get("/{repair_id}/closure-pdf")
def download_repair_closure_pdf(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update")),
):
    payload = RepairReadService(db).get_closure_payload(repair_id)
    pdf_bytes = generate_repair_closure_pdf_bytes(payload)

    file_code = payload.get("repair_code") or payload.get("repair_number") or f"OT_{repair_id}"
    safe_code = _safe_pdf_filename(str(file_code))
    filename = f"CIERRE_{safe_code}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{repair_id}/intake-sheet")
def get_repair_intake_sheet(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read"))
):
    return RepairReadService(db).get_repair_intake_sheet_payload(repair_id)


@router.post("/{repair_id}/intake-sheet", status_code=status.HTTP_201_CREATED)
def upsert_repair_intake_sheet(
    repair_id: int,
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    write_result = RepairWriteService(db).upsert_repair_intake_sheet(repair_id, payload, user)
    return {
        "ok": True,
        "created": write_result["created"],
        "sheet": RepairReadService(db).serialize_intake_sheet(write_result["sheet"]),
    }


@router.post("/{repair_id}/archive")
def archive_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    return RepairWriteService(db).archive_repair(repair_id, user)


@router.post("/{repair_id}/notify")
def notify_client(
    repair_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    return RepairWriteService(db).notify_client(
        repair_id,
        background_tasks=background_tasks,
    )


@router.post("/{repair_id}/reactivate")
def reactivate_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    return RepairWriteService(db).reactivate_repair(repair_id)


@router.post("/{repair_id}/activate")
def activate_repair(
    repair_id: int,
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    """
    Activa una OT post-ingreso: guarda firma de intake y envía email T&C.
    Body: { signature_data?: str, terms_accepted?: bool }
    """
    return RepairWriteService(db).activate_repair(
        repair_id,
        signature_data=payload.get("signature_data"),
        terms_accepted=bool(payload.get("terms_accepted", False)),
    )


@router.put("/{repair_id}")
def update_repair(
    repair_id: int,
    repair: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "update"))
):
    user_id = int(user.get("user_id")) if user and user.get("user_id") else None
    return RepairWriteService(db).update_repair_with_audit(
        repair_id=repair_id,
        payload=repair,
        user_id=user_id,
    )


@router.delete("/{repair_id}")
def delete_repair(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "delete"))
):
    return RepairWriteService(db).delete_repair_with_audit(repair_id, user)


@router.get("/{repair_id}/audit")
def get_repair_audit(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    return RepairReadService(db).list_repair_audit(repair_id)


# ---------------------------------------------------------------------------
# Endpoints that use RepairService for transactional operations
# ---------------------------------------------------------------------------


@router.post("/{repair_id}/components", status_code=status.HTTP_201_CREATED)
def add_component_usage(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Registrar uso de un componente en una reparación y descontar stock"""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        from_reserved = str(payload.get("from_reserved", "false")).strip().lower() in ("1", "true", "yes", "on")
        skip_stock_check = str(payload.get("skip_stock_check", "false")).strip().lower() in ("1", "true", "yes", "on")
        usage = svc.add_component_usage(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            from_reserved=from_reserved,
            skip_stock_check=skip_stock_check,
            notes=payload.get("notes")
        )
        return usage
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repair_id}/components/reserve", status_code=status.HTTP_201_CREATED)
def reserve_component_stock(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Reservar stock para una reparación sin descontarlo del total físico."""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        result = svc.reserve_component(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            notes=payload.get("notes"),
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repair_id}/components/release", status_code=status.HTTP_200_OK)
def release_component_reservation(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Liberar stock previamente reservado para una reparación."""
    required = ("component_table", "component_id", "quantity")
    for k in required:
        if k not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing field: {k}")

    svc = RepairService(db)
    try:
        result = svc.release_component_reservation(
            repair_id=repair_id,
            component_table=str(payload["component_table"]),
            component_id=int(payload["component_id"]),
            quantity=int(payload["quantity"]),
            user_id=int(user.get("user_id")) if user and user.get("user_id") else None,
            notes=payload.get("notes"),
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repair_id}/components")
def list_component_usages(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    svc = RepairService(db)
    return svc.get_component_usages(repair_id)


@router.delete("/{repair_id}/components/{usage_id}", status_code=status.HTTP_200_OK)
def remove_component_usage(repair_id: int, usage_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Eliminar uso de componente y devolver stock al inventario"""
    svc = RepairService(db)
    try:
        user_id = int(user.get("user_id")) if user and user.get("user_id") else None
        result = svc.remove_component_usage(usage_id=usage_id, user_id=user_id)
        return {"ok": True, "message": "Component removed and stock restored", "restored_quantity": result.get("restored_quantity", 0)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repair_id}/notes", status_code=status.HTTP_201_CREATED)
def add_repair_note(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Agregar nota técnica o interna a una reparación"""
    return RepairWriteService(db).add_repair_note(repair_id, payload, user)


@router.get("/{repair_id}/notes")
def list_repair_notes(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    return RepairReadService(db).list_repair_notes(repair_id)


@router.post("/{repair_id}/photos", status_code=status.HTTP_201_CREATED)
def add_repair_photo(repair_id: int, payload: Dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "update"))):
    """Registrar URL de foto asociada a la reparación. For file uploads use `uploads` router."""
    return RepairWriteService(db).add_repair_photo(repair_id, payload)


@router.get("/{repair_id}/photos")
def list_repair_photos(repair_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("repairs", "read"))):
    return RepairReadService(db).list_repair_photos(repair_id)
