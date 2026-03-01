# Testing Coverage Matrix

Fecha de corte: 2026-02-28

## Qué significa "100% cubierto" en este proyecto

No existe un solo porcentaje útil. Para esta aplicación conviene medir cinco capas:

1. Cobertura de rutas del producto.
2. Cobertura de auditoría funcional por módulo.
3. Cobertura CRUD de entidades críticas.
4. Cobertura de flujos transversales y roles.
5. Cobertura de código instrumentada con Vitest.

## Estado actual

### 1. Rutas del producto

- `43/43` rutas de aplicación cubiertas por E2E.
- Desglose:
  - Públicas: `19/19`
  - Cliente: `5/5`
  - Admin: `15/15`
  - Dinámicas/tokenizadas: `4/4`
- Base:
  - `tests/e2e/routes.spec.ts`
  - `tests/e2e/dynamic-routes.spec.ts`
  - `tests/e2e/auth.spec.ts`

Notas:
- El catch-all `/:pathMatch(.*)*` no se contabiliza como ruta funcional.
- Las rutas dinámicas cubiertas son:
  - `/repairs/:id`
  - `/admin/repairs/:id`
  - `/signature/:token`
  - `/photo-upload/:token`

### 2. Auditoría funcional por módulo admin

- `15/15` módulos admin con auditoría de acciones seguras.
- Base:
  - `tests/e2e/site-audit.spec.ts`
- Módulos cubiertos:
  - `/admin`
  - `/admin/clients`
  - `/admin/categories`
  - `/admin/inventory/unified`
  - `/admin/inventory`
  - `/admin/quotes`
  - `/admin/repairs`
  - `/admin/appointments`
  - `/admin/contact`
  - `/admin/newsletter`
  - `/admin/tickets`
  - `/admin/purchase-requests`
  - `/admin/manuals`
  - `/admin/stats`
  - `/admin/archive`

Qué valida esta auditoría:
- Carga de la vista.
- Errores JS de página.
- Requests fallidos.
- Respuestas `4xx/5xx`.
- Botones/acciones seguras clave por módulo.

### 3. CRUD de entidades críticas

- `9/9` módulos admin críticos con CRUD E2E completo hoy:
  - usuarios
  - categorías
  - inventario
  - reparaciones
  - cotizaciones
  - citas
  - tickets
  - solicitudes de compra
  - manuales
- Base:
  - `tests/e2e/admin-crud.spec.ts`
  - `tests/e2e/admin-extended-crud.spec.ts`

Lectura correcta:
- El CRUD admin principal quedó cubierto de punta a punta.
- Lo que sigue faltando no es CRUD admin base, sino más profundidad en flujos cliente/público y estados de error.

### 4. Flujos transversales y roles

Cubiertos hoy:
- login admin por UI
- login cliente por UI
- redirect de ruta protegida a login
- cotizador/diagnóstico con fotos de catálogo
- formulario de contacto público con persistencia real
- actualización de perfil cliente con persistencia real
- agendamiento de cita cliente con persistencia real
- descarga cliente de PDF de cierre desde una reparación real
- firma por token
- carga de foto por token
- navegación pública, cliente y admin sin errores visibles

Base:
- `tests/e2e/auth.spec.ts`
- `tests/e2e/client-public-actions.spec.ts`
- `tests/e2e/quotation.spec.ts`
- `tests/e2e/public.spec.ts`
- `tests/e2e/site-audit.spec.ts`

### 5. Cobertura de código con Vitest

Estado:
- La instrumentación quedó operativa y la suite unitaria/integración ya no tiene deuda bloqueante.

Última corrida:
- `150` tests pasando
- `0` tests fallando
- summary actual:
  - statements: `13.65%`
  - branches: `53.72%`
  - functions: `33.60%`
  - lines: `13.65%`

Lectura correcta:
- El coverage ya es real y estable, pero hoy es bajo.
- Ese porcentaje refleja que el frente completo es mucho más grande que la parte actualmente cubierta con Vitest.
- La foto útil hoy no es "los tests fallan", sino "las pruebas unitarias sólo cubren una fracción pequeña del producto".

## Resultado operativo actual

### Barrido E2E

- `npm run test:e2e`
- Resultado actual: `82/82` passing

### Build

- `npm run build`
- Resultado actual: passing

### Coverage de Vitest

- `npm run test:coverage`
- Estado actual: ejecuta y reporta coverage real.

## Cómo leer el porcentaje real hoy

Si se resume en una sola frase:

- Cobertura de rutas funcionales: `100%`
- Cobertura de auditoría admin: `100%`
- Cobertura CRUD admin profunda del negocio: `100%`
- Cobertura de código instrumentada: `real, estable y todavía baja`

## Qué falta para acercarse al "100%"

### Fase 1: cerrar cobertura funcional

1. Cubrir estados de error:
   - `401`
   - `403`
   - `404`
   - `422`
   - `500`
2. Extender flujos cliente/público con acciones profundas:
   - OT payments
   - historial de reparaciones con cambios de estado relevantes
   - descargas/adjuntos adicionales
   - formularios públicos secundarios
3. Cubrir estados visuales:
   - loading
   - empty
   - forbidden
   - retry/error

### Fase 2: cerrar cobertura técnica

1. Subir cobertura de componentes y vistas críticas.
2. Cubrir más stores/composables activos del flujo real.
3. Añadir tests unitarios para servicios front clave.
4. Mantener el setup común actual y seguir creciendo desde esta base.
5. Recién entonces reportar objetivos de umbral altos:
   - line coverage
   - branch coverage
   - function coverage

## Comandos de referencia

```bash
npm run test:e2e
npm run build
npm run test:coverage
```

## Resumen corto para explicar a otra persona

Hoy el sitio tiene cobertura E2E completa de rutas, auditoría automatizada de todos los módulos visibles del admin, CRUD admin profundo y flujos reales de cliente/público. Eso permite detectar enlaces rotos, endpoints faltantes, errores JS y regresiones funcionales sin revisar todo a mano. Lo que todavía falta para hablar de "100% total" es cubrir más estados de error, más acciones profundas fuera del admin y seguir levantando la cobertura unitaria del front.
