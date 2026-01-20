"""
InvoiceService - Servicio de Facturación
========================================
Gestiona creación, cálculo y estados de facturas.
ADITIVO: Nuevo servicio, no modifica existentes.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, InvoiceType, InvoiceSequence
from app.models.repair import Repair
from app.models.client import Client
from app.models.payment import Payment


class InvoiceService:
    """Servicio para gestión de facturas"""

    def __init__(self, db: Session):
        self.db = db

    def create_invoice(
        self,
        client_id: Optional[int] = None,
        repair_id: Optional[int] = None,
        invoice_type: str = InvoiceType.INVOICE.value,
        items: List[Dict[str, Any]] = None,
        due_days: int = 30,
        tax_rate: float = 19.0,
        notes: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Invoice:
        """
        Crea una nueva factura.

        Args:
            client_id: ID del cliente
            repair_id: ID de reparación asociada
            invoice_type: Tipo de documento
            items: Lista de items [{description, quantity, unit_price, ...}]
            due_days: Días para vencimiento
            tax_rate: Tasa de IVA
            notes: Notas para el cliente
            created_by: ID del usuario que crea

        Returns:
            Invoice creada
        """
        # Generar número de factura
        prefix_map = {
            InvoiceType.INVOICE.value: "F",
            InvoiceType.QUOTE.value: "Q",
            InvoiceType.CREDIT_NOTE.value: "NC",
            InvoiceType.RECEIPT.value: "R"
        }
        prefix = prefix_map.get(invoice_type, "F")
        invoice_number = self._generate_number(prefix)

        # Obtener datos del cliente si existe
        client_name = client_email = client_phone = client_address = client_tax_id = None
        if client_id:
            client = self.db.query(Client).filter(Client.id == client_id).first()
            if client:
                client_name = client.name
                client_email = client.email
                client_phone = client.phone
                client_address = client.address
                client_tax_id = getattr(client, 'tax_id', None)

        # Crear factura
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
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            client_address=client_address,
            client_tax_id=client_tax_id
        )

        self.db.add(invoice)
        self.db.flush()  # Para obtener el ID

        # Agregar items
        if items:
            for idx, item_data in enumerate(items):
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
                    sort_order=idx
                )
                item.calculate_subtotal()
                self.db.add(item)

        self.db.flush()

        # Calcular totales
        invoice.calculate_totals()
        self.db.commit()
        self.db.refresh(invoice)

        return invoice

    def create_from_repair(
        self,
        repair_id: int,
        include_labor: bool = True,
        include_parts: bool = True,
        created_by: Optional[int] = None
    ) -> Invoice:
        """
        Crea factura a partir de una reparación.

        Args:
            repair_id: ID de la reparación
            include_labor: Incluir mano de obra
            include_parts: Incluir repuestos
            created_by: Usuario que crea

        Returns:
            Invoice creada
        """
        repair = self.db.query(Repair).filter(Repair.id == repair_id).first()
        if not repair:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reparación {repair_id} no encontrada"
            )

        items = []

        # Agregar mano de obra
        if include_labor and repair.labor_cost:
            items.append({
                "description": f"Mano de obra - {repair.work_performed or 'Reparación'}",
                "item_type": "labor",
                "quantity": 1,
                "unit": "servicio",
                "unit_price": repair.labor_cost
            })

        # Agregar repuestos/componentes
        if include_parts and repair.component_usages:
            for usage in repair.component_usages:
                items.append({
                    "description": usage.component_name or f"Componente #{usage.component_id}",
                    "item_type": "part",
                    "quantity": usage.quantity,
                    "unit": "u",
                    "unit_price": usage.unit_cost or 0,
                    "component_table": usage.component_table,
                    "component_id": usage.component_id
                })

        # Obtener client_id desde repair si tiene instrument con client
        client_id = None
        if hasattr(repair, 'instrument') and repair.instrument:
            if hasattr(repair.instrument, 'client_id'):
                client_id = repair.instrument.client_id

        return self.create_invoice(
            client_id=client_id,
            repair_id=repair_id,
            invoice_type=InvoiceType.INVOICE.value,
            items=items,
            notes=f"Factura por reparación #{repair.repair_number}",
            created_by=created_by
        )

    def add_item(
        self,
        invoice_id: int,
        description: str,
        quantity: float = 1,
        unit_price: int = 0,
        **kwargs
    ) -> InvoiceItem:
        """Agrega un item a una factura existente"""
        invoice = self.get_invoice(invoice_id)

        if invoice.status != InvoiceStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden editar facturas en borrador"
            )

        # Obtener orden máximo
        max_order = self.db.query(func.max(InvoiceItem.sort_order)).filter(
            InvoiceItem.invoice_id == invoice_id
        ).scalar() or 0

        item = InvoiceItem(
            invoice_id=invoice_id,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            sort_order=max_order + 1,
            **kwargs
        )
        item.calculate_subtotal()

        self.db.add(item)

        # Recalcular totales
        self.db.flush()
        invoice.calculate_totals()

        self.db.commit()
        self.db.refresh(item)

        return item

    def remove_item(self, invoice_id: int, item_id: int) -> bool:
        """Elimina un item de una factura"""
        invoice = self.get_invoice(invoice_id)

        if invoice.status != InvoiceStatus.DRAFT.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden editar facturas en borrador"
            )

        item = self.db.query(InvoiceItem).filter(
            InvoiceItem.id == item_id,
            InvoiceItem.invoice_id == invoice_id
        ).first()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )

        self.db.delete(item)

        # Recalcular totales
        self.db.flush()
        invoice.calculate_totals()

        self.db.commit()
        return True

    def update_status(
        self,
        invoice_id: int,
        new_status: str,
        user_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> Invoice:
        """
        Actualiza el estado de una factura.

        Transiciones válidas:
        - draft -> sent, void
        - sent -> viewed, paid, partial, overdue, void
        - viewed -> paid, partial, overdue, void
        - partial -> paid, void
        - overdue -> paid, partial, void
        """
        invoice = self.get_invoice(invoice_id)
        current = invoice.status

        # Validar transición
        valid_transitions = {
            InvoiceStatus.DRAFT.value: [InvoiceStatus.SENT.value, InvoiceStatus.VOID.value],
            InvoiceStatus.SENT.value: [InvoiceStatus.VIEWED.value, InvoiceStatus.PAID.value,
                                        InvoiceStatus.PARTIAL.value, InvoiceStatus.OVERDUE.value,
                                        InvoiceStatus.VOID.value],
            InvoiceStatus.VIEWED.value: [InvoiceStatus.PAID.value, InvoiceStatus.PARTIAL.value,
                                          InvoiceStatus.OVERDUE.value, InvoiceStatus.VOID.value],
            InvoiceStatus.PARTIAL.value: [InvoiceStatus.PAID.value, InvoiceStatus.VOID.value],
            InvoiceStatus.OVERDUE.value: [InvoiceStatus.PAID.value, InvoiceStatus.PARTIAL.value,
                                           InvoiceStatus.VOID.value]
        }

        if current not in valid_transitions or new_status not in valid_transitions.get(current, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transición no válida: {current} -> {new_status}"
            )

        # Actualizar estado y timestamps
        invoice.status = new_status

        if new_status == InvoiceStatus.SENT.value:
            invoice.sent_at = datetime.utcnow()
        elif new_status == InvoiceStatus.VIEWED.value:
            invoice.viewed_at = datetime.utcnow()
        elif new_status == InvoiceStatus.PAID.value:
            invoice.paid_at = datetime.utcnow()
            invoice.amount_due = 0
        elif new_status == InvoiceStatus.VOID.value:
            invoice.voided_at = datetime.utcnow()
            invoice.voided_by = user_id
            invoice.void_reason = reason

        self.db.commit()
        self.db.refresh(invoice)

        return invoice

    def record_payment(
        self,
        invoice_id: int,
        amount: int,
        payment_method: str = "cash",
        transaction_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Payment:
        """
        Registra un pago para una factura.

        Args:
            invoice_id: ID de la factura
            amount: Monto en centavos
            payment_method: Método de pago
            transaction_id: ID de transacción externa
            user_id: Usuario que registra

        Returns:
            Payment creado
        """
        invoice = self.get_invoice(invoice_id)

        if invoice.status == InvoiceStatus.VOID.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede pagar una factura anulada"
            )

        if invoice.status == InvoiceStatus.PAID.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La factura ya está pagada"
            )

        # Crear pago
        from app.models.payment import PaymentStatus

        payment = Payment(
            invoice_id=invoice_id,
            repair_id=invoice.repair_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status=PaymentStatus.SUCCESS,
            payment_date=datetime.utcnow()
        )

        self.db.add(payment)

        # Actualizar montos de factura
        invoice.amount_paid += amount
        invoice.amount_due = max(0, invoice.total - invoice.amount_paid)

        # Actualizar estado
        if invoice.amount_paid >= invoice.total:
            invoice.status = InvoiceStatus.PAID.value
            invoice.paid_at = datetime.utcnow()
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.PARTIAL.value

        self.db.commit()
        self.db.refresh(payment)

        return payment

    def get_invoice(self, invoice_id: int) -> Invoice:
        """Obtiene una factura por ID"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Factura {invoice_id} no encontrada"
            )
        return invoice

    def get_by_number(self, invoice_number: str) -> Optional[Invoice]:
        """Obtiene factura por número"""
        return self.db.query(Invoice).filter(
            Invoice.invoice_number == invoice_number
        ).first()

    def list_invoices(
        self,
        client_id: Optional[int] = None,
        repair_id: Optional[int] = None,
        status: Optional[str] = None,
        invoice_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Invoice]:
        """Lista facturas con filtros opcionales"""
        query = self.db.query(Invoice)

        if client_id:
            query = query.filter(Invoice.client_id == client_id)
        if repair_id:
            query = query.filter(Invoice.repair_id == repair_id)
        if status:
            query = query.filter(Invoice.status == status)
        if invoice_type:
            query = query.filter(Invoice.invoice_type == invoice_type)
        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        return query.order_by(Invoice.issue_date.desc()).offset(offset).limit(limit).all()

    def get_overdue_invoices(self) -> List[Invoice]:
        """Obtiene facturas vencidas"""
        now = datetime.utcnow()
        return self.db.query(Invoice).filter(
            Invoice.status.in_([InvoiceStatus.SENT.value, InvoiceStatus.VIEWED.value,
                                InvoiceStatus.PARTIAL.value]),
            Invoice.due_date < now
        ).all()

    def mark_overdue(self) -> int:
        """Marca como vencidas las facturas pasadas de fecha"""
        overdue = self.get_overdue_invoices()
        count = 0
        for invoice in overdue:
            if invoice.status != InvoiceStatus.OVERDUE.value:
                invoice.status = InvoiceStatus.OVERDUE.value
                count += 1
        self.db.commit()
        return count

    def get_summary(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtiene resumen de facturación"""
        query = self.db.query(Invoice)

        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)

        invoices = query.all()

        total_invoiced = sum(i.total for i in invoices if i.status != InvoiceStatus.VOID.value)
        total_paid = sum(i.amount_paid for i in invoices)
        total_pending = sum(i.amount_due for i in invoices if i.status not in
                           [InvoiceStatus.VOID.value, InvoiceStatus.PAID.value])

        by_status = {}
        for inv in invoices:
            by_status[inv.status] = by_status.get(inv.status, 0) + 1

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "count": len(invoices),
            "by_status": by_status
        }

    def _generate_number(self, prefix: str) -> str:
        """Genera número secuencial para factura"""
        year = datetime.utcnow().year

        # Buscar o crear secuencia
        seq = self.db.query(InvoiceSequence).filter(
            InvoiceSequence.prefix == prefix,
            InvoiceSequence.year == year
        ).with_for_update().first()

        if seq:
            seq.last_number += 1
            next_num = seq.last_number
        else:
            # Crear nueva secuencia
            seq = InvoiceSequence(prefix=prefix, year=year, last_number=1)
            self.db.add(seq)
            next_num = 1

        self.db.flush()

        return f"{prefix}-{year}-{next_num:05d}"
