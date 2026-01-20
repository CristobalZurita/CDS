"""
Modelo Invoice para facturación
===============================
Sistema de facturas con items, pagos y estados.
ADITIVO: Nueva tabla, no modifica existentes.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum
from app.core.database import Base


class InvoiceStatus(str, Enum):
    """Estados posibles de una factura"""
    DRAFT = "draft"              # Borrador, editable
    SENT = "sent"                # Enviada al cliente
    VIEWED = "viewed"            # Vista por el cliente
    PAID = "paid"                # Pagada completamente
    PARTIAL = "partial"          # Pago parcial
    OVERDUE = "overdue"          # Vencida
    VOID = "void"                # Anulada
    REFUNDED = "refunded"        # Reembolsada


class InvoiceType(str, Enum):
    """Tipos de documento"""
    INVOICE = "invoice"          # Factura normal
    QUOTE = "quote"              # Cotización (sin valor fiscal)
    CREDIT_NOTE = "credit_note"  # Nota de crédito
    RECEIPT = "receipt"          # Recibo simple


class Invoice(Base):
    """
    Factura o documento de cobro.

    Campos:
    - invoice_number: Número único secuencial (ej: F-2024-00001)
    - repair_id: Referencia opcional a reparación
    - client_id: Cliente asociado
    - Totales calculados a partir de items
    """
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    # Identificación
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_type = Column(String(20), default=InvoiceType.INVOICE.value, nullable=False)

    # Referencias
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)

    # Estado
    status = Column(String(20), default=InvoiceStatus.DRAFT.value, nullable=False, index=True)

    # Fechas
    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=True)  # Fecha de vencimiento
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    voided_at = Column(DateTime, nullable=True)

    # Montos (en centavos para precisión)
    subtotal = Column(Integer, default=0, nullable=False)  # Sin IVA
    tax_rate = Column(Float, default=19.0)  # IVA Chile 19%
    tax_amount = Column(Integer, default=0, nullable=False)
    discount_amount = Column(Integer, default=0)
    discount_percent = Column(Float, default=0.0)
    total = Column(Integer, default=0, nullable=False)  # Total con IVA

    # Pagos
    amount_paid = Column(Integer, default=0)  # Monto ya pagado
    amount_due = Column(Integer, default=0)   # Monto pendiente

    # Información adicional
    notes = Column(Text, nullable=True)  # Notas para el cliente
    internal_notes = Column(Text, nullable=True)  # Notas internas
    terms = Column(Text, nullable=True)  # Términos y condiciones
    footer = Column(Text, nullable=True)  # Pie de página

    # Información del cliente (snapshot al momento de emisión)
    client_name = Column(String(255), nullable=True)
    client_email = Column(String(255), nullable=True)
    client_phone = Column(String(50), nullable=True)
    client_address = Column(Text, nullable=True)
    client_tax_id = Column(String(50), nullable=True)  # RUT en Chile

    # Auditoría
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    voided_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    void_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice")
    client = relationship("Client", back_populates="invoices")
    repair = relationship("Repair", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice({self.invoice_number}, status={self.status}, total={self.total})>"

    @property
    def is_overdue(self) -> bool:
        """Verifica si la factura está vencida"""
        if self.status in [InvoiceStatus.PAID.value, InvoiceStatus.VOID.value]:
            return False
        if self.due_date and datetime.utcnow() > self.due_date:
            return True
        return False

    @property
    def is_fully_paid(self) -> bool:
        """Verifica si está completamente pagada"""
        return self.amount_paid >= self.total

    def calculate_totals(self):
        """Recalcula totales basado en items"""
        self.subtotal = sum(item.subtotal for item in self.items)

        # Aplicar descuento
        if self.discount_percent > 0:
            self.discount_amount = int(self.subtotal * (self.discount_percent / 100))
        subtotal_after_discount = self.subtotal - self.discount_amount

        # Calcular IVA
        self.tax_amount = int(subtotal_after_discount * (self.tax_rate / 100))
        self.total = subtotal_after_discount + self.tax_amount
        self.amount_due = self.total - self.amount_paid

    @staticmethod
    def generate_invoice_number(db_session, prefix: str = "F") -> str:
        """Genera número de factura secuencial"""
        year = datetime.utcnow().year
        # Buscar último número del año
        last = db_session.query(Invoice).filter(
            Invoice.invoice_number.like(f"{prefix}-{year}-%")
        ).order_by(Invoice.id.desc()).first()

        if last:
            try:
                last_num = int(last.invoice_number.split("-")[-1])
                next_num = last_num + 1
            except ValueError:
                next_num = 1
        else:
            next_num = 1

        return f"{prefix}-{year}-{next_num:05d}"


class InvoiceItem(Base):
    """
    Línea de detalle de factura.

    Puede representar:
    - Mano de obra
    - Materiales/repuestos
    - Servicios adicionales
    - Descuentos (cantidad negativa)
    """
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)

    # Descripción
    description = Column(String(500), nullable=False)
    item_type = Column(String(50), default="service")  # service, part, labor, discount

    # Referencia opcional a producto/componente
    product_id = Column(Integer, nullable=True)  # FK implícito a products
    component_table = Column(String(50), nullable=True)  # Para sistema polimórfico
    component_id = Column(Integer, nullable=True)

    # Cantidades y precios (en centavos)
    quantity = Column(Float, default=1.0, nullable=False)
    unit = Column(String(20), default="u")  # u, hr, kg, etc.
    unit_price = Column(Integer, nullable=False)  # Precio unitario
    discount = Column(Integer, default=0)  # Descuento por línea
    subtotal = Column(Integer, nullable=False)  # quantity * unit_price - discount

    # Orden de aparición
    sort_order = Column(Integer, default=0)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación
    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem({self.description[:30]}, qty={self.quantity}, total={self.subtotal})>"

    def calculate_subtotal(self):
        """Calcula el subtotal de la línea"""
        self.subtotal = int(self.quantity * self.unit_price) - self.discount


class InvoiceSequence(Base):
    """
    Control de secuencias para numeración de documentos.
    Permite diferentes secuencias por tipo de documento y año.
    """
    __tablename__ = "invoice_sequences"

    id = Column(Integer, primary_key=True, index=True)
    prefix = Column(String(10), nullable=False)  # F, Q, NC, R
    year = Column(Integer, nullable=False)
    last_number = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Índice único para prefix + year
        {'sqlite_autoincrement': True},
    )
