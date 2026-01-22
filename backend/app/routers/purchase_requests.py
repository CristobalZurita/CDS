from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_permission, get_current_user
from app.models.purchase_request import PurchaseRequest, PurchaseRequestItem
from app.schemas.purchase_request import PurchaseRequestCreate, PurchaseRequestOut

router = APIRouter(prefix="/purchase-requests", tags=["purchase_requests"])


@router.get("/", response_model=List[PurchaseRequestOut])
def list_purchase_requests(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    requests = db.query(PurchaseRequest).order_by(PurchaseRequest.updated_at.desc()).all()
    return requests


@router.post("/", response_model=PurchaseRequestOut, status_code=201)
def create_purchase_request(
    payload: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    req = PurchaseRequest(
        client_id=payload.client_id,
        repair_id=payload.repair_id,
        created_by=int(user.get("user_id")) if user else None,
        status="draft",
        notes=payload.notes,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    for item in payload.items:
        req_item = PurchaseRequestItem(
            request_id=req.id,
            product_id=item.product_id,
            sku=item.sku,
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price or 0.0,
            external_url=item.external_url,
            status="suggested",
        )
        db.add(req_item)
    db.commit()
    db.refresh(req)
    return req


@router.get("/{request_id}", response_model=PurchaseRequestOut)
def get_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    req = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    return req


@router.patch("/{request_id}")
def update_purchase_request_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
    req = db.query(PurchaseRequest).filter(PurchaseRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Purchase request not found")
    req.status = status
    db.commit()
    return {"ok": True}
