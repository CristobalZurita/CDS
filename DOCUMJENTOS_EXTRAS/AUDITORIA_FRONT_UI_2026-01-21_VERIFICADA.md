# AUDITORIA FRONTEND UI (VERIFICACION)
**Fecha:** 2026-01-21
**Base:** `AUDITORIA_FRONT_UI_2026-01-21.md`
**Metodo:** Contraste directo contra codigo actual.

---

## Pendientes confirmados (UI)

### Clientes
- **Sin boton de crear cliente** en `src/vue/content/pages/admin/ClientsPage.vue`.
- Solo lista y detalle; no hay formulario conectado para crear/editar cliente.

### Reparaciones
- `src/vue/components/admin/RepairsList.vue` solo tiene editar/borrar.
- **No existe boton "Nueva Reparacion"** en admin.
- `src/vue/components/admin/RepairForm.vue` existe, pero **no esta conectado** a ninguna pagina.

### Categorias
- `src/vue/components/admin/CategoryList.vue` solo editar/borrar.
- **No existe boton "Nueva Categoria"** ni formulario conectado.

### Usuarios
- `src/vue/components/admin/UserList.vue` solo editar/borrar.
- **No existe boton "Nuevo Usuario"** ni formulario conectado.

---

## Acciones que existen pero fallan por wiring

### Inventario (items)
- Boton **"Nuevo item"** existe en `src/vue/content/pages/admin/InventoryPage.vue`.
- **Store usa fetch relativo** en `src/stores/inventory.js`:
  - `/api/v1/items` apunta al frontend (`localhost:5173`) y da 404.
- **Formulario envia `category` texto** (`src/vue/components/admin/InventoryForm.vue`).
  - Backend exige `category_id` -> error 422.

### Inventario Unificado (POC)
- `src/views/InventoryUnified.vue` usa fetch relativo `/api/v1/...`.
- Falla si el API corre en `localhost:8000`.

---

## Funcionalidad existente (SI funciona si API esta ok)
- **Agregar dispositivos a cliente** en `src/vue/components/admin/ClientDetail.vue`.
- **Detalle de reparacion** en `src/vue/content/pages/admin/RepairDetailAdminPage.vue` con:
  - Cambio de estado, materiales, fotos, notas.
- **Citas (admin)** en `src/vue/content/pages/admin/AppointmentsPage.vue`.

---

## Observacion clave
El frontend **no es fachada vacia**, pero faltan botones de creacion en flujos clave y hay wiring incorrecto que impide usar inventario e importaciones.

---

## Recomendaciones inmediatas (orden sugerido)

1) **Unificar consumo API**
   - Reemplazar fetch relativos por `api` (`src/services/api.js`).

2) **Inventario**
   - Cambiar formulario a `category_id` con selector de categorias.

3) **Clientes**
   - Agregar boton "Nuevo Cliente" + formulario conectado a `POST /clients`.

4) **Reparaciones**
   - Conectar `RepairForm.vue` y agregar boton "Nueva Reparacion".

5) **Categorias/Usuarios**
   - Agregar botones y formularios de creacion.

---

## Archivos verificados
- `src/vue/content/pages/admin/ClientsPage.vue`
- `src/vue/components/admin/ClientDetail.vue`
- `src/vue/components/admin/RepairsList.vue`
- `src/vue/components/admin/CategoryList.vue`
- `src/vue/components/admin/UserList.vue`
- `src/vue/content/pages/admin/InventoryPage.vue`
- `src/stores/inventory.js`

