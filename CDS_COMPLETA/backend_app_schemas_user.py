"""
Pydantic schemas para usuarios
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para crear usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3)
    full_name: str
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """Schema para respuesta de usuario (sin contraseña)"""
    id: int
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detalle completo del usuario"""
    updated_at: datetime
