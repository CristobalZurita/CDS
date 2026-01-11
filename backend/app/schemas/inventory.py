from pydantic import BaseModel
from typing import Optional


class ItemSummary(BaseModel):
	id: int
	sku: Optional[str]
	name: str
	category: str
	stock: int = 0

	class Config:
		orm_mode = True
