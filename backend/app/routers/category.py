from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=List[CategoryRead], include_in_schema=False)
@router.get("/", response_model=List[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    svc = CategoryService(db)
    return svc.list_categories()

@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("categories", "create"))
):
    svc = CategoryService(db)
    return svc.create_category(payload.model_dump())

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("categories", "update"))
):
    svc = CategoryService(db)
    return svc.update_category(category_id, payload.model_dump(exclude_unset=True))

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), user: dict = Depends(require_permission("categories", "delete"))):
    svc = CategoryService(db)
    return svc.delete_category(category_id)
