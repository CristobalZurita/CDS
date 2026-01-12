from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from functools import lru_cache
import os
import pandas as pd

from backend.app.schemas.inventory import ItemSummary

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
