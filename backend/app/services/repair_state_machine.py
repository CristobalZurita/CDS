"""
Repair State Machine - Validación de transiciones de estado para reparaciones
FASE 2: Implementación aditiva

Estados y transiciones válidas según el modelo de negocio:
    ingreso(1) → diagnostico(2), rechazado(10)
    diagnostico(2) → presupuesto(3), rechazado(10)
    presupuesto(3) → aprobado(4), rechazado(10)
    aprobado(4) → en_trabajo(5), rechazado(10)
    en_trabajo(5) → listo(6), rechazado(10)
    listo(6) → entregado(7), rechazado(10)
    entregado(7) → noventena(8)
    noventena(8) → archivado(9)
    archivado(9) → (terminal)
    rechazado(10) → archivado(9)
"""
from typing import Dict, Set, Optional
from fastapi import HTTPException, status


# =============================================================================
# Estado IDs según tabla repair_statuses
# =============================================================================
class RepairStateID:
    INGRESO = 1
    DIAGNOSTICO = 2
    PRESUPUESTO = 3
    APROBADO = 4
    EN_TRABAJO = 5
    LISTO = 6
    ENTREGADO = 7
    NOVENTENA = 8
    ARCHIVADO = 9
    RECHAZADO = 10


# =============================================================================
# Mapa de transiciones válidas: estado_actual -> {estados_permitidos}
# =============================================================================
VALID_TRANSITIONS: Dict[int, Set[int]] = {
    RepairStateID.INGRESO: {RepairStateID.DIAGNOSTICO, RepairStateID.RECHAZADO},
    RepairStateID.DIAGNOSTICO: {RepairStateID.PRESUPUESTO, RepairStateID.RECHAZADO},
    RepairStateID.PRESUPUESTO: {RepairStateID.APROBADO, RepairStateID.RECHAZADO},
    RepairStateID.APROBADO: {RepairStateID.EN_TRABAJO, RepairStateID.RECHAZADO},
    RepairStateID.EN_TRABAJO: {RepairStateID.LISTO, RepairStateID.RECHAZADO},
    RepairStateID.LISTO: {RepairStateID.ENTREGADO, RepairStateID.RECHAZADO},
    RepairStateID.ENTREGADO: {RepairStateID.NOVENTENA},
    RepairStateID.NOVENTENA: {RepairStateID.ARCHIVADO},
    RepairStateID.ARCHIVADO: set(),  # Terminal
    RepairStateID.RECHAZADO: {RepairStateID.ARCHIVADO},
}


# Nombres legibles para mensajes de error
STATE_NAMES: Dict[int, str] = {
    RepairStateID.INGRESO: "Ingreso",
    RepairStateID.DIAGNOSTICO: "Diagnóstico",
    RepairStateID.PRESUPUESTO: "Presupuesto",
    RepairStateID.APROBADO: "Aprobado",
    RepairStateID.EN_TRABAJO: "En trabajo",
    RepairStateID.LISTO: "Listo",
    RepairStateID.ENTREGADO: "Entregado",
    RepairStateID.NOVENTENA: "Noventena",
    RepairStateID.ARCHIVADO: "Archivado",
    RepairStateID.RECHAZADO: "Rechazado",
}


# Porcentaje de progreso por estado (para notificaciones)
STATE_PROGRESS: Dict[int, int] = {
    RepairStateID.INGRESO: 0,
    RepairStateID.DIAGNOSTICO: 15,
    RepairStateID.PRESUPUESTO: 30,
    RepairStateID.APROBADO: 40,
    RepairStateID.EN_TRABAJO: 60,
    RepairStateID.LISTO: 80,
    RepairStateID.ENTREGADO: 90,
    RepairStateID.NOVENTENA: 95,
    RepairStateID.ARCHIVADO: 100,
    RepairStateID.RECHAZADO: 0,
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
    if current_state_id in (RepairStateID.ARCHIVADO,):
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
    return state_id in (RepairStateID.ARCHIVADO,)


def get_allowed_transitions(current_state_id: int) -> Set[int]:
    """Obtiene el conjunto de estados a los que se puede transicionar desde el estado actual"""
    return VALID_TRANSITIONS.get(current_state_id, set())


def get_allowed_transitions_with_names(current_state_id: int) -> Dict[int, str]:
    """Obtiene las transiciones permitidas con sus nombres"""
    allowed = get_allowed_transitions(current_state_id)
    return {state_id: STATE_NAMES.get(state_id, str(state_id)) for state_id in allowed}
