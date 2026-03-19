from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.services.client_portal_service import (
    audit_client_closure_pdf_download,
    build_client_closure_pdf_payload,
    create_store_purchase_request_record,
    get_dashboard_payload,
    get_profile_payload,
    get_repair_details_payload,
    get_repair_timeline_payload,
    list_client_purchase_requests_payload,
    list_client_repairs_payload,
    submit_client_deposit_proof_record,
    update_profile_payload,
)
from app.services.pdf_generator import generate_repair_closure_pdf_bytes

router = APIRouter(prefix="/client", tags=["client"])


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return get_dashboard_payload(db, int(user["user_id"]))


@router.get("/repairs")
def list_client_repairs(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return list_client_repairs_payload(db, int(user["user_id"]))


@router.get("/repairs/{repair_id}/timeline")
def get_repair_timeline(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return get_repair_timeline_payload(db, int(user["user_id"]), repair_id)


@router.get("/repairs/{repair_id}/details")
def get_repair_details(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return get_repair_details_payload(db, int(user["user_id"]), repair_id)


@router.get("/repairs/{repair_id}/closure-pdf")
def get_client_repair_closure_pdf(
    repair_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    payload, filename, user_id = build_client_closure_pdf_payload(
        db,
        int(user["user_id"]),
        repair_id,
    )
    pdf_bytes = generate_repair_closure_pdf_bytes(payload)
    audit_client_closure_pdf_download(repair_id, filename, user_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return get_profile_payload(db, int(user["user_id"]))


@router.put("/profile")
def update_profile(
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return update_profile_payload(db, int(user["user_id"]), payload)


@router.get("/purchase-requests")
def list_client_purchase_requests(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return list_client_purchase_requests_payload(db, int(user["user_id"]))


@router.post("/store/purchase-requests")
def create_store_purchase_request(
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return create_store_purchase_request_record(db, int(user["user_id"]), payload)


@router.post("/purchase-requests/{request_id}/deposit-proof")
def submit_client_deposit_proof(
    request_id: int,
    payload: Dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("repairs", "read")),
):
    return submit_client_deposit_proof_record(db, int(user["user_id"]), request_id, payload)
