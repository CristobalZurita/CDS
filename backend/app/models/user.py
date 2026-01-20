"""
Modelo User para SQLAlchemy - Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class UserRole(Base):
    """Modelo de roles de usuario"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)

    users = relationship("User", back_populates="role_obj")


class User(Base):
    """Modelo de usuario - coincide con schema real de cirujano.db"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=False, default=3)
    is_active = Column(Integer, default=1)
    is_verified = Column(Integer, default=0)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relaciones
    role_obj = relationship("UserRole", back_populates="users")
    repairs = relationship("Repair", back_populates="technician", foreign_keys="Repair.assigned_to")

    # Relación con nuevo sistema de roles granulares (ADITIVO - no reemplaza role_obj)
    assigned_roles = relationship(
        "Role",
        secondary="user_role_assignments",
        back_populates="users"
    )

    def __init__(self, **kwargs):
        full_name = kwargs.pop("full_name", None)
        role = kwargs.pop("role", None)
        if full_name and not kwargs.get("first_name") and not kwargs.get("last_name"):
            parts = str(full_name).strip().split()
            if parts:
                kwargs["first_name"] = parts[0]
                kwargs["last_name"] = " ".join(parts[1:]) if len(parts) > 1 else None
        if role and "role_id" not in kwargs:
            role_map = {"admin": 1, "technician": 2, "client": 3}
            if isinstance(role, str):
                kwargs["role_id"] = role_map.get(role.lower(), 3)
            elif isinstance(role, int):
                kwargs["role_id"] = role
        super().__init__(**kwargs)

    @property
    def full_name(self):
        """Propiedad para compatibilidad con código existente"""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.username or self.email

    @property
    def role(self):
        """Propiedad para compatibilidad - retorna nombre del rol"""
        if self.role_obj:
            return self.role_obj.name
        # Fallback basado en role_id
        role_map = {1: "admin", 2: "technician", 3: "client"}
        return role_map.get(self.role_id, "client")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role_id={self.role_id})>"
