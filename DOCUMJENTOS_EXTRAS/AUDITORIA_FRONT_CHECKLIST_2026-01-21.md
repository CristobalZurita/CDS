# AUDITORIA FRONTEND COMPLETA - CHECKLIST DE ACCIONES Y BOTONES
**Fecha:** 2026-01-21
**Alcance:** Front completo (publico, cliente, admin) + validacion de acciones.
**Objetivo:** Detectar donde faltan botones/acciones y que debe existir segun el flujo del sistema.

---

## 1) RUTAS PUBLICAS (sitio)

### Home (`/`)
- Contacto: formulario existe en `ContactForm.vue` y envia a `/contact`.
- **Checklist:**
  - [ ] Mensaje se guarda en backend y aparece en `/admin/contact`.
  - [ ] Validaciones de campos (min/max, email valido).

### Cotizador IA (`/cotizador-ia`)
- Flujo de cotizacion existe (selector, diagnostico, resultado).
- **Checklist:**
  - [ ] Resultado se guarda como quote real (backend).
  - [ ] Boton “Agendar” redirige a `/agendar`.

### Agendar (`/agendar`)
- UI completa y hace POST a `/appointments`.
- **Checklist:**
  - [ ] Cita creada aparece en `/admin/appointments`.
  - [ ] Validaciones de fecha/hora y campos.

### Registro (`/register`)
- Usuario se registra; admin lo aprueba.
- **Checklist:**
  - [ ] Registro crea usuario con rol cliente y estado pendiente.
  - [ ] Admin puede aprobar/rechazar.

---

## 2) PANEL CLIENTE (usuario autenticado)

### Dashboard (`/dashboard`)
- Muestra stats + accesos rapidos.
- **Checklist:**
  - [ ] Estadisticas vienen del backend (no mock).
  - [ ] Acciones rapidas funcionan (agendar, cotizar, ver reparaciones).

### Reparaciones (`/repairs`)
- Lista de reparaciones del cliente.
- **Checklist:**
  - [ ] Lista real desde `/client/repairs`.
  - [ ] Boton “Ver detalles” abre `/repairs/:id`.

### Reparacion detalle (`/repairs/:id`)
- Muestra status, fotos, notas.
- **Checklist:**
  - [ ] Datos reales y actualizados.

### Perfil (`/profile`)
- Edicion de perfil + preferencias.
- **Checklist:**
  - [ ] Guardar perfil funciona (PUT `/client/profile`).
  - [ ] Preferencias guardan en backend.

---

## 3) PANEL ADMIN

### Admin Dashboard (`/admin`)
- Stats + reparaciones + usuarios.
- **Checklist:**
  - [ ] Stats vienen de `/stats` (sin error 500).
  - [ ] Boton “Actualizar” en listas funciona.

### Clientes (`/admin/clients`)
- **Estado actual:** solo lista/seleccion, no hay boton crear.
- **Debe existir:**
  - [ ] Boton “Nuevo Cliente”.
  - [ ] Formulario para crear cliente.
  - [ ] Boton “Editar Cliente”.
  - [ ] Boton “Eliminar Cliente”.
- **Instrumentos dentro de cliente:**
  - [ ] Boton “Agregar instrumento” (ya existe).
  - [ ] Boton “Editar/Eliminar instrumento” (falta).

### Reparaciones (`/admin/repairs`)
- **Estado actual:** solo lista, sin crear.
- **Debe existir:**
  - [ ] Boton “Nueva Reparacion”.
  - [ ] Formulario conectado (`RepairForm.vue`).
  - [ ] Editar/borrar reparacion (ya existe editar/borrar).

### Inventario (`/admin/inventory`)
- **Estado actual:** boton nuevo existe pero wiring incorrecto.
- **Debe existir:**
  - [ ] Listado real de items (API correcta).
  - [ ] Formulario con `category_id` (select categorias).
  - [ ] Crear/editar/borrar items funcionando.
  - [ ] Busqueda y filtros por categoria.

### Inventario Unificado (`/admin/inventory/unified`)
- **Estado actual:** usa fetch relativo.
- **Debe existir:**
  - [ ] Busqueda por categoria real.
  - [ ] Boton “Iniciar importacion” funcional (si backend lo soporta).

### Categorias (`/admin/categories`)
- **Estado actual:** solo listado.
- **Debe existir:**
  - [ ] Boton “Nueva Categoria”.
  - [ ] Formulario de categoria (nombre, descripcion, tipo).

### Citas (`/admin/appointments`)
- **Estado actual:** UI completa.
- **Checklist:**
  - [ ] Citas creadas desde `/agendar` o usuario llegan aqui.

### Contacto (`/admin/contact`)
- **Estado actual:** pagina existe.
- **Debe existir:**
  - [ ] Mensajes de `ContactForm` visibles.
  - [ ] Filtro/estado (nuevo/leido/archivado).

### Newsletter (`/admin/newsletter`)
- **Debe existir:**
  - [ ] Lista de suscriptores.
  - [ ] Opcion de enviar campaña.

### Stats (`/admin/stats`)
- **Debe existir:**
  - [ ] Clientes totales.
  - [ ] Instrumentos totales.
  - [ ] Reparaciones por estado.

---

## 4) OBSERVACIONES TECNICAS CLAVE

- Varias acciones fallan por **uso de fetch relativo** (`/api/v1`) en lugar de `api` con `VITE_API_URL`.
- Formularios existen pero no estan conectados a paginas (ej: `RepairForm.vue`).
- Falta flujo completo de creacion/admin en clientes, reparaciones, categorias y usuarios.

---

## 5) PROXIMO PASO

Usar este checklist como contrato funcional.
Una vez validado, se implementan los botones y acciones de forma **aditiva**.
