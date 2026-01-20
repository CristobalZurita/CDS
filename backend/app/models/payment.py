"""
Modelo Payment para registrar pagos asociados a reparaciones
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True, index=True)

    amount = Column(Integer, nullable=False)  # in cents
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(255), nullable=True, index=True, unique=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # === CAMPOS ADICIONALES (ADITIVOS) ===
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    payment_date = Column(DateTime, nullable=True)  # Fecha efectiva del pago
    payment_due_date = Column(DateTime, nullable=True)  # Fecha de vencimiento
    refund_of_id = Column(Integer, ForeignKey("payments.id"), nullable=True)  # Si es reembolso
    payment_processor = Column(String(50), nullable=True)  # stripe, mercadopago, manual
    processor_fee = Column(Integer, default=0)  # Comisión del procesador en centavos
    currency = Column(String(3), default="CLP")  # Código moneda ISO
    partial_payment_of = Column(Integer, ForeignKey("payments.id"), nullable=True)  # Pago parcial

    # Relaciones
    user = relationship("User")
    repair = relationship("Repair")
    invoice = relationship("Invoice", back_populates="payments")  # ADITIVO
    refund_of = relationship("Payment", remote_side=[id], foreign_keys=[refund_of_id])

    def __repr__(self):
        return f"<Payment(id={self.id}, repair_id={self.repair_id}, amount={self.amount})>"
