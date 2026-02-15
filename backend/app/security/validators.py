"""
Backend Security - Input Validators
Prevención de: SQL injection, XSS, buffer overflow, etc
Uso: validate_email(email), validate_password(pwd), etc
"""

import re
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, field_validator


class SecurityValidator:
    """Validadores de seguridad centralizados"""

    # Patrones de validación
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    MAX_STRING_LENGTH = 10000  # Prevenir buffer overflow

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar email"""
        if not email or len(email) > 255:
            return False
        return bool(SecurityValidator.EMAIL_PATTERN.match(email))

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validar contraseña
        Retorna (válido, mensaje_error)
        """
        if len(password) < SecurityValidator.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {SecurityValidator.PASSWORD_MIN_LENGTH} chars"

        if SecurityValidator.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"

        if SecurityValidator.PASSWORD_REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            return False, "Password must contain number"

        if SecurityValidator.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain special character"

        return True, ""

    @staticmethod
    def validate_string(value: str, max_length: Optional[int] = None) -> bool:
        """Validar string - sin caracteres peligrosos"""
        if not isinstance(value, str):
            return False

        max_len = max_length or SecurityValidator.MAX_STRING_LENGTH
        if len(value) > max_len:
            return False

        # ✅ Permitir caracteres normales, bloquear control characters
        if any(ord(c) < 32 and c not in '\n\t\r' for c in value):
            return False

        return True

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validar teléfono"""
        # +1 (555) 123-4567 o variantes
        pattern = re.compile(r'^\+?[\d\s\-()]{7,}$')
        return bool(pattern.match(phone))

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validar URL - Solo http/https"""
        pattern = re.compile(r'^https?://[^\s]+$')
        return bool(pattern.match(url))

    @staticmethod
    def validate_sql_injection(value: str) -> bool:
        """Detectar posibles SQL injection patterns"""
        dangerous_patterns = [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(\bUPDATE\b.*\bSET\b)",
            r"(.*;.*)",  # Stacked queries
            r"(/\*.*\*/)",  # Comments
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def sanitize_integer(value: Any, min_val: int = 0, max_val: int = 2147483647) -> Optional[int]:
        """Sanitizar número entero"""
        try:
            num = int(value)
            if min_val <= num <= max_val:
                return num
        except (ValueError, TypeError):
            pass
        return None


class LoginSchema(BaseModel):
    """Schema para login - validado por Pydantic"""
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password too short')
        return v


class RegisterSchema(BaseModel):
    """Schema para registro"""
    email: EmailStr
    password: str
    firstName: str
    lastName: str

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        is_valid, msg = SecurityValidator.validate_password(v)
        if not is_valid:
            raise ValueError(msg)
        return v

    @field_validator('firstName', 'lastName')
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not SecurityValidator.validate_string(v, max_length=100):
            raise ValueError('Invalid name')
        if len(v) < 2:
            raise ValueError('Name too short')
        return v


class UpdateUserSchema(BaseModel):
    """Schema para actualizar usuario"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        if v and not SecurityValidator.validate_phone(v):
            raise ValueError('Invalid phone number')
        return v
