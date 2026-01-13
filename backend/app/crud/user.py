"""
CRUD operations para usuarios
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.crud.base import CRUDBase
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.core.security import hash_password, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations para usuarios"""

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """
        Crea un nuevo usuario con contraseña hasheada
        Override del método base para hashear contraseña
        """
        # Convertir schema a dict y extraer password
        obj_data = obj_in.dict()
        plain_password = obj_data.pop("password")

        # Crear usuario con password hasheado
        db_obj = User(
            **obj_data,
            hashed_password=hash_password(plain_password)
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtiene usuario por email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Obtiene usuario por username"""
        return db.query(self.model).filter(self.model.username == username).first()

    def authenticate(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica usuario con email y contraseña
        Retorna el usuario si las credenciales son válidas, None en caso contrario
        """
        user = self.get_by_email(db, email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Verificar que el usuario esté activo
        if not user.is_active:
            return None

        return user

    def update_password(
        self,
        db: Session,
        user_id: int,
        new_password: str
    ) -> Optional[User]:
        """
        Actualiza la contraseña de un usuario
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.utcnow()

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_role(
        self,
        db: Session,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Obtiene usuarios filtrados por rol"""
        return (
            db.query(self.model)
            .filter(self.model.role == role)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Obtiene solo usuarios activos"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def deactivate(self, db: Session, user_id: int) -> Optional[User]:
        """
        Desactiva un usuario (soft delete)
        Marca is_active=False en lugar de eliminar
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.is_active = False
        user.updated_at = datetime.utcnow()

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def activate(self, db: Session, user_id: int) -> Optional[User]:
        """
        Reactiva un usuario desactivado
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.is_active = True
        user.updated_at = datetime.utcnow()

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_role(
        self,
        db: Session,
        user_id: int,
        new_role: UserRole
    ) -> Optional[User]:
        """
        Actualiza el rol de un usuario
        """
        user = self.get(db, user_id)
        if not user:
            return None

        user.role = new_role
        user.updated_at = datetime.utcnow()

        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# Instancia singleton
user = CRUDUser(User)
