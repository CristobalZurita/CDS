"""
backend/app/models/order.py
Modelo Order + OrderItem.

Después de crear este archivo, correr:
    cd backend
    alembic revision --autogenerate -m "add_orders"
    alembic upgrade head
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    code       = Column(String(20), unique=True, index=True)   # CDS-20250001
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Estado: pending | paid | preparing | shipped | delivered | cancelled
    status     = Column(String(30), default="pending", nullable=False, index=True)

    # Pago: transfer | webpay | store
    payment_method  = Column(String(20), default="transfer")
    payment_status  = Column(String(20), default="pending")   # pending | confirmed | failed
    webpay_token    = Column(String(200), nullable=True)

    # Cliente
    customer_name   = Column(String(200), nullable=False)
    customer_email  = Column(String(200), nullable=False, index=True)
    customer_phone  = Column(String(30),  nullable=True)
    customer_rut    = Column(String(20),  nullable=True)

    # Envío
    shipping_address = Column(String(300), nullable=True)
    shipping_commune = Column(String(100), nullable=True)
    shipping_region  = Column(String(100), nullable=True)
    shipping_cost    = Column(Float, default=0.0)

    total     = Column(Float, nullable=False)
    notes     = Column(Text,  nullable=True)

    items     = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, code={self.code}, status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, index=True)
    order_id   = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty        = Column(Integer, nullable=False)
    unit_price = Column(Float,   nullable=False)

    order      = relationship("Order",   back_populates="items")
    product    = relationship("Product")

    @property
    def subtotal(self):
        return self.unit_price * self.qty
