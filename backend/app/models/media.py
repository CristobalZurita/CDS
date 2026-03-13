"""
Modelos para gestión dinámica de medios.
ADITIVO: no modifica modelos existentes.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class MediaAsset(Base):
    """
    Imagen almacenada en Cloudinary.
    Se registra en BD después de cada upload para tener fuente de verdad local.
    """
    __tablename__ = "media_assets"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(500), unique=True, nullable=False, index=True)
    secure_url = Column(String(1000), nullable=False)
    folder = Column(String(200), nullable=True)        # ej: cirujano/instrumentos
    original_filename = Column(String(300), nullable=True)
    format = Column(String(20), nullable=True)         # webp, png, jpg…
    bytes = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    bindings = relationship("MediaBinding", back_populates="asset")

    def __repr__(self):
        return f"<MediaAsset(id={self.id}, public_id={self.public_id})>"


class MediaBinding(Base):
    """
    Vincula un slot del sitio con un asset de Cloudinary.
    Ej: slot_key='home.hero.bg' → asset_id=42
    Esto permite cambiar imágenes del front sin tocar código.
    """
    __tablename__ = "media_bindings"

    id = Column(Integer, primary_key=True, index=True)
    slot_key = Column(String(200), unique=True, nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("media_assets.id"), nullable=False)
    label = Column(String(200), nullable=True)         # nombre legible para el admin
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    asset = relationship("MediaAsset", back_populates="bindings")

    def __repr__(self):
        return f"<MediaBinding(slot_key={self.slot_key}, asset_id={self.asset_id})>"
