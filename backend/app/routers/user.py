from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.core.security import hash_password


def _split_full_name(full_name: str) -> tuple[str | None, str | None]:
    parts = (full_name or "").strip().split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    return db.query(User).all()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    first_name, last_name = _split_full_name(user.full_name)
    db_user = User(
        email=user.email,
        username=user.username,
        first_name=first_name,
        last_name=last_name,
        hashed_password=hash_password(user.password),
        phone=user.phone,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    data = user.dict(exclude_unset=True)
    if "full_name" in data:
        first_name, last_name = _split_full_name(data.pop("full_name") or "")
        db_user.first_name = first_name
        db_user.last_name = last_name
    for key, value in data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"ok": True}
