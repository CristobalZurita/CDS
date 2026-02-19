"""
Servicio transaccional para dominio Repair
Maneja: ComponentUsage → Stock → StockMovement → Costos
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, List

from app.models.repair import Repair, RepairStatus
from app.models.repair_component_usage import RepairComponentUsage
from app.models.repair_photo import RepairPhoto
from app.models.repair_note import RepairNote
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.services.repair_state_machine import (
    validate_transition,
    get_state_name,
    get_state_progress,
    RepairStateID,
)
from app.services.event_system import event_bus, Events
from app.services.logging_service import create_audit


class RepairService:
    """Servicio para operaciones transaccionales de reparación"""

    def __init__(self, db: Session):
        self.db = db

    def get_repair(self, repair_id: int) -> Repair:
        """Obtiene reparación por ID"""
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reparación {repair_id} no encontrada"
            )
        return repair

    def is_repair_closed(self, repair: Repair) -> bool:
        """Verifica si la reparación está cerrada (delivered)"""
        if repair.status_obj:
            return repair.status_obj.code in ('archivado', 'rechazado')
        return repair.status_id in (RepairStateID.ARCHIVADO, RepairStateID.RECHAZADO)

    def add_component_usage(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        from_reserved: bool = False,
        notes: Optional[str] = None
    ) -> RepairComponentUsage:
        """
        Agrega uso de componente a reparación.
        TRANSACCIÓN ATÓMICA:
        1. Verifica stock disponible
        2. Crea RepairComponentUsage
        3. Descuenta Stock
        4. Registra StockMovement (OUT)
        5. Actualiza parts_cost en Repair
        """
        repair = self.get_repair(repair_id)

        if self.is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar reparación cerrada"
            )

        # Buscar stock del componente
        stock = self.db.query(Stock).filter(
            Stock.component_table == component_table,
            Stock.component_id == component_id
        ).first()

        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock no encontrado para {component_table}.{component_id}"
            )

        # Verificar disponibilidad
        available = stock.available_quantity
        if from_reserved:
            reserved_qty = stock.quantity_reserved or 0
            if reserved_qty < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reserva insuficiente. Reservado: {reserved_qty}, Requerido: {quantity}"
                )
        elif available < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {available}, Requerido: {quantity}"
            )

        try:
            # 1. Crear registro de uso de componente
            usage = RepairComponentUsage(
                repair_id=repair_id,
                component_table=component_table,
                component_id=component_id,
                quantity=quantity,
                unit_cost=stock.unit_cost,
                notes=notes
            )
            self.db.add(usage)

            # 2. Descontar stock
            if from_reserved:
                stock.quantity_reserved = max((stock.quantity_reserved or 0) - quantity, 0)
            stock.quantity -= quantity
            stock.updated_at = datetime.utcnow()

            # 3. Registrar movimiento de stock
            movement = StockMovement(
                stock_id=stock.id,
                movement_type="OUT_RESERVED" if from_reserved else "OUT",
                quantity=quantity,
                repair_id=repair_id,
                notes=f"Uso en reparación #{repair.repair_number}",
                performed_by=user_id
            )
            self.db.add(movement)

            # 4. Actualizar parts_cost en repair
            self._recalculate_parts_cost(repair)

            self.db.commit()
            self.db.refresh(usage)
            return usage

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(e)}"
            )

    def reserve_component(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        notes: Optional[str] = None,
    ) -> dict:
        """
        Reserva stock para una reparación sin consumirlo todavía.
        """
        repair = self.get_repair(repair_id)

        if self.is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede reservar en reparación cerrada"
            )

        stock = self.db.query(Stock).filter(
            Stock.component_table == component_table,
            Stock.component_id == component_id
        ).first()

        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock no encontrado para {component_table}.{component_id}"
            )

        available = stock.available_quantity
        if available < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para reservar. Disponible: {available}, Requerido: {quantity}"
            )

        try:
            stock.quantity_reserved = (stock.quantity_reserved or 0) + quantity
            stock.updated_at = datetime.utcnow()

            movement = StockMovement(
                stock_id=stock.id,
                movement_type="RESERVE",
                quantity=quantity,
                repair_id=repair_id,
                notes=notes or f"Reserva para reparación #{repair.repair_number}",
                performed_by=user_id
            )
            self.db.add(movement)

            self.db.commit()
            self.db.refresh(stock)
            return {
                "stock_id": stock.id,
                "reserved_quantity": quantity,
                "total_reserved": stock.quantity_reserved or 0,
                "available_quantity": stock.available_quantity,
            }
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(e)}"
            )

    def release_component_reservation(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        notes: Optional[str] = None,
    ) -> dict:
        """
        Libera reserva de stock asociada a reparación.
        """
        repair = self.get_repair(repair_id)

        if self.is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede liberar reserva en reparación cerrada"
            )

        stock = self.db.query(Stock).filter(
            Stock.component_table == component_table,
            Stock.component_id == component_id
        ).first()

        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock no encontrado para {component_table}.{component_id}"
            )

        current_reserved = stock.quantity_reserved or 0
        if current_reserved <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay reserva para liberar"
            )

        release_qty = min(quantity, current_reserved)

        try:
            stock.quantity_reserved = current_reserved - release_qty
            stock.updated_at = datetime.utcnow()

            movement = StockMovement(
                stock_id=stock.id,
                movement_type="UNRESERVE",
                quantity=release_qty,
                repair_id=repair_id,
                notes=notes or f"Liberación de reserva reparación #{repair.repair_number}",
                performed_by=user_id
            )
            self.db.add(movement)

            self.db.commit()
            self.db.refresh(stock)
            return {
                "stock_id": stock.id,
                "released_quantity": release_qty,
                "total_reserved": stock.quantity_reserved or 0,
                "available_quantity": stock.available_quantity,
            }
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(e)}"
            )

    def remove_component_usage(
        self,
        usage_id: int,
        user_id: Optional[int]
    ) -> dict:
        """
        Elimina uso de componente y devuelve stock.
        TRANSACCIÓN ATÓMICA:
        1. Obtiene RepairComponentUsage
        2. Devuelve cantidad a Stock
        3. Registra StockMovement (RETURN)
        4. Elimina RepairComponentUsage
        5. Recalcula parts_cost
        """
        usage = self.db.query(RepairComponentUsage).filter(
            RepairComponentUsage.id == usage_id
        ).first()

        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Uso de componente {usage_id} no encontrado"
            )

        repair = self.get_repair(usage.repair_id)

        if self.is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar reparación cerrada"
            )

        # Buscar stock
        stock = self.db.query(Stock).filter(
            Stock.component_table == usage.component_table,
            Stock.component_id == usage.component_id
        ).first()

        try:
            if stock:
                # Devolver al stock
                stock.quantity += usage.quantity
                stock.updated_at = datetime.utcnow()

                # Registrar movimiento de devolución
                movement = StockMovement(
                    stock_id=stock.id,
                    movement_type="RETURN",
                    quantity=usage.quantity,
                    repair_id=usage.repair_id,
                    notes=f"Devolución de reparación #{repair.repair_number}",
                    performed_by=user_id
                )
                self.db.add(movement)

            # Eliminar uso
            self.db.delete(usage)

            # Recalcular parts_cost
            self._recalculate_parts_cost(repair)

            self.db.commit()
            return {"message": "Componente devuelto", "usage_id": usage_id}

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(e)}"
            )

    def _recalculate_parts_cost(self, repair: Repair) -> None:
        """Recalcula parts_cost sumando todos los componentes usados"""
        total = 0.0
        for usage in repair.component_usages:
            if usage.unit_cost:
                total += usage.quantity * usage.unit_cost
        repair.parts_cost = total
        repair.total_cost = (repair.parts_cost or 0) + (repair.labor_cost or 0) + (repair.additional_cost or 0) - (repair.discount or 0)

    def update_labor_cost(self, repair_id: int, labor_cost: float) -> Repair:
        """Actualiza costo de mano de obra y recalcula total"""
        repair = self.get_repair(repair_id)

        if self.is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar reparación cerrada"
            )

        repair.labor_cost = labor_cost
        repair.total_cost = (repair.parts_cost or 0) + (repair.labor_cost or 0) + (repair.additional_cost or 0) - (repair.discount or 0)
        self.db.commit()
        self.db.refresh(repair)
        return repair

    def close_repair(self, repair_id: int, user_id: int) -> Repair:
        """
        Cierra reparación (marca como entregada).
        Una vez cerrada, no se puede modificar.
        """
        repair = self.get_repair(repair_id)

        if self.is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reparación ya está cerrada"
            )

        # Buscar status "delivered"
        delivered_status = self.db.query(RepairStatus).filter(
            RepairStatus.code == "delivered"
        ).first()

        if delivered_status:
            repair.status_id = delivered_status.id
        else:
            repair.status_id = 4  # fallback

        repair.delivery_date = datetime.utcnow()
        repair.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(repair)
        return repair

    def get_component_usages(self, repair_id: int) -> List[RepairComponentUsage]:
        """Obtiene lista de componentes usados en reparación"""
        self.get_repair(repair_id)  # Valida que existe
        return self.db.query(RepairComponentUsage).filter(
            RepairComponentUsage.repair_id == repair_id
        ).all()

    def get_repair_economic_summary(self, repair_id: int) -> dict:
        """Retorna resumen económico de la reparación"""
        repair = self.get_repair(repair_id)
        return {
            "repair_id": repair.id,
            "repair_number": repair.repair_number,
            "parts_cost": repair.parts_cost or 0,
            "labor_cost": repair.labor_cost or 0,
            "additional_cost": repair.additional_cost or 0,
            "discount": repair.discount or 0,
            "total_cost": repair.total_cost or 0,
            "paid_amount": repair.paid_amount or 0,
            "payment_status": repair.payment_status,
            "is_closed": self.is_repair_closed(repair),
            "component_count": len(repair.component_usages)
        }

    def update_status(
        self,
        repair_id: int,
        new_status_id: int,
        user_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Repair:
        """
        Actualiza el estado de una reparación con validación de transición.
        TRANSACCIÓN ATÓMICA:
        1. Valida transición de estado (state machine)
        2. Actualiza timestamps según el nuevo estado
        3. Crea audit log
        4. Emite evento para notificaciones

        Args:
            repair_id: ID de la reparación
            new_status_id: ID del nuevo estado
            user_id: ID del usuario que realiza el cambio
            notes: Notas opcionales sobre el cambio

        Returns:
            Repair actualizado

        Raises:
            HTTPException: Si la transición no es válida
        """
        repair = self.get_repair(repair_id)
        current_status_id = repair.status_id

        # Si es el mismo estado, no hacer nada
        if current_status_id == new_status_id:
            return repair

        # Validar transición (lanza HTTPException si es inválida)
        validate_transition(current_status_id, new_status_id)

        # Actualizar timestamps según el nuevo estado
        now = datetime.utcnow()

        note_to_add = None
        if new_status_id == RepairStateID.APROBADO:
            repair.approval_date = now
        elif new_status_id == RepairStateID.EN_TRABAJO:
            if not repair.start_date:  # Solo si es primera vez
                repair.start_date = now
        elif new_status_id == RepairStateID.LISTO:
            repair.completion_date = now
        elif new_status_id == RepairStateID.ENTREGADO:
            repair.delivery_date = now
            # Al entregar, pasa a noventena automáticamente
            new_status_id = RepairStateID.NOVENTENA
            repair.warranty_until = (now + timedelta(days=repair.warranty_days or 90)).date()
        elif new_status_id == RepairStateID.NOVENTENA:
            repair.warranty_until = (now + timedelta(days=repair.warranty_days or 90)).date()
        elif new_status_id == RepairStateID.RECHAZADO:
            repair.archived_at = now
            repair.archived_by = user_id
            note_to_add = "RECHAZADO"
        elif new_status_id == RepairStateID.ARCHIVADO:
            repair.archived_at = now
            repair.archived_by = user_id

        # Actualizar estado
        previous_status_id = repair.status_id
        repair.status_id = new_status_id
        repair.updated_at = now

        try:
            if note_to_add:
                self.db.add(RepairNote(
                    repair_id=repair.id,
                    user_id=user_id or 1,
                    note=note_to_add if not notes else f"{note_to_add}: {notes}",
                    note_type="internal"
                ))
            self.db.commit()
            self.db.refresh(repair)

            # Crear audit log
            try:
                create_audit(
                    event_type="repair.status.change",
                    user_id=user_id,
                    details={
                        "repair_id": repair.id,
                        "repair_number": repair.repair_number,
                        "from_status_id": previous_status_id,
                        "to_status_id": new_status_id,
                        "from_status": get_state_name(previous_status_id),
                        "to_status": get_state_name(new_status_id),
                        "notes": notes
                    },
                    message=f"Estado cambiado: {get_state_name(previous_status_id)} → {get_state_name(new_status_id)}"
                )
            except Exception:
                pass  # Auditoría no debe romper el flujo principal

            # Emitir evento para notificaciones
            self._emit_status_change_event(repair, new_status_id, notes)

            return repair

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(e)}"
            )

    def _emit_status_change_event(
        self,
        repair: Repair,
        new_status_id: int,
        notes: Optional[str] = None
    ) -> None:
        """
        Emite eventos según el cambio de estado para activar notificaciones.
        """
        try:
            # Obtener datos del cliente a través del dispositivo
            client_email = None
            client_name = None
            instrument_name = None

            if hasattr(repair, 'device') and repair.device:
                device = repair.device
                if hasattr(device, 'client') and device.client:
                    client = device.client
                    client_email = client.email
                    client_name = client.name
                if hasattr(device, 'model'):
                    instrument_name = device.model

            # Solo emitir si tenemos email del cliente
            if client_email:
                # Evento genérico de cambio de estado
                event_bus.emit(Events.REPAIR_STATUS_CHANGED, {
                    'customer_email': client_email,
                    'customer_name': client_name or 'Cliente',
                    'repair_id': repair.repair_number,
                    'status': get_state_name(new_status_id),
                    'progress': get_state_progress(new_status_id),
                    'notes': notes
                })

                # Evento específico de completado (listo para recoger)
                if new_status_id == RepairStateID.LISTO:
                    event_bus.emit(Events.REPAIR_COMPLETED, {
                        'customer_email': client_email,
                        'customer_name': client_name or 'Cliente',
                        'repair_id': repair.repair_number,
                        'instrument': instrument_name or 'Dispositivo',
                        'total_cost': repair.total_cost or 0
                    })

        except Exception as e:
            # Log error pero no romper el flujo principal
            import logging
            logging.getLogger(__name__).error(f"Error emitiendo evento: {str(e)}")
