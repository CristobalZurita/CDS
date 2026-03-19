"""
InvoiceService - fachada estable para facturación.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.invoice import Invoice, InvoiceItem, InvoiceType
from app.models.payment import Payment
from app.services.invoice_payment_service import InvoicePaymentService
from app.services.invoice_query_service import InvoiceQueryService
from app.services.invoice_write_service import InvoiceWriteService


class InvoiceService:
    """Fachada estable para el dominio de facturación."""

    def __init__(self, db: Session):
        self.db = db
        self.write_service = InvoiceWriteService(db)
        self.payment_service = InvoicePaymentService(db)
        self.query_service = InvoiceQueryService(db)

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
        return self.write_service.create_invoice(
            client_id=client_id,
            repair_id=repair_id,
            invoice_type=invoice_type,
            items=items,
            due_days=due_days,
            tax_rate=tax_rate,
            notes=notes,
            created_by=created_by,
        )

    def create_from_repair(
        self,
        repair_id: int,
        include_labor: bool = True,
        include_parts: bool = True,
        created_by: Optional[int] = None,
    ) -> Invoice:
        return self.write_service.create_from_repair(
            repair_id=repair_id,
            include_labor=include_labor,
            include_parts=include_parts,
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
        return self.write_service.add_item(
            invoice_id=invoice_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            **kwargs,
        )

    def remove_item(self, invoice_id: int, item_id: int) -> bool:
        return self.write_service.remove_item(invoice_id, item_id)

    def update_status(
        self,
        invoice_id: int,
        new_status: str,
        user_id: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Invoice:
        return self.payment_service.update_status(
            invoice_id=invoice_id,
            new_status=new_status,
            user_id=user_id,
            reason=reason,
        )

    def record_payment(
        self,
        invoice_id: int,
        amount: int,
        payment_method: str = "cash",
        transaction_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Payment:
        return self.payment_service.record_payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            user_id=user_id,
        )

    def get_invoice(self, invoice_id: int) -> Invoice:
        return self.query_service.get_invoice(invoice_id)

    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        return self.query_service.get_by_number(invoice_number)

    def list_invoices(
        self,
        client_id: Optional[int] = None,
        repair_id: Optional[int] = None,
        status: Optional[str] = None,
        invoice_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Invoice]:
        return self.query_service.list_invoices(
            client_id=client_id,
            repair_id=repair_id,
            status=status,
            invoice_type=invoice_type,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )

    def get_overdue_invoices(self) -> List[Invoice]:
        return self.payment_service.get_overdue_invoices()

    def mark_overdue(self) -> int:
        return self.payment_service.mark_overdue()

    def get_summary(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        return self.query_service.get_summary(from_date=from_date, to_date=to_date)
