from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, InvoiceType
from app.services.invoice_support import (
    generate_invoice_number,
    get_invoice_or_404,
    get_repair_or_404,
    resolve_client_snapshot,
    resolve_invoice_prefix,
)


class InvoiceWriteService:
    def __init__(self, db: Session):
        self.db = db

    def create_invoice(
        self,
        client_id: Optional[int] = None,
        repair_id: Optional[int] = None,
        invoice_type: str = InvoiceType.INVOICE.value,
        items: Optional[List[Dict[str, Any]]] = None,
        due_days: int = 30,
        tax_rate: float = 19.0,
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> Invoice:
        invoice_number = generate_invoice_number(self.db, resolve_invoice_prefix(invoice_type))
        client_snapshot = resolve_client_snapshot(self.db, client_id)

        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_type=invoice_type,
            client_id=client_id,
            repair_id=repair_id,
            status=InvoiceStatus.DRAFT.value,
            issue_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=due_days),
            tax_rate=tax_rate,
            notes=notes,
            created_by=created_by,
            **client_snapshot,
        )

        self.db.add(invoice)
        self.db.flush()

        for idx, item_data in enumerate(items or []):
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data.get("description", ""),
                item_type=item_data.get("item_type", "service"),
                quantity=item_data.get("quantity", 1),
                unit=item_data.get("unit", "u"),
                unit_price=item_data.get("unit_price", 0),
                discount=item_data.get("discount", 0),
                product_id=item_data.get("product_id"),
                component_table=item_data.get("component_table"),
                component_id=item_data.get("component_id"),
                sort_order=idx,
            )
            item.calculate_subtotal()
            self.db.add(item)

        self.db.flush()
        invoice.calculate_totals()
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def create_from_repair(
        self,
        repair_id: int,
        include_labor: bool = True,
        include_parts: bool = True,
        created_by: Optional[int] = None,
    ) -> Invoice:
        repair = get_repair_or_404(self.db, repair_id)
        items: List[Dict[str, Any]] = []

        if include_labor and repair.labor_cost:
            items.append(
                {
                    "description": f"Mano de obra - {repair.work_performed or 'Reparación'}",
                    "item_type": "labor",
                    "quantity": 1,
                    "unit": "servicio",
                    "unit_price": repair.labor_cost,
                }
            )

        if include_parts and repair.component_usages:
            for usage in repair.component_usages:
                items.append(
                    {
                        "description": usage.component_name or f"Componente #{usage.component_id}",
                        "item_type": "part",
                        "quantity": usage.quantity,
                        "unit": "u",
                        "unit_price": usage.unit_cost or 0,
                        "component_table": usage.component_table,
                        "component_id": usage.component_id,
                    }
                )

        client_id = None
        if hasattr(repair, "instrument") and repair.instrument and hasattr(repair.instrument, "client_id"):
            client_id = repair.instrument.client_id

        return self.create_invoice(
            client_id=client_id,
            repair_id=repair_id,
            invoice_type=InvoiceType.INVOICE.value,
            items=items,
            notes=f"Factura por reparación #{repair.repair_number}",
            created_by=created_by,
        )

    def add_item(
        self,
        invoice_id: int,
        description: str,
        quantity: float = 1,
        unit_price: int = 0,
        **kwargs,
    ) -> InvoiceItem:
        invoice = get_invoice_or_404(self.db, invoice_id)
        if invoice.status != InvoiceStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden editar facturas en borrador",
            )

        max_order = (
            self.db.query(func.max(InvoiceItem.sort_order))
            .filter(InvoiceItem.invoice_id == invoice_id)
            .scalar()
            or 0
        )

        item = InvoiceItem(
            invoice_id=invoice_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            sort_order=max_order + 1,
            **kwargs,
        )
        item.calculate_subtotal()
        self.db.add(item)
        self.db.flush()
        invoice.calculate_totals()
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_item(self, invoice_id: int, item_id: int) -> bool:
        invoice = get_invoice_or_404(self.db, invoice_id)
        if invoice.status != InvoiceStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden editar facturas en borrador",
            )

        item = (
            self.db.query(InvoiceItem)
            .filter(
                InvoiceItem.id == item_id,
                InvoiceItem.invoice_id == invoice_id,
            )
            .first()
        )
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado",
            )

        self.db.delete(item)
        self.db.flush()
        invoice.calculate_totals()
        self.db.commit()
        return True
