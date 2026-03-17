from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.inventory import ItemSummary, ProductCreate, ProductUpdate, ProductResponse
from app.models.inventory import Product
from app.models.category import Category
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.inventory_product_service import (
	get_product_or_404,
	create_product_record,
	update_product_record,
	delete_product_record,
)

router = APIRouter(prefix="/items", tags=["items"])


def _serialize_item_summary(product: Product, category_name: Optional[str] = None) -> ItemSummary:
	return ItemSummary(
		id=product.id,
		sku=product.sku,
		name=product.name,
		category=category_name or "unknown",
		stock=int(product.quantity or 0),
	)


@router.get('', response_model=List[ItemSummary])
def list_items(
	limit: int = Query(20, ge=1, le=200),
	page: int = Query(1, ge=1),
	category: Optional[str] = None,
	db: Session = Depends(get_db),
):
	"""List items from the current database-backed inventory."""
	query = db.query(Product, Category.name).join(Category, Product.category_id == Category.id)
	if category:
		query = query.filter(Category.name.ilike(f"%{category}%"))

	rows = (
		query
		.order_by(Product.name.asc())
		.offset((page - 1) * limit)
		.limit(limit)
		.all()
	)

	return [_serialize_item_summary(product, category_name) for product, category_name in rows]


@router.get('/{item_id}', response_model=ItemSummary)
def get_item(item_id: int, db: Session = Depends(get_db)):
	row = (
		db.query(Product, Category.name)
		.join(Category, Product.category_id == Category.id)
		.filter(Product.id == item_id)
		.first()
	)
	if not row:
		raise HTTPException(status_code=404, detail='Item not found')
	product, category_name = row
	return _serialize_item_summary(product, category_name)


# ============================================================================
# CRUD ENDPOINTS - Database-backed (Product model)
# ============================================================================

@router.post('', response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_item(data: ProductCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
	"""
	Crear nuevo producto en inventario.

	- **category_id**: ID de categoría existente (requerido)
	- **name**: Nombre del producto (requerido)
	- **sku**: Código único de producto (requerido)
	- **price**: Precio en centavos (requerido)
	- **quantity**: Cantidad inicial (default: 0)
	- **min_quantity**: Stock mínimo para alertas (default: 5)
	"""
	return create_product_record(
		db,
		category_id=data.category_id,
		name=data.name,
		sku=data.sku,
		description=data.description,
		price=data.price,
		quantity=data.quantity,
		min_quantity=data.min_quantity,
	)


@router.put('/{item_id}', response_model=ProductResponse)
def update_item(item_id: int, data: ProductUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
	"""
	Actualizar producto existente.

	Solo se actualizan los campos proporcionados.
	"""
	product = get_product_or_404(
		db,
		item_id,
		detail=f"Producto con ID {item_id} no encontrado"
	)
	return update_product_record(db, product, data.model_dump(exclude_unset=True))


@router.delete('/{item_id}', status_code=status.HTTP_200_OK)
def delete_item(item_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
	"""
	Eliminar producto del inventario.

	Retorna confirmación con ID del producto eliminado.
	"""
	product = get_product_or_404(
		db,
		item_id,
		detail=f"Producto con ID {item_id} no encontrado"
	)
	delete_product_record(db, product)
	return {"message": "Producto eliminado", "id": item_id}
