"""
Modelo Quote - Cotizaciones
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class QuoteStatus:
    """Estados válidos de cotización."""
    PENDING = "pending"
    SENT = "sent"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELED = "canceled"

    ALL = {
        PENDING,
        SENT,
        APPROVED,
        DENIED,
        CANCELED,
    }


class Quote(Base):
    """Cotización de reparación"""

    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_number = Column(String, unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    problem_description = Column(Text, nullable=False)
    photos_received = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    estimated_parts_cost = Column(Float, default=0)
    estimated_labor_cost = Column(Float, default=0)
    estimated_total = Column(Float, default=0)
    status = Column(String, default=QuoteStatus.PENDING)
    valid_until = Column(Date, nullable=True)
    client_response = Column(Text, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relaciones
    client = relationship("Client", back_populates="quotes")
    creator = relationship("User", foreign_keys=[created_by])
    repairs = relationship("Repair", backref="quote")
    items = relationship(
        "QuoteItem",
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteItem.sort_order",
    )
    recipients = relationship(
        "QuoteRecipient",
        back_populates="quote",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Quote(id={self.id}, number={self.quote_number}, status={self.status})>"


class QuoteItem(Base):
    """Línea de detalle de cotización."""

    __tablename__ = "quote_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False, index=True)
    item_type = Column(String(32), default="service", nullable=False)
    sku = Column(String(120), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Float, default=1.0, nullable=False)
    unit_price = Column(Float, default=0.0, nullable=False)
    line_total = Column(Float, default=0.0, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    source_table = Column(String(64), nullable=True)
    source_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quote = relationship("Quote", back_populates="items")

    def recalculate_line_total(self) -> float:
        self.line_total = float(self.quantity or 0) * float(self.unit_price or 0)
        return self.line_total

    def __repr__(self):
        return f"<QuoteItem(id={self.id}, quote_id={self.quote_id}, name={self.name})>"


class QuoteRecipient(Base):
    """Destinatario de cotización para envío."""

    __tablename__ = "quote_recipients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    quote = relationship("Quote", back_populates="recipients")

    def __repr__(self):
        return f"<QuoteRecipient(id={self.id}, quote_id={self.quote_id}, email={self.email})>"
