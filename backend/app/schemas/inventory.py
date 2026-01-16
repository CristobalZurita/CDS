from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemSummary(BaseModel):
	id: int
	sku: Optional[str]
	name: str
	category: str
	stock: int = 0

	class Config:
		orm_mode = True


class ProductCreate(BaseModel):
	"""Schema para crear producto"""
	category_id: int
	name: str = Field(..., min_length=1, max_length=255)
	sku: str = Field(..., min_length=1, max_length=100)
	description: Optional[str] = None
	price: int = Field(..., ge=0)
	quantity: int = Field(default=0, ge=0)
	min_quantity: int = Field(default=5, ge=0)


class ProductUpdate(BaseModel):
	"""Schema para actualizar producto"""
	category_id: Optional[int] = None
	name: Optional[str] = Field(None, min_length=1, max_length=255)
	sku: Optional[str] = Field(None, min_length=1, max_length=100)
	description: Optional[str] = None
	price: Optional[int] = Field(None, ge=0)
	quantity: Optional[int] = Field(None, ge=0)
	min_quantity: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
	"""Schema de respuesta de producto"""
	id: int
	category_id: int
	name: str
	sku: str
	description: Optional[str]
	price: int
	quantity: int
	min_quantity: int
	is_low_stock: bool
	created_at: datetime
	updated_at: datetime

	class Config:
		orm_mode = True
