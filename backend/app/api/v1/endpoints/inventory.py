from fastapi import APIRouter, Query, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.inventory import ItemSummary, ProductCreate, ProductUpdate, ProductResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.inventory_product_service import (
    create_product_record,
    delete_product_record,
    get_item_summary_or_404,
    get_product_or_404,
    list_item_summaries,
    update_product_record,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get('', response_model=List[ItemSummary], deprecated=True)
def list_items(
    limit: int = Query(20, ge=1, le=200),
    page: int = Query(1, ge=1),
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Compatibility list endpoint. Canonical inventory flow lives under /inventory."""
    return list_item_summaries(
        db,
        limit=limit,
        page=page,
        category=category,
    )


@router.get('/{item_id}', response_model=ItemSummary, deprecated=True)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return get_item_summary_or_404(db, item_id)


# ============================================================================
# CRUD ENDPOINTS - Database-backed (Product model)
# ============================================================================

@router.post('', response_model=ProductResponse, status_code=status.HTTP_201_CREATED, deprecated=True)
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


@router.put('/{item_id}', response_model=ProductResponse, deprecated=True)
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


@router.delete('/{item_id}', status_code=status.HTTP_200_OK, deprecated=True)
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
