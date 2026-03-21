from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stock_movement import StockMovement
from app.models.stock import Stock
from app.core.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/stock-movements", tags=["StockMovements"])


def _serialize_stock_movement(entry: StockMovement) -> dict:
    stock = entry.stock
    return {
        "id": entry.id,
        "stock_id": entry.stock_id,
        "movement_type": entry.movement_type,
        "quantity": entry.quantity,
        "repair_id": entry.repair_id,
        "notes": entry.notes,
        "performed_by": entry.performed_by,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "component_table": stock.component_table if stock else None,
        "component_id": stock.component_id if stock else None,
    }


@router.get("/")
def list_movements(
    stock_id: Optional[int] = None,
    product_id: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("stock_movements", "read")),
):
    query = db.query(StockMovement).join(Stock, Stock.id == StockMovement.stock_id)

    if stock_id is not None:
        query = query.filter(StockMovement.stock_id == stock_id)

    if product_id is not None:
        query = query.filter(
            Stock.component_table == "products",
            Stock.component_id == product_id,
        )

    rows = (
        query
        .order_by(StockMovement.created_at.desc(), StockMovement.id.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_stock_movement(entry) for entry in rows]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_movement(
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("stock_movements", "create")),
):
    required = ("stock_id", "movement_type", "quantity")
    for field in required:
        if payload.get(field) in (None, ""):
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    stock = db.query(Stock).filter(Stock.id == int(payload["stock_id"])).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    db_obj = StockMovement(
        stock_id=int(payload["stock_id"]),
        movement_type=str(payload["movement_type"]).strip(),
        quantity=int(payload["quantity"]),
        repair_id=int(payload["repair_id"]) if payload.get("repair_id") else None,
        notes=str(payload.get("notes") or "").strip() or None,
        performed_by=int(user.get("user_id")) if user and user.get("user_id") else None,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return _serialize_stock_movement(db_obj)
