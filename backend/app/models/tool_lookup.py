"""
Modelos lookup para herramientas
Alineado con schema real de cirujano.db
"""
from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class ToolCategory(Base):
    __tablename__ = "tool_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)


class ToolBrand(Base):
    __tablename__ = "tool_brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    quality_tier = Column(String, nullable=True)
