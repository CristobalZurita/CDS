"""
WebSocket Router - Fase 4 (ADITIVO)

Endpoint WebSocket para conexiones en tiempo real.
Permite a los clientes recibir actualizaciones sin polling.
"""

from fastapi import APIRouter, WebSocket, Depends, HTTPException, status
from app.websocket.connection_manager import manager

router = APIRouter(prefix="/ws")


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = None
):
    """
    WebSocket endpoint para notificaciones en tiempo real.

    Los clientes pueden conectarse para recibir actualizaciones de:
    - Cambios de estado de OT
    - Nuevas reparaciones
    - Pagos recibidos
    - Etc.

    Args:
        websocket: Conexión WebSocket
        token: JWT token opcional para autenticación
    """
    user_id = None

    # Autenticación opcional
    if token:
        try:
            # Validar token y obtener user_id
            from app.core.auth import verify_token
            payload = verify_token(token)
            user_id = payload.get("user_id")
        except Exception:
            # Token inválido, continuar como anónimo
            pass

    # Conectar al manager
    await manager.connect(websocket, user_id)

    try:
        # Mantener conexión viva
        while True:
            # Esperar mensajes del cliente (ping/pong)
            data = await websocket.receive_text()
            # Aquí se podrían procesar mensajes del cliente si es necesario

    except Exception:
        # Desconectar al finalizar
        manager.disconnect(websocket)