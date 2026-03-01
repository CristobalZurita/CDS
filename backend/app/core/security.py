"""
Seguridad: JWT, password hashing, y utilidades de autenticación
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

try:
    from jose import JWTError, jwt  # type: ignore
except Exception as exc:
    raise RuntimeError(
        "python-jose is required for JWT operations. Install 'python-jose' to run the API."
    ) from exc
from app.core.config import settings

# Contexto para hashing de contraseñas
# Usar bcrypt directamente para evitar incompatibilidades con passlib
try:
    import bcrypt
    _bcrypt_available = True
except ImportError:
    _bcrypt_available = False

pbkdf2_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Configuración JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hash una contraseña usando bcrypt"""
    # Bcrypt has a 72-byte input limit. Truncate the UTF-8 encoded
    # password to avoid ValueError being raised by the backend hashing
    # implementation when a too-long password is supplied.
    try:
        pw_bytes = password.encode("utf-8")
    except Exception:
        # Fallback: coerce to str then encode
        pw_bytes = str(password).encode("utf-8")

    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]

    if _bcrypt_available:
        try:
            return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")
        except ValueError:
            # Fall through to pbkdf2 when the native bcrypt backend rejects
            # the input in constrained environments.
            pass

    # Pass the (possibly truncated) bytes back as string to the pbkdf2 fallback.
    safe_password = pw_bytes.decode("utf-8", errors="ignore")

    return pbkdf2_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash"""
    # Intentar con bcrypt directamente primero (evita bugs de passlib)
    if _bcrypt_available and hashed_password.startswith("$2"):
        try:
            password_bytes = plain_password.encode("utf-8")
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            pass  # Fallback a passlib

    # Fallback a passlib para otros esquemas
    try:
        return pbkdf2_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token de acceso
    
    Args:
        data: Datos a codificar (user_id, username, etc)
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Crea un JWT token de refresco (válido por 7 días)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_refresh_secret, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un JWT token
    
    Args:
        token: JWT token a verificar
    
    Returns:
        Payload decodificado
    
    Raises:
        JWTError: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Token inválido o expirado")


def verify_refresh_token(token: str) -> dict:
    """Verifica un token de refresco"""
    try:
        payload = jwt.decode(token, settings.jwt_refresh_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Refresh token inválido o expirado")


def verify_crypto_dependencies() -> None:
    """Fail fast if crypto dependencies are missing or misconfigured."""
    if jwt is None:
        raise RuntimeError("JWT provider unavailable (python-jose missing)")
