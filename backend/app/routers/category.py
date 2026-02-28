from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", include_in_schema=False)
@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    svc = CategoryService(db)
    return svc.list_categories()

@router.post("", include_in_schema=False)
@router.post("/")
def create_category(payload: dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("categories", "create"))):
    svc = CategoryService(db)
    return svc.create_category(payload)

@router.put("/{category_id}")
def update_category(category_id: int, payload: dict, db: Session = Depends(get_db), user: dict = Depends(require_permission("categories", "update"))):
    svc = CategoryService(db)
    return svc.update_category(category_id, payload)

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("categories", "delete"))):
    svc = CategoryService(db)
    return svc.delete_category(category_id)
