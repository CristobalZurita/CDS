"""
Pydantic schemas para usuarios
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para crear usuario"""
    email: EmailStr
    username: str = Field(..., min_length=3)
    full_name: str
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None
    role: Optional[str] = "client"


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(BaseModel):
    """Schema para respuesta de usuario (sin contraseña)"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: Optional[str] = None
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    

class UserDetailResponse(UserResponse):
    """Detalle completo del usuario"""
    updated_at: datetime


# Alias for compatibility with routers
UserRead = UserResponse
