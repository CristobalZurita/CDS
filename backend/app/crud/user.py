"""CRUD for users (basic)."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


def _split_full_name(full_name: str | None) -> tuple[str | None, str | None]:
    parts = (full_name or "").strip().split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], " ".join(parts[1:])


def _role_to_id(role: str | None) -> int | None:
    if not role:
        return None
    role_map = {"admin": 1, "technician": 2, "client": 3}
    return role_map.get(str(role).strip().lower())


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        phone=payload.phone,
        role=payload.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, payload: UserUpdate) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    data = payload.model_dump(exclude_unset=True)
    if "full_name" in data:
        first_name, last_name = _split_full_name(data.pop("full_name"))
        user.first_name = first_name
        user.last_name = last_name
    if "role" in data:
        role_id = _role_to_id(data.pop("role"))
        if role_id is not None:
            user.role_id = role_id
    if "password" in data:
        password = data.pop("password")
        if password:
            user.hashed_password = hash_password(password)
    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
