"""
Repair State Machine - Validación de transiciones de estado para reparaciones
FASE 2: Implementación aditiva

Estados y transiciones válidas según el modelo de negocio:
    pending_quote(1) → quoted(2), cancelled(9)
    quoted(2) → approved(3), cancelled(9)
    approved(3) → in_progress(4), cancelled(9)
    in_progress(4) → waiting_parts(5), testing(6), cancelled(9)
    waiting_parts(5) → in_progress(4)
    testing(6) → in_progress(4), completed(7)
    completed(7) → delivered(8)
    delivered(8) → (terminal)
    cancelled(9) → (terminal)
"""
from typing import Dict, Set, Optional
from fastapi import HTTPException, status


# =============================================================================
# Estado IDs según tabla repair_statuses
# =============================================================================
class RepairStateID:
    PENDING_QUOTE = 1
    QUOTED = 2
    APPROVED = 3
    IN_PROGRESS = 4
    WAITING_PARTS = 5
    TESTING = 6
    COMPLETED = 7
    DELIVERED = 8
    CANCELLED = 9


# =============================================================================
# Mapa de transiciones válidas: estado_actual -> {estados_permitidos}
# =============================================================================
VALID_TRANSITIONS: Dict[int, Set[int]] = {
    RepairStateID.PENDING_QUOTE: {RepairStateID.QUOTED, RepairStateID.CANCELLED},
    RepairStateID.QUOTED: {RepairStateID.APPROVED, RepairStateID.CANCELLED},
    RepairStateID.APPROVED: {RepairStateID.IN_PROGRESS, RepairStateID.CANCELLED},
    RepairStateID.IN_PROGRESS: {RepairStateID.WAITING_PARTS, RepairStateID.TESTING, RepairStateID.CANCELLED},
    RepairStateID.WAITING_PARTS: {RepairStateID.IN_PROGRESS},
    RepairStateID.TESTING: {RepairStateID.IN_PROGRESS, RepairStateID.COMPLETED},
    RepairStateID.COMPLETED: {RepairStateID.DELIVERED},
    RepairStateID.DELIVERED: set(),  # Terminal
    RepairStateID.CANCELLED: set(),  # Terminal
}


# Nombres legibles para mensajes de error
STATE_NAMES: Dict[int, str] = {
    RepairStateID.PENDING_QUOTE: "Pendiente Cotización",
    RepairStateID.QUOTED: "Cotizado",
    RepairStateID.APPROVED: "Aprobado",
    RepairStateID.IN_PROGRESS: "En Progreso",
    RepairStateID.WAITING_PARTS: "Esperando Repuestos",
    RepairStateID.TESTING: "En Pruebas",
    RepairStateID.COMPLETED: "Completado",
    RepairStateID.DELIVERED: "Entregado",
    RepairStateID.CANCELLED: "Cancelado",
}


# Porcentaje de progreso por estado (para notificaciones)
STATE_PROGRESS: Dict[int, int] = {
    RepairStateID.PENDING_QUOTE: 0,
    RepairStateID.QUOTED: 10,
    RepairStateID.APPROVED: 20,
    RepairStateID.IN_PROGRESS: 40,
    RepairStateID.WAITING_PARTS: 50,
    RepairStateID.TESTING: 70,
    RepairStateID.COMPLETED: 90,
    RepairStateID.DELIVERED: 100,
    RepairStateID.CANCELLED: 0,
}


# =============================================================================
# Funciones de validación
# =============================================================================

def is_valid_transition(current_state_id: int, new_state_id: int) -> bool:
    """
    Verifica si una transición de estado es válida.

    Args:
        current_state_id: ID del estado actual
        new_state_id: ID del estado destino

    Returns:
        True si la transición es válida, False si no
    """
    if current_state_id not in VALID_TRANSITIONS:
        return False

    return new_state_id in VALID_TRANSITIONS[current_state_id]


def validate_transition(current_state_id: int, new_state_id: int) -> None:
    """
    Valida una transición de estado y lanza HTTPException si es inválida.

    Args:
        current_state_id: ID del estado actual
        new_state_id: ID del estado destino

    Raises:
        HTTPException: Si la transición no es válida
    """
    # Si es el mismo estado, no hay transición
    if current_state_id == new_state_id:
        return

    # Verificar si el estado actual es terminal
    if current_state_id in (RepairStateID.DELIVERED, RepairStateID.CANCELLED):
        current_name = STATE_NAMES.get(current_state_id, str(current_state_id))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede modificar una reparación en estado '{current_name}' (estado terminal)"
        )

    # Verificar si la transición es válida
    if not is_valid_transition(current_state_id, new_state_id):
        current_name = STATE_NAMES.get(current_state_id, str(current_state_id))
        new_name = STATE_NAMES.get(new_state_id, str(new_state_id))
        allowed = VALID_TRANSITIONS.get(current_state_id, set())
        allowed_names = [STATE_NAMES.get(s, str(s)) for s in allowed]

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición inválida: '{current_name}' → '{new_name}'. "
                   f"Transiciones permitidas desde '{current_name}': {allowed_names}"
        )


def get_state_name(state_id: int) -> str:
    """Obtiene el nombre legible de un estado"""
    return STATE_NAMES.get(state_id, f"Estado {state_id}")


def get_state_progress(state_id: int) -> int:
    """Obtiene el porcentaje de progreso de un estado"""
    return STATE_PROGRESS.get(state_id, 0)


def is_terminal_state(state_id: int) -> bool:
    """Verifica si un estado es terminal (no permite más transiciones)"""
    return state_id in (RepairStateID.DELIVERED, RepairStateID.CANCELLED)


def get_allowed_transitions(current_state_id: int) -> Set[int]:
    """Obtiene el conjunto de estados a los que se puede transicionar desde el estado actual"""
    return VALID_TRANSITIONS.get(current_state_id, set())


def get_allowed_transitions_with_names(current_state_id: int) -> Dict[int, str]:
    """Obtiene las transiciones permitidas con sus nombres"""
    allowed = get_allowed_transitions(current_state_id)
    return {state_id: STATE_NAMES.get(state_id, str(state_id)) for state_id in allowed}
