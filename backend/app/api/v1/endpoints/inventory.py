from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from functools import lru_cache
import os
import pandas as pd

from app.schemas.inventory import ItemSummary, ProductCreate, ProductUpdate, ProductResponse
from app.models.inventory import Product
from app.core.database import get_db

router = APIRouter(prefix="/items", tags=["items"])


@lru_cache(maxsize=1)
def _load_excel(path: Optional[str] = None):
	if path is None:
		path = os.path.abspath(os.path.join(os.getcwd(), 'Inventario_Cirujanosintetizadores.xlsx'))
	if not os.path.exists(path):
		raise FileNotFoundError(f'Excel file not found: {path}')
	df = pd.read_excel(path, sheet_name=0, dtype=object, engine='openpyxl')
	return df.fillna('')


def _row_to_item(idx: int, row: pd.Series) -> ItemSummary:
	# For POC: pick first non-empty value among prioritized columns
	priority = ["Ic's", 'Transistores', 'Resistencias', 'Diodos', 'Diodo Led', 'otros', 'herramientas taller', 'insumos taller']
	name = None
	category = None
	for col in priority:
		if col in row and str(row[col]).strip():
			name = str(row[col]).strip()
			category = col
			break
	if name is None:
		# fallback: use the 'otros' column or the first non-empty
		for c in row.index:
			if str(row[c]).strip():
				name = str(row[c]).strip()
				category = str(c)
				break
	item = ItemSummary(
		id=int(row.get('N°') or idx),
		name=name or f'row-{idx}',
		category=category or 'unknown',
		stock=10,
		sku=str(row.get('N°') or idx)
	)
	return item


@router.get('', response_model=List[ItemSummary])
def list_items(limit: int = Query(20, ge=1, le=200), page: int = Query(1, ge=1), category: Optional[str] = None):
	"""List items derived from the Excel master (POC - read-only, non-persistent)

	This POC endpoint reads the Excel file and returns a flattened list of items for UI prototyping.
	"""
	try:
		df = _load_excel()
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="Excel master file not found on server")

	items: List[ItemSummary] = []
	for idx, row in df.iterrows():
		item = _row_to_item(idx + 1, row)
		if category and category.lower() not in item.category.lower():
			continue
		items.append(item)

	start = (page - 1) * limit
	end = start + limit
	return items[start:end]


@router.get('/{item_id}', response_model=ItemSummary)
def get_item(item_id: int):
	try:
		df = _load_excel()
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="Excel master file not found on server")
	for idx, row in df.iterrows():
		if int(row.get('N°') or (idx + 1)) == item_id:
			return _row_to_item(idx + 1, row)
	raise HTTPException(status_code=404, detail='Item not found')


# ============================================================================
# CRUD ENDPOINTS - Database-backed (Product model)
# ============================================================================

@router.post('', response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_item(data: ProductCreate, db: Session = Depends(get_db)):
	"""
	Crear nuevo producto en inventario.

	- **category_id**: ID de categoría existente (requerido)
	- **name**: Nombre del producto (requerido)
	- **sku**: Código único de producto (requerido)
	- **price**: Precio en centavos (requerido)
	- **quantity**: Cantidad inicial (default: 0)
	- **min_quantity**: Stock mínimo para alertas (default: 5)
	"""
	# Verificar SKU único
	existing = db.query(Product).filter(Product.sku == data.sku).first()
	if existing:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"SKU '{data.sku}' ya existe"
		)

	product = Product(
		category_id=data.category_id,
		name=data.name,
		sku=data.sku,
		description=data.description,
		price=data.price,
		quantity=data.quantity,
		min_quantity=data.min_quantity
	)

	try:
		db.add(product)
		db.commit()
		db.refresh(product)
	except IntegrityError as e:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Error de integridad: verificar category_id existe"
		)

	return product


@router.put('/{item_id}', response_model=ProductResponse)
def update_item(item_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
	"""
	Actualizar producto existente.

	Solo se actualizan los campos proporcionados.
	"""
	product = db.query(Product).filter(Product.id == item_id).first()

	if not product:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Producto con ID {item_id} no encontrado"
		)

	# Verificar SKU único si se está cambiando
	if data.sku and data.sku != product.sku:
		existing = db.query(Product).filter(Product.sku == data.sku).first()
		if existing:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"SKU '{data.sku}' ya existe"
			)

	# Actualizar solo campos proporcionados
	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		if value is not None:
			setattr(product, field, value)

	try:
		db.commit()
		db.refresh(product)
	except IntegrityError:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Error de integridad: verificar category_id existe"
		)

	return product


@router.delete('/{item_id}', status_code=status.HTTP_200_OK)
def delete_item(item_id: int, db: Session = Depends(get_db)):
	"""
	Eliminar producto del inventario.

	Retorna confirmación con ID del producto eliminado.
	"""
	# Usar delete directo para evitar lazy load de relaciones inconsistentes
	from sqlalchemy import delete
	result = db.execute(delete(Product).where(Product.id == item_id))

	if result.rowcount == 0:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Producto con ID {item_id} no encontrado"
		)

	db.commit()

	return {"message": "Producto eliminado", "id": item_id}
