"""
Event Handlers Setup

Registra los manejadores de eventos para el sistema de notificaciones
"""

import logging
from app.services.event_system import event_bus, Events
from app.services.email_service import email_service
from app.services.clockify_service import ClockifyService
from app.websocket.connection_manager import manager
from app.services.repair_state_machine import RepairStateID
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


def setup_event_handlers():
    """
    Registra todos los manejadores de eventos
    """
    logger.info("Setting up event handlers...")
    
    # Quotation events
    event_bus.subscribe(Events.QUOTATION_SAVED, handle_quotation_saved)
    
    # Repair events
    event_bus.subscribe(Events.REPAIR_CREATED, handle_repair_created)
    event_bus.subscribe(Events.REPAIR_STATUS_CHANGED, handle_repair_status_changed)
    event_bus.subscribe(Events.REPAIR_STATUS_CHANGED, handle_repair_clockify_integration)
    event_bus.subscribe(Events.REPAIR_STATUS_CHANGED, handle_repair_websocket_broadcast)
    event_bus.subscribe(Events.REPAIR_COMPLETED, handle_repair_completed)
    
    # Appointment events
    event_bus.subscribe(Events.APPOINTMENT_CREATED, handle_appointment_created)
    event_bus.subscribe(Events.APPOINTMENT_REMINDER, handle_appointment_reminder)

    # Contact events
    event_bus.subscribe(Events.CONTACT_MESSAGE_RECEIVED, handle_contact_message_received)

    logger.info("✓ Event handlers registered")


# ============================================================================
# QUOTATION HANDLERS
# ============================================================================

def handle_quotation_saved(data):
    """
    Maneja evento cuando una cotización es guardada
    
    Esperado: {
        'customer_email': str,
        'customer_name': str,
        'quotation_id': str,
        'instrument': str,
        'min_price': float,
        'max_price': float
    }
    """
    try:
        email_service.send_quotation_saved_email(
            email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            quotation_id=data.get('quotation_id'),
            instrument=data.get('instrument'),
            min_price=data.get('min_price', 0),
            max_price=data.get('max_price', 0)
        )
        logger.info(f"Quotation saved email sent to {data.get('customer_email')}")
    except Exception as e:
        logger.error(f"Error handling quotation saved event: {str(e)}")


# ============================================================================
# REPAIR HANDLERS
# ============================================================================

def handle_repair_created(data):
    """
    Maneja evento cuando una reparación es creada
    
    Esperado: {
        'customer_email': str,
        'customer_name': str,
        'repair_id': str,
        'instrument': str,
        'fault_description': str,
        'estimated_completion': str
    }
    """
    try:
        email_service.send_repair_created_email(
            email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            repair_id=data.get('repair_id'),
            instrument=data.get('instrument'),
            fault_description=data.get('fault_description'),
            estimated_completion=data.get('estimated_completion')
        )
        logger.info(f"Repair created email sent to {data.get('customer_email')}")
    except Exception as e:
        logger.error(f"Error handling repair created event: {str(e)}")


def handle_repair_status_changed(data):
    """
    Maneja evento cuando el status de una reparación cambia
    
    Esperado: {
        'customer_email': str,
        'customer_name': str,
        'repair_id': str,
        'status': str,
        'progress': int,
        'notes': str (optional)
    }
    """
    try:
        email_service.send_repair_status_email(
            email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            repair_id=data.get('repair_id'),
            status=data.get('status'),
            progress=data.get('progress', 0),
            notes=data.get('notes')
        )
        logger.info(f"Repair status email sent to {data.get('customer_email')}")
    except Exception as e:
        logger.error(f"Error handling repair status changed event: {str(e)}")


def handle_repair_completed(data):
    """
    Maneja evento cuando una reparación es completada y está lista para recoger
    
    Esperado: {
        'customer_email': str,
        'customer_name': str,
        'repair_id': str,
        'instrument': str,
        'total_cost': float
    }
    """
    try:
        email_service.send_ready_for_pickup_email(
            email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            repair_id=data.get('repair_id'),
            instrument=data.get('instrument'),
            total_cost=data.get('total_cost', 0)
        )
        logger.info(f"Repair completed email sent to {data.get('customer_email')}")
    except Exception as e:
        logger.error(f"Error handling repair completed event: {str(e)}")


# ============================================================================
# APPOINTMENT HANDLERS
# ============================================================================

