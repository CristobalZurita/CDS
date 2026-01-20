"""
Modelo Client - Clientes del taller
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Client(Base):
    """Cliente del taller de reparaciones"""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    phone_alt = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    country = Column(String, default="Chile")
    preferred_contact = Column(String, default="whatsapp")
    notes = Column(Text, nullable=True)
    total_repairs = Column(Integer, default=0)
    total_spent = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # === CAMPOS ADICIONALES (ADITIVOS) ===
    # Segmentación de cliente
    customer_segment = Column(String(20), default="regular")  # vip, regular, new, inactive
    lifetime_value = Column(Float, default=0.0)  # Valor total histórico

    # Información fiscal (para B2B)
    tax_id = Column(String(50), nullable=True)  # RUT en Chile
    company_name = Column(String(255), nullable=True)
    billing_address = Column(Text, nullable=True)

    # Preferencias
    language_preference = Column(String(10), default="es")
    service_preference = Column(String(20), default="whatsapp")  # email, whatsapp, phone, sms

    # Notas internas (solo para staff)
    internal_notes = Column(Text, nullable=True)

    # Relaciones
    user = relationship("User", foreign_keys=[user_id])
    devices = relationship("Device", back_populates="client")
    quotes = relationship("Quote", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")  # ADITIVO
    warranties = relationship("Warranty", back_populates="client")  # ADITIVO

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name})>"
