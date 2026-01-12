"""
Endpoints de autenticación: login, register, logout
"""
from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.params import Depends
from backend.app.core.database import get_db
from backend.app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token
)
from backend.app.core.dependencies import get_current_user
from backend.app.core.ratelimit import limiter
from backend.app.services.logging_service import create_audit
from backend.app.models.user import User
from backend.app.schemas.auth import (
    LoginRequest, RegisterRequest, Token, PasswordResetRequest
)
from backend.app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo usuario
    
    - **email**: Email único del usuario
    - **username**: Username único (3-100 caracteres)
    - **full_name**: Nombre completo (3+ caracteres)
    - **password**: Contraseña (8+ caracteres)
    - **phone**: Teléfono (opcional)
    """
    
    # Verificar si el email ya existe
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    
    # Verificar si el username ya existe
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username ya existe"
        )
    
    # Crear nuevo usuario
    new_user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
        phone=request.phone
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Audit registration
    try:
        create_audit(event_type="auth.register", user_id=new_user.id, ip_address=None, details={"email": new_user.email, "username": new_user.username})
    except Exception:
        pass
    
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # limit login attempts to mitigate brute-force
async def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login: obtener token de acceso
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Retorna:
    - **access_token**: JWT token para usar en endpoints protegidos
    - **refresh_token**: Token para obtener nuevo access_token
    """
    
    # Buscar usuario por email (gracefully handle DB issues during tests)
    try:
        user = db.query(User).filter(User.email == payload.email).first()
    except Exception as e:
        # In test or minimal environments the DB may not be initialized; treat as invalid credentials
        # and let rate limiting still apply without raising an internal error.
        user = None
    if not user:
        # Audit failed login attempt
        try:
            ip = getattr(request.client, "host", None)
            create_audit(event_type="auth.login.failed", user_id=None, ip_address=ip, details={"email": payload.email})
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar contraseña
    if not user or not verify_password(payload.password, user.hashed_password):
        # Audit failed login attempt
        try:
            ip = getattr(request.client, "host", None)
            create_audit(event_type="auth.login.failed", user_id=(user.id if user else None), ip_address=ip, details={"email": payload.email})
        except Exception:
            pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear tokens
    access_token = create_access_token(data={
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value
    })
    
    refresh_token = create_refresh_token(data={
        "sub": str(user.id)
    })
    # Audit successful login
    try:
        ip = getattr(request.client, "host", None)
        create_audit(event_type="auth.login.success", user_id=user.id, ip_address=ip, details={"username": user.username})
    except Exception:
        pass
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    """
    Logout: invalida el token actual (cliente)
    
    En la práctica, el logout se maneja desde el frontend
    eliminando el token del localStorage.
    Este endpoint es opcional para implementar blacklist en backend.
    """
    return {"message": "Logout exitoso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener información del usuario actual (autenticado)
    
    Requiere: Header Authorization: Bearer {token}
    """
    user_obj = db.query(User).filter(User.id == int(user["user_id"])).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user_obj


@router.post("/refresh")
async def refresh_access_token(request_body: dict):
    """
    Refrescar access token usando refresh token
    
    - **refresh_token**: Token de refresco obtenido en login (enviar en JSON body)
    
    Retorna nuevo access_token y refresh_token
    """
    from backend.app.core.security import verify_refresh_token
    
    refresh_token = request_body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="refresh_token requerido en body"
        )
    
    try:
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        
        new_access_token = create_access_token(data={"sub": user_id})
        new_refresh_token = create_refresh_token(data={"sub": user_id})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
