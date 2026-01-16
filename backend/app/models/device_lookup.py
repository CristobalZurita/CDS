"""
Modelos de lookup para Device
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from app.core.database import Base


class DeviceBrand(Base):
    """Marcas de dispositivos"""
    __tablename__ = "device_brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    country = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)


class DeviceType(Base):
    """Tipos de dispositivos"""
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
