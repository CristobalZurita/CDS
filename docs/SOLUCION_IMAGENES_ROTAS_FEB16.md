# Solución: Imágenes Rotas en Cotizador - Feb 16, 2026

## Problema
El cotizador mostraba **todas las fotos del inventario interno** como imágenes rotas después de la migración a WebP.

## Raíz del Problema
1. **No había campo `image_url` en la tabla `products`** de la BD
2. El frontend usaba **rutas hardcodeadas** (`/images/instrumentos/{id}.webp`) que no existían
3. Las imágenes rotas se mostraban por defecto en el navegador

## Solución Implementada (3 capas)

### 1. BACKEND - Agregar campo a BD ✅
**Archivo:** `backend/app/models/inventory.py`
- Agregado: `image_url: Column(String(500), nullable=True)`
- Migración Alembic creada: `007_add_image_url_to_products.py`

**Archivo:** `backend/app/schemas.py`
- Agregado: `image_url: Optional[str]` al schema `InventoryItemBase`

**Archivo:** `backend/app/routers/inventory.py`
- Actualizado endpoint `/inventory` para devolver `image_url` desde BD

### 2. BACKEND - Limpiar datos existentes ✅
**Script:** `backend/scripts/cleanup_inventory_images.py`
- Establece `image_url = NULL` para todos los productos existentes
- Previene mostrar rutas inválidas

### 3. FRONTEND - Ocultar imágenes rotas ✅
**Archivo:** `src/vue/components/quotation/InteractiveInstrumentDiagnostic.vue`
- Agregado manejador `@error` en imágenes
- Agrega clase `img-broken` cuando falla la carga
- CSS oculta imágenes con clase `img-broken`

**Archivo:** `src/composables/useInstrumentsCatalog.ts`
- Actualizada documentación: Catálogo es **SOLO para instrumentos predefinidos**
- No es fuente de datos de inventario

## Flujo de Datos Correcto

```
Frontend (Cotizador IA)
    ↓
    Muestra catálogo de instrumentos FROM JSON (/assets/data/instruments.json)
    ↓
    Imágenes vienen del catálogo JSON (imagePath generado)
    ↓
    Si imagen no existe → se oculta automáticamente por CSS

Inventario (Admin Panel)
    ↓
    Lee de BD /api/v1/inventory
    ↓
    Devuelve image_url (NULL por ahora, puede poblarse después)
    ↓
    Frontend renderiza solo si image_url tiene valor real
```

## Diferencias: Catálogo vs Inventario

| Aspecto | Catálogo (Cotizador) | Inventario (Admin) |
|---------|-------------------|------------------|
| Fuente | JSON estático | Base de datos |
| Endpoint | Local (assets) | `/api/v1/inventory` |
| Fotos | Inventario (estático) | Base de datos (dinámico) |
| Propósito | Diagnóstico público | Gestión técnica |
| Imágenes rotas | Se ocultan automáticamente | NULL en BD |

## Pasos de Ejecución

### 1. Ejecutar migración Alembic
```bash
cd backend
alembic upgrade head
```

### 2. Ejecutar script de limpieza (opcional pero recomendado)
```bash
cd backend
python scripts/cleanup_inventory_images.py
```

### 3. Recargar frontend
El navegador debería:
- ✅ Mostrar catálogo de instrumentos correctamente
- ✅ NO mostrar imágenes rotas
- ✅ Ocultar automáticamente fotos 404

## Resultado Final

**Cotizador:** Limpio, sin imágenes rotas, muestra solo instrumentos predefinidos
**Inventario:** Preparado para recibir URLs reales de imágenes desde BD
**Frontend:** Lógica separada entre catálogo (estático) e inventario (dinámico)

---
**Status:** ✅ COMPLETADO - Feb 16, 2026 14:15
**Commits:** Pendientes (hacer git commit/push)