def handle_appointment_created(data):
    """
    Maneja evento cuando una cita es creada
    
    Esperado: {
        'customer_email': str,
        'customer_name': str,
        'appointment_date': str,
        'appointment_time': str
    }
    """
    try:
        # El email de confirmación se puede enviar inmediatamente
        email_service.send_appointment_reminder_email(
            email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            appointment_date=data.get('appointment_date'),
            appointment_time=data.get('appointment_time')
        )
        logger.info(f"Appointment confirmation email sent to {data.get('customer_email')}")
    except Exception as e:
        logger.error(f"Error handling appointment created event: {str(e)}")


def handle_appointment_reminder(data):
    """
    Maneja evento de recordatorio de cita (24 horas antes)

    Esperado: {
        'customer_email': str,
        'customer_name': str,
        'appointment_date': str,
        'appointment_time': str
    }
    """
    try:
        email_service.send_appointment_reminder_email(
            email=data.get('customer_email'),
            customer_name=data.get('customer_name'),
            appointment_date=data.get('appointment_date'),
            appointment_time=data.get('appointment_time')
        )
        logger.info(f"Appointment reminder email sent to {data.get('customer_email')}")
    except Exception as e:
        logger.error(f"Error handling appointment reminder event: {str(e)}")


# ============================================================================
# CONTACT HANDLERS
# ============================================================================

def handle_contact_message_received(data):
    """
    Maneja evento cuando se recibe un mensaje de contacto.
    Notifica al equipo administrativo sobre el nuevo mensaje.

    Esperado: {
        'message_id': int,
        'name': str,
        'email': str,
        'subject': str,
        'message': str
    }
    """
    try:
        # Log del mensaje recibido (el email al admin se puede implementar si es necesario)
        logger.info(
            f"Contact message received - ID: {data.get('message_id')}, "
            f"From: {data.get('name')} <{data.get('email')}>, "
            f"Subject: {data.get('subject')}"
        )

        # Aquí se podría agregar notificación por email al admin si se configura
        # email_service.send_admin_notification(...)

    except Exception as e:
        logger.error(f"Error handling contact message event: {str(e)}")


# ============================================================================
# CLOCKIFY INTEGRATION HANDLERS
# ============================================================================

def handle_repair_clockify_integration(data):
    """
    Maneja integración Clockify para cambios de estado OT.
    Inicia/detiene time entries según estado.

    Esperado: {
        'repair_id': str,  # repair_number
        'status': str,     # nombre del estado
        'progress': int    # porcentaje de progreso
    }
    """
    try:
        from app.models.repair import Repair
        from app.core.database import get_db_session

        repair_number = data.get('repair_id')
        status_name = data.get('status')

        if not repair_number:
            return

        # Buscar repair por número
        db = SessionLocal()
        try:
            repair = db.query(Repair).filter(Repair.repair_number == repair_number).first()
            if not repair or not repair.clockify_project_id:
                return

            clockify = ClockifyService()

            # Lógica según estado
            if status_name == "En trabajo":
                # Iniciar time entry si no hay uno activo
                active_entry = clockify.get_active_time_entry(repair.clockify_project_id)
                if not active_entry:
                    clockify.start_time_entry(
                        repair.clockify_project_id,
                        f"Trabajo en OT {repair.repair_number}"
                    )
                    logger.info(f"Clockify: Started time entry for OT {repair_number}")

            elif status_name in ["Listo", "Entregado"]:
                # Detener time entry activo
                if clockify.stop_current_time_entry(repair.clockify_project_id):
                    logger.info(f"Clockify: Stopped time entry for OT {repair_number}")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error handling Clockify integration: {str(e)}")


# ============================================================================
# WEBSOCKET BROADCAST HANDLERS
# ============================================================================

def handle_repair_websocket_broadcast(data):
    """
    Broadcast cambios de estado OT a todos los clientes conectados via WebSocket.

    Esperado: {
        'repair_id': str,
        'status': str,
        'progress': int,
        'customer_name': str
    }
    """
    try:
        import asyncio
        from app.websocket.connection_manager import MessageType

        # Broadcast a todos los usuarios conectados
        message = {
            "type": MessageType.REPAIR_STATUS_CHANGE,
            "data": {
                "repair_id": data.get('repair_id'),
                "status": data.get('status'),
                "progress": data.get('progress', 0),
                "customer_name": data.get('customer_name'),
                "timestamp": data.get('timestamp')
            }
        }

        # Ejecutar broadcast de forma asíncrona
        asyncio.create_task(manager.broadcast_all(message))

        logger.info(f"WebSocket broadcast: OT {data.get('repair_id')} status changed to {data.get('status')}")

    except Exception as e:
        logger.error(f"Error broadcasting repair status change: {str(e)}")
