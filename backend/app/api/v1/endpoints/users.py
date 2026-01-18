"""User endpoints (API v1)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.crud.user import create_user, list_users, get_user, update_user, delete_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
def list_users_endpoint(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    return list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    return create_user(db, payload)


@router.put("/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    user = update_user(db, user_id, payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    ok = delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
