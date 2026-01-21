# AUDITORIA FRONTEND UI (ACCIONES FALTANTES)
**Fecha:** 2026-01-21
**Alcance:** Admin UI y flujos de creacion/gestion (clientes, instrumentos, reparaciones, inventario, categorias, usuarios, citas).
**Metodo:** Revision de vistas Vue y componentes admin + analisis de endpoints usados en front.

---

## 1) Flujos clave que faltan en la UI (sin boton o sin pantalla de creacion)

### Clientes
- **No hay boton para crear cliente** en `src/vue/content/pages/admin/ClientsPage.vue`.
- La lista solo permite seleccionar cliente, no crear ni editar.
- El detalle muestra dispositivos, pero depende de que exista cliente creado previamente.

### Instrumentos (dispositivos del cliente)
- Existe formulario de agregar dispositivo en `src/vue/components/admin/ClientDetail.vue`.
- **Falta UI para crear instrumento fuera del cliente** (si se quisiera catalogo general).

### Reparaciones
- `src/vue/components/admin/RepairsList.vue` solo tiene editar/borrar.
- **No hay boton para crear reparacion nueva** desde admin.
- Existe `src/vue/components/admin/RepairForm.vue`, pero **no esta conectado** a ninguna pagina.

### Categorias
- `src/vue/components/admin/CategoryList.vue` solo tiene editar/borrar.
- **No hay boton de crear categoria** ni formulario conectado.

### Usuarios
- `src/vue/components/admin/UserList.vue` solo tiene editar/borrar.
- **No hay boton de crear usuario** ni formulario conectado.

---

## 2) Acciones que existen pero fallan por wiring incorrecto

### Inventario (items)
- Hay boton **"Nuevo item"** en `src/vue/content/pages/admin/InventoryPage.vue`.
- **Falla porque el store usa fetch relativo**:
  - `src/stores/inventory.js` llama a `/api/v1/items` (relativo) en lugar de usar `API_URL`.
  - En el navegador esto va a `http://localhost:5173/api/v1/...` y da 404.
- **El formulario envia `category` (texto)** pero el backend exige `category_id`.
  - `src/vue/components/admin/InventoryForm.vue` usa `form.category`.
  - Resultado: error 422 en backend.

### Inventario Unificado (POC)
- `src/views/InventoryUnified.vue` tambien usa fetch relativo `/api/v1/...`.
- Si el API esta en `localhost:8000`, vuelve a fallar por 404.

---

## 3) Citas (admin)
- La pagina `src/vue/content/pages/admin/AppointmentsPage.vue` si tiene acciones (confirmar/cancelar/eliminar).
- Depende de API `/appointments` y funciona **solo si el backend esta disponible**.

---

## 4) Que SI esta implementado en UI
- **Detalle de reparacion** en `src/vue/content/pages/admin/RepairDetailAdminPage.vue` tiene:
  - Cambio de estado
  - Materiales usados
  - Fotos
  - Notas
- **Agregar dispositivo a cliente** existe en `ClientDetail.vue`.
- **Inventario** tiene tabla y formulario (aunque con fallas de wiring).

---

## 5) Diagnostico: por que se ve "caja vacia"
- En varias secciones el UI esta **solo en modo listado** sin botones de creacion.
- Inventario y POC fallan por endpoints mal apuntados (fetch relativo).
- Formularios no conectados (`RepairForm`, `InstrumentForm`).

---

## 6) Recomendaciones de correccion (orden sugerido)

1) **Unificar consumo de API en el front**
   - Reemplazar fetch relativos en stores por `api` de `src/services/api.js`.
   - Asegurar que todo use `VITE_API_URL`.

2) **Inventario**
   - Cambiar formulario para enviar `category_id` (select de categorias).
   - Ajustar store para usar `api` y no `/api/v1` relativo.

3) **Clientes**
   - Agregar boton "Nuevo Cliente" en `ClientsPage.vue`.
   - Crear formulario (modal o pagina) que consuma `POST /clients`.

4) **Reparaciones**
   - Conectar `RepairForm.vue` a `RepairsAdminPage.vue`.
   - Agregar boton "Nueva Reparacion".

5) **Categorias / Usuarios**
   - Agregar boton "Nueva Categoria" y formulario.
   - Agregar boton "Nuevo Usuario" y formulario.

6) **Instrumentos**
   - Definir si se crean siempre dentro del cliente (flujo actual) o existe catalogo general.
   - Si es catalogo general: conectar `InstrumentForm.vue`.

---

## 7) Archivos clave revisados
- `src/vue/content/pages/admin/ClientsPage.vue`
- `src/vue/components/admin/ClientList.vue`
- `src/vue/components/admin/ClientDetail.vue`
- `src/vue/content/pages/admin/InventoryPage.vue`
- `src/stores/inventory.js`
- `src/vue/components/admin/InventoryForm.vue`
- `src/views/InventoryUnified.vue`
- `src/vue/components/admin/RepairsList.vue`
- `src/vue/components/admin/RepairForm.vue`
- `src/vue/components/admin/UserList.vue`
- `src/vue/components/admin/CategoryList.vue`

---

**Resultado:**
El frontend admin **no es solo fachada**, pero **faltan botones de creacion** y hay **fallas de wiring** que hacen que varias acciones no se vean o no funcionen.
