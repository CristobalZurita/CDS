from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.repair import Repair
from app.models.repair_component_usage import RepairComponentUsage
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.services.repair_service_support import (
    get_repair_or_404,
    is_repair_closed,
    recalculate_parts_cost,
)


class RepairComponentStockService:
    def __init__(self, db: Session):
        self.db = db

    def _get_stock_or_404(self, component_table: str, component_id: int) -> Stock:
        stock = (
            self.db.query(Stock)
            .filter(
                Stock.component_table == component_table,
                Stock.component_id == component_id,
            )
            .first()
        )
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock no encontrado para {component_table}.{component_id}",
            )
        return stock

    def _ensure_open_repair(self, repair_id: int) -> Repair:
        repair = get_repair_or_404(self.db, repair_id)
        if is_repair_closed(repair):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar reparación cerrada",
            )
        return repair

    def add_component_usage(
        self,
        repair_id: int,
        component_table: str,
        component_id: int,
        quantity: int,
        user_id: Optional[int],
        from_reserved: bool = False,
        notes: Optional[str] = None,
    ) -> RepairComponentUsage:
        repair = self._ensure_open_repair(repair_id)
        stock = self._get_stock_or_404(component_table, component_id)

        available = stock.available_quantity
        if from_reserved:
            reserved_qty = stock.quantity_reserved or 0
            if reserved_qty < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Reserva insuficiente. Reservado: {reserved_qty}, Requerido: {quantity}",
                )
        elif available < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {available}, Requerido: {quantity}",
            )

        try:
            usage = RepairComponentUsage(
                repair_id=repair_id,
                component_table=component_table,
                component_id=component_id,
                quantity=quantity,
                unit_cost=stock.unit_cost,
                notes=notes,
            )
            self.db.add(usage)

            if from_reserved:
                stock.quantity_reserved = max((stock.quantity_reserved or 0) - quantity, 0)
            stock.quantity -= quantity
            stock.updated_at = datetime.utcnow()

            self.db.add(
                StockMovement(
                    stock_id=stock.id,
                    movement_type="OUT_RESERVED" if from_reserved else "OUT",
                    quantity=quantity,
                    repair_id=repair_id,
                    notes=f"Uso en reparación #{repair.repair_number}",
                    performed_by=user_id,
                )
            )

            recalculate_parts_cost(repair)

            self.db.commit()
            self.db.refresh(usage)
            return usage
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(exc)}",
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
        repair = self._ensure_open_repair(repair_id)
        stock = self._get_stock_or_404(component_table, component_id)

        available = stock.available_quantity
        if available < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para reservar. Disponible: {available}, Requerido: {quantity}",
            )

        try:
            stock.quantity_reserved = (stock.quantity_reserved or 0) + quantity
            stock.updated_at = datetime.utcnow()
            self.db.add(
                StockMovement(
                    stock_id=stock.id,
                    movement_type="RESERVE",
                    quantity=quantity,
                    repair_id=repair_id,
                    notes=notes or f"Reserva para reparación #{repair.repair_number}",
                    performed_by=user_id,
                )
            )
            self.db.commit()
            self.db.refresh(stock)
            return {
                "stock_id": stock.id,
                "reserved_quantity": quantity,
                "total_reserved": stock.quantity_reserved or 0,
                "available_quantity": stock.available_quantity,
            }
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(exc)}",
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
        repair = self._ensure_open_repair(repair_id)
        stock = self._get_stock_or_404(component_table, component_id)

        current_reserved = stock.quantity_reserved or 0
        if current_reserved <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay reserva para liberar",
            )

        release_qty = min(quantity, current_reserved)

        try:
            stock.quantity_reserved = current_reserved - release_qty
            stock.updated_at = datetime.utcnow()
            self.db.add(
                StockMovement(
                    stock_id=stock.id,
                    movement_type="UNRESERVE",
                    quantity=release_qty,
                    repair_id=repair_id,
                    notes=notes or f"Liberación de reserva reparación #{repair.repair_number}",
                    performed_by=user_id,
                )
            )
            self.db.commit()
            self.db.refresh(stock)
            return {
                "stock_id": stock.id,
                "released_quantity": release_qty,
                "total_reserved": stock.quantity_reserved or 0,
                "available_quantity": stock.available_quantity,
            }
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(exc)}",
            )

    def remove_component_usage(
        self,
        usage_id: int,
        user_id: Optional[int],
    ) -> dict:
        usage = (
            self.db.query(RepairComponentUsage)
            .filter(RepairComponentUsage.id == usage_id)
            .first()
        )
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Uso de componente {usage_id} no encontrado",
            )

        repair = self._ensure_open_repair(usage.repair_id)
        stock = (
            self.db.query(Stock)
            .filter(
                Stock.component_table == usage.component_table,
                Stock.component_id == usage.component_id,
            )
            .first()
        )

        try:
            if stock:
                stock.quantity += usage.quantity
                stock.updated_at = datetime.utcnow()
                self.db.add(
                    StockMovement(
                        stock_id=stock.id,
                        movement_type="RETURN",
                        quantity=usage.quantity,
                        repair_id=usage.repair_id,
                        notes=f"Devolución de reparación #{repair.repair_number}",
                        performed_by=user_id,
                    )
                )

            self.db.delete(usage)
            recalculate_parts_cost(repair)

            self.db.commit()
            return {"message": "Componente devuelto", "usage_id": usage_id}
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de integridad: {str(exc)}",
            )

    def update_labor_cost(self, repair_id: int, labor_cost: float) -> Repair:
        repair = self._ensure_open_repair(repair_id)
        repair.labor_cost = labor_cost
        repair.total_cost = (
            (repair.parts_cost or 0)
            + (repair.labor_cost or 0)
            + (repair.additional_cost or 0)
            - (repair.discount or 0)
        )
        self.db.commit()
        self.db.refresh(repair)
        return repair

    def get_component_usages(self, repair_id: int) -> List[RepairComponentUsage]:
        get_repair_or_404(self.db, repair_id)
        return (
            self.db.query(RepairComponentUsage)
            .filter(RepairComponentUsage.repair_id == repair_id)
            .all()
        )

    def get_repair_economic_summary(self, repair_id: int) -> dict:
        repair = get_repair_or_404(self.db, repair_id)
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
            "is_closed": is_repair_closed(repair),
            "component_count": len(repair.component_usages),
        }
