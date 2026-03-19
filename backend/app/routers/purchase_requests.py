from typing import List

from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_permission, get_current_user
from app.schemas import PaymentRead
from app.schemas.purchase_request import PurchaseRequestCreate, PurchaseRequestOut
from app.services.purchase_request_service import (
    _apply_request_stock_state,
    _get_request_or_404,
    build_purchase_requests_board,
    confirm_client_payment_for_request,
    create_purchase_request_record,
    delete_purchase_request_record,
    get_purchase_request_detail_payload,
    list_purchase_request_payments_for_request,
    list_purchase_requests_query,
    request_client_payment_for_request,
    update_purchase_request_status_record,
)

router = APIRouter(prefix="/purchase-requests", tags=["purchase_requests"])


@router.get("/", response_model=List[PurchaseRequestOut])
def list_purchase_requests(
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    return list_purchase_requests_query(db)


@router.get("/board")
def list_purchase_requests_board(
    status: str | None = Query(default=None),
    client_id: int | None = Query(default=None),
    repair_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    return build_purchase_requests_board(
        db,
        status=status,
        client_id=client_id,
        repair_id=repair_id,
    )


@router.post("/", response_model=PurchaseRequestOut, status_code=201)
def create_purchase_request(
    payload: PurchaseRequestCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    return create_purchase_request_record(payload, db, user)


@router.get("/{request_id}", response_model=PurchaseRequestOut)
def get_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    return _get_request_or_404(db, request_id)


@router.get("/{request_id}/detail")
def get_purchase_request_detail(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    return get_purchase_request_detail_payload(db, request_id)


@router.get("/{request_id}/payments", response_model=List[PaymentRead])
def list_purchase_request_payments(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "read")),
):
    return list_purchase_request_payments_for_request(db, request_id)


@router.post("/{request_id}/request-payment")
def request_client_payment(
    request_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
    return request_client_payment_for_request(request_id, payload, db, user)


@router.post("/{request_id}/confirm-payment")
def confirm_client_payment(
    request_id: int,
    payload: dict = Body(default={}),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
    return confirm_client_payment_for_request(request_id, payload, db, user)


@router.patch("/{request_id}")
def update_purchase_request_status(
    request_id: int,
    status: str | None = Query(default=None),
    payload: dict | None = Body(default=None),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "update")),
):
    return update_purchase_request_status_record(
        request_id,
        status=status,
        payload=payload,
        db=db,
        user=user,
    )


@router.delete("/{request_id}", status_code=204)
def delete_purchase_request(
    request_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("purchase_requests", "delete")),
):
    return delete_purchase_request_record(request_id, db, user)
