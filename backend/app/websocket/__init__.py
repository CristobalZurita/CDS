"""
WebSocket Module - Fase 4 (ADITIVO)
==================================

Módulo para notificaciones en tiempo real.

Contiene:
- connection_manager.py: Gestor de conexiones WebSocket
"""

from app.websocket.connection_manager import (
    manager,
    ConnectionManager,
    MessageType,
    WebSocketMessage,
    notify_repair_status_change,
    notify_new_repair,
    notify_payment_received,
    notify_low_stock
)

__all__ = [
    'manager',
    'ConnectionManager', 
    'MessageType',
    'WebSocketMessage',
    'notify_repair_status_change',
    'notify_new_repair',
    'notify_payment_received',
    'notify_low_stock'
]
