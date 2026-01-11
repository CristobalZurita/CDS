"""
Dependencias de FastAPI: get_current_user, etc.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.security import verify_token, JWTError

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Obtiene el usuario actual desde el JWT token
    
    Uso en endpoint:
        @router.get("/profile")
        async def get_profile(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    
    Raises:
        HTTPException: Si el token es inválido o no está presente
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"user_id": user_id, **payload}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado o inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Obtiene el usuario actual y verifica que sea admin
    
    Uso en endpoint:
        @router.get("/admin/stats")
        async def get_stats(user: dict = Depends(get_current_admin)):
            return {"stats": {...}}
    """
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Solo administradores.",
        )
    return user


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Obtiene el usuario si está autenticado, sino retorna None
    Útil para endpoints que funcionan con o sin autenticación
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    try:
        payload = verify_token(token)
        return {"user_id": payload.get("sub"), **payload}
    except JWTError:
        return None
