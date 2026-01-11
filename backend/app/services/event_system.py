"""
Event System - Maneja eventos de la aplicación

Permite que componentes disparen eventos y otros componentes reaccionen
sin acoplamiento directo. Se usa para enviar emails automáticos.
"""

from typing import Callable, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """
    Bus de eventos simple para manejo de eventos en la aplicación
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, handler: Callable):
        """
        Suscribirse a un evento
        
        Args:
            event_name: Nombre del evento (ej: 'quotation.created')
            handler: Función a ejecutar cuando se dispare el evento
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        
        self.listeners[event_name].append(handler)
        logger.debug(f"Subscriber added for event: {event_name}")
    
    def unsubscribe(self, event_name: str, handler: Callable):
        """
        Desuscribirse de un evento
        """
        if event_name in self.listeners:
            self.listeners[event_name].remove(handler)
            logger.debug(f"Subscriber removed for event: {event_name}")
    
    def emit(self, event_name: str, data: Any = None):
        """
        Dispara un evento
        
        Args:
            event_name: Nombre del evento
            data: Datos del evento
        """
        logger.debug(f"Event emitted: {event_name}")
        
        if event_name not in self.listeners:
            return
        
        for handler in self.listeners[event_name]:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error handling event {event_name}: {str(e)}")


# Global event bus instance
event_bus = EventBus()


# Event names
class Events:
    """Nombres de eventos disponibles"""
    
    # Quotation events
    QUOTATION_CREATED = 'quotation.created'
    QUOTATION_SAVED = 'quotation.saved'
    
    # Repair events
    REPAIR_CREATED = 'repair.created'
    REPAIR_UPDATED = 'repair.updated'
    REPAIR_STATUS_CHANGED = 'repair.status_changed'
    REPAIR_COMPLETED = 'repair.completed'
    
    # Appointment events
    APPOINTMENT_CREATED = 'appointment.created'
    APPOINTMENT_CANCELLED = 'appointment.cancelled'
    APPOINTMENT_REMINDER = 'appointment.reminder'
