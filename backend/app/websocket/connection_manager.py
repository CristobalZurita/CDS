"""
WebSocket Connection Manager - Fase 4 (============================================ADITIVO)
==

Sistema de WebSockets para notificaciones en tiempo real.
Permite enviar actualizaciones a clientes sin polling.

NO reemplaza nada existente - es ADITIVO.

Inspirado en:
- FastAPI WebSocket documentation
- Socket.IO pattern

Uso:
    from app.websocket.connection_manager import manager, ConnectionManager
    
    # Conectar
    await manager.connect(websocket, user_id)
    
    # Enviar a usuario específico
    await manager.send_personal_message(user_id, {"type": "repair_update", "data": {...}})
    
    # Enviar a todos los admins
    await manager.broadcast_to_admins({"type": "new_repair", "data": {...}})
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect


# Logger
logger = logging.getLogger(__name__)


# =============================================================================
# Tipos de mensajes
# =============================================================================
class MessageType:
    """Tipos de mensajes WebSocket"""
    REPAIR_STATUS_CHANGE = "repair_status_change"
    REPAIR_CREATED = "repair_created"
    REPAIR_COMPLETED = "repair_completed"
    PAYMENT_RECEIVED = "payment_received"
    NEW_APPOINTMENT = "new_appointment"
    INVENTORY_LOW_STOCK = "inventory_low_stock"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


@dataclass
class WebSocketMessage:
    """Mensaje estructurado para WebSocket"""
    type: str
    data: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: str = "normal"  # normal, high, critical
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp,
            "priority": self.priority
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        data = json.loads(json_str)
        return cls(
            type=data.get("type", "unknown"),
            data=data.get("data", {}),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            priority=data.get("priority", "normal")
        )


# =============================================================================
# Connection Manager
# =============================================================================
class ConnectionManager:
    """
    Gestor de conexiones WebSocket.
    
    Permite:
    - Conectar/desconectar clientes
    - Enviar mensajes a usuarios específicos
    - Broadcast a grupos (admins, técnicos)
    - Mantener alive con heartbeats
    """
    
    def __init__(self):
        # Conexiones activas: user_id -> List[WebSocket]
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
        # Conexiones por rol: role -> Set[WebSocket]
        self.role_connections: Dict[str, Set[WebSocket]] = {}
        
        # Mapping websocket -> user_id para rápido lookup
        self.ws_to_user: Dict[WebSocket, Optional[int]] = {}
        
        # Conexiones anónimas (sin auth)
        self.anonymous_connections: Set[WebSocket] = set()
        
        logger.info("WebSocket ConnectionManager initialized")
    
    async def connect(
        self, 
        websocket: WebSocket, 
        user_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> None:
        """
        Nueva conexión WebSocket.
        
        Args:
            websocket: La conexión WebSocket
            user_id: ID del usuario (None si es anónimo)
            role: Rol del usuario (admin, technician, client)
        """
        await websocket.accept()
        
        if user_id:
            # Usuario autenticado
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            self.ws_to_user[websocket] = user_id
            
            # Agregar por rol
            if role:
                if role not in self.role_connections:
                    self.role_connections[role] = set()
                self.role_connections[role].add(websocket)
            
            logger.info(f"WebSocket connected: user_id={user_id}, role={role}")
        else:
            # Conexión anónima
            self.anonymous_connections.add(websocket)
            self.ws_to_user[websocket] = None
            logger.info("WebSocket connected: anonymous")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Desconectar WebSocket.
        
        Args:
            websocket: La conexión a cerrar
        """
        user_id = self.ws_to_user.pop(websocket, None)
        
        if user_id and user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remover de conexiones por rol
        for role, connections in self.role_connections.items():
            if websocket in connections:
                connections.discard(websocket)
        
        # Remover de anónimas
        self.anonymous_connections.discard(websocket)
        
        logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(
        self, 
        user_id: int, 
        message: dict,
        priority: str = "normal"
    ) -> bool:
        """
        Enviar mensaje a un usuario específico.
        
        Args:
            user_id: ID del usuario destino
            message: Contenido del mensaje
            priority: Prioridad del mensaje
        
        Returns:
            True si se envió, False si el usuario no está conectado
        """
        if user_id not in self.active_connections:
            logger.debug(f"User {user_id} not connected, message not sent")
            return False
        
        ws_message = WebSocketMessage(
            type=message.get("type", "notification"),
            data=message.get("data", message),
            priority=priority
        )
        
        success = True
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(ws_message.to_json())
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                success = False
        
        return success
    
    async def send_personal_json(
        self, 
        user_id: int, 
        json_message: str
    ) -> bool:
        """Enviar JSON raw a usuario específico"""
        if user_id not in self.active_connections:
            return False
        
        success = True
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(json_message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                success = False
        
        return success
    
    async def broadcast_to_role(
        self, 
        role: str, 
        message: dict,
        priority: str = "normal"
    ) -> int:
        """
        Enviar mensaje a todos los usuarios con un rol específico.
        
        Args:
            role: Rol destino (admin, technician)
            message: Contenido del mensaje
            priority: Prioridad
        
        Returns:
            Número de conexiones receptoras
        """
        if role not in self.role_connections:
            logger.debug(f"No connections for role {role}")
            return 0
        
        ws_message = WebSocketMessage(
            type=message.get("type", "notification"),
            data=message.get("data", message),
            priority=priority
        )
        
        count = 0
        for websocket in list(self.role_connections[role]):
            try:
                await websocket.send_text(ws_message.to_json())
                count += 1
            except Exception as e:
                logger.error(f"Error broadcasting to role {role}: {e}")
                self.disconnect(websocket)
        
        return count
    
    async def broadcast_to_admins(
        self, 
        message: dict,
        priority: str = "normal"
    ) -> int:
        """Enviar mensaje a todos los administradores"""
        return await self.broadcast_to_role("admin", message, priority)
    
    async def broadcast_to_technicians(
        self, 
        message: dict,
        priority: str = "normal"
    ) -> int:
        """Enviar mensaje a todos los técnicos"""
        return await self.broadcast_to_role("technician", message, priority)
    
    async def broadcast_all(
        self, 
        message: dict,
        priority: str = "normal"
    ) -> int:
        """Enviar mensaje a todas las conexiones"""
        ws_message = WebSocketMessage(
            type=message.get("type", "notification"),
            data=message.get("data", message),
            priority=priority
        )
        
        # Broadcast a todos los usuarios autenticados
        count = 0
        all_ws = []
        for user_id, websockets in self.active_connections.items():
            all_ws.extend(websockets)
        
        for websocket in all_ws:
            try:
                await websocket.send_text(ws_message.to_json())
                count += 1
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
        
        return count
    
    def get_connected_users(self) -> List[int]:
        """Obtener lista de usuarios conectados"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """Obtener número total de conexiones"""
        return sum(len(ws_list) for ws_list in self.active_connections.values())
    
    def get_connection_count_by_role(self) -> Dict[str, int]:
        """Obtener número de conexiones por rol"""
        return {
            role: len(connections) 
            for role, connections in self.role_connections.items()
        }
    
    async def handle_heartbeat(self, websocket: WebSocket) -> bool:
        """Manejar heartbeat del cliente"""
        try:
            await websocket.send_text(json.dumps({
                "type": MessageType.HEARTBEAT,
                "timestamp": datetime.utcnow().isoformat()
            }))
            return True
        except Exception:
            return False


# =============================================================================
# Instancia global del manager
# =============================================================================
manager = ConnectionManager()


# =============================================================================
# Helper functions para eventos del sistema
# =============================================================================
async def notify_repair_status_change(
    repair_id: int,
    repair_number: str,
    old_status: str,
    new_status: str,
    client_id: int,
    technician_id: Optional[int] = None
) -> None:
    """
    Notificar cambio de estado de reparación.
    
    Args:
        repair_id: ID de la reparación
        repair_number: Número de OT
        old_status: Estado anterior
        new_status: Estado nuevo
        client_id: ID del cliente
        technician_id: ID del técnico asignado
    """
    message = {
        "type": MessageType.REPAIR_STATUS_CHANGE,
        "data": {
            "repair_id": repair_id,
            "repair_number": repair_number,
            "old_status": old_status,
            "new_status": new_status
        }
    }
    
    # Notificar al cliente
    await manager.send_personal_message(
        client_id,
        message,
        priority="high"
    )
    
    # Notificar al técnico si hay uno asignado
    if technician_id:
        await manager.send_personal_message(
            technician_id,
            message,
            priority="high"
        )
    
    # Notificar a todos los admins
    await manager.broadcast_to_admins(message, priority="normal")


async def notify_new_repair(
    repair_id: int,
    repair_number: str,
    client_name: str
) -> None:
    """Notificar nueva reparación a admins y técnicos"""
    message = {
        "type": MessageType.REPAIR_CREATED,
        "data": {
            "repair_id": repair_id,
            "repair_number": repair_number,
            "client_name": client_name
        }
    }
    
    await manager.broadcast_to_admins(message, priority="high")
    await manager.broadcast_to_technicians(message, priority="normal")


async def notify_payment_received(
    repair_id: int,
    repair_number: str,
    amount: float,
    client_id: int,
    technician_id: Optional[int] = None
) -> None:
    """Notificar pago recibido"""
    message = {
        "type": MessageType.PAYMENT_RECEIVED,
        "data": {
            "repair_id": repair_id,
            "repair_number": repair_number,
            "amount": amount
        }
    }
    
    await manager.send_personal_message(client_id, message, priority="high")
    
    if technician_id:
        await manager.send_personal_message(technician_id, message, priority="normal")
    
    await manager.broadcast_to_admins(message, priority="normal")


async def notify_low_stock(
    product_sku: str,
    product_name: str,
    current_stock: int,
    min_stock: int
) -> None:
    """Notificar stock bajo"""
    message = {
        "type": MessageType.INVENTORY_LOW_STOCK,
        "data": {
            "sku": product_sku,
            "name": product_name,
            "current_stock": current_stock,
            "min_stock": min_stock
        }
    }
    
    await manager.broadcast_to_admins(message, priority="high")
    await manager.broadcast_to_technicians(message, priority="normal")


# =============================================================================
# WebSocket Endpoint (se integra en main.py)
# =============================================================================
"""
# AGREGAR EN main.py (aditivo, no destructivo):

from app.websocket.connection_manager import manager, MessageType
from fastapi import WebSocket, WebSocketDisconnect
import json

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    '''
    Endpoint principal de WebSocket.
    
    Query params:
    - token: Token JWT de autenticación (opcional)
    - role: Rol del usuario (admin, technician, client)
    '''
    # Obtener user_id del token o params
    user_id = None
    role = websocket.query_params.get("role", "client")
    
    # Si hay token, validar y obtener user_id
    token = websocket.query_params.get("token")
    if token:
        try:
            # Validar token y obtener user_id
            payload = verify_token(token)
            user_id = payload.get("user_id")
        except:
            pass
    
    # Conectar
    await manager.connect(websocket, user_id, role)
    
    try:
        while True:
            # Esperar mensajes del cliente
            data = await websocket.receive_text()
            
            try:
                message = WebSocketMessage.from_json(data)
                
                # Manejar tipos de mensaje específicos
                if message.type == MessageType.HEARTBEAT:
                    await manager.handle_heartbeat(websocket)
                    
                elif message.type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from user {user_id}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected: user_id={user_id}")
"""
