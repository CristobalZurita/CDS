# KiCad Catalog Workflow (Aditivo)

Este flujo agrega una capa de catalogo profesional basada en nomenclatura KiCad/JEDEC/EIA sin borrar ni reemplazar tus fuentes actuales.

## 1) Generar catalogo KiCad normalizado

```bash
python scripts/ingest/build_kicad_component_catalog.py
```

Salida:

- `DE_PYTHON_NUEVO/json/kicad_component_catalog.json`
- `DE_PYTHON_NUEVO/json/kicad_component_catalog_summary.json`

Cada item queda marcado como:

- `origin_status: REAL` si viene de tus JSON actuales.
- `origin_status: CATALOGO_ONLY` si fue agregado como referencia comercial.
- `enabled: true/false` para activar solo lo que realmente existe.

Extensiones manuales:

- Archivo: `DE_PYTHON_NUEVO/json/manual_inventory_extensions.txt`
- Regla: se agregan solo entradas no duplicadas contra `display_name` existente.
- Estado por defecto de extensiones manuales: `origin_status=REAL`, `enabled=true`.

## 2) Importar a base de datos (sin destruir)

Solo reales:

```bash
cd backend
python scripts/import_kicad_component_catalog.py --dry-run
```

Reales + catalogo ampliado:

```bash
cd backend
python scripts/import_kicad_component_catalog.py --dry-run --include-catalog-only
```

Aplicar cambios reales:

```bash
cd backend
python scripts/import_kicad_component_catalog.py
```

Aplicar todo el catalogo:

```bash
cd backend
python scripts/import_kicad_component_catalog.py --include-catalog-only
```

Notas:

- El importador hace `upsert` por `sku`.
- No elimina productos existentes.
- No modifica stock/cantidad existente en productos ya creados.
- Se adapta al esquema real de `products`/`categories` detectando columnas disponibles.
