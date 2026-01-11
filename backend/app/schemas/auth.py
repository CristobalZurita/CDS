"""
Pydantic schemas para autenticación
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Token(BaseModel):
    """Respuesta de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: int
    username: str
    email: str
    role: str


class LoginRequest(BaseModel):
    """Request de login"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Request de registro"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Request para recuperar contraseña"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirmación de reset de contraseña"""
    token: str
    new_password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Request para refrescar token"""
    refresh_token: str
