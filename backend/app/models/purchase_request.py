"""
PurchaseRequest models for internal cart/suggestions.
ADITIVO: new tables.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    repair_id = Column(Integer, ForeignKey("repairs.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(20), default="draft")  # draft | suggested | approved | purchased | received | cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client")
    repair = relationship("Repair")
    creator = relationship("User", foreign_keys=[created_by])
    items = relationship("PurchaseRequestItem", back_populates="request", cascade="all, delete-orphan")


class PurchaseRequestItem(Base):
    __tablename__ = "purchase_request_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("purchase_requests.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    sku = Column(String(120), nullable=True)
    name = Column(String(255), nullable=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    external_url = Column(String(500), nullable=True)
    status = Column(String(20), default="suggested")  # suggested | approved | purchased | received

    request = relationship("PurchaseRequest", back_populates="items")
