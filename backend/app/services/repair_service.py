"""
Servicio transaccional para dominio Repair
Maneja: ComponentUsage → Stock → StockMovement → Costos
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, List

from app.models.repair import Repair, RepairStatus
from app.models.repair_component_usage import RepairComponentUsage
from app.models.repair_photo import RepairPhoto
from app.models.repair_note import RepairNote
from app.models.stock import Stock
from app.models.stock_movement import StockMovement


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
            return repair.status_obj.code in ('delivered', 'cancelled')
        return repair.status_id in (4, 5)  # delivered=4, cancelled=5

    def add_component_usage(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: int,
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
        available = stock.quantity - (stock.quantity_reserved or 0)
        if available < quantity:
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
            stock.quantity -= quantity
            stock.updated_at = datetime.utcnow()

            # 3. Registrar movimiento de stock
            movement = StockMovement(
                stock_id=stock.id,
                movement_type="OUT",
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

    def remove_component_usage(
        self,
        usage_id: int,
        user_id: int
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
