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

- `4` módulos con CRUD E2E completo hoy:
  - usuarios
  - categorías
  - inventario
  - reparaciones
- Base:
  - `tests/e2e/admin-crud.spec.ts`

Pendiente para decir "CRUD admin total":
- cotizaciones
- citas
- tickets
- solicitudes de compra
- manuales

### 4. Flujos transversales y roles

Cubiertos hoy:
- login admin por UI
- login cliente por UI
- redirect de ruta protegida a login
- cotizador/diagnóstico con fotos de catálogo
- firma por token
- carga de foto por token
- navegación pública, cliente y admin sin errores visibles

Base:
- `tests/e2e/auth.spec.ts`
- `tests/e2e/quotation.spec.ts`
- `tests/e2e/public.spec.ts`
- `tests/e2e/site-audit.spec.ts`

### 5. Cobertura de código con Vitest

Estado:
- La instrumentación ya quedó configurada y `npm run test:coverage` sí ejecuta coverage.
- El número global todavía no es confiable porque la suite unitaria/integración actual está parcialmente obsoleta.

Última corrida:
- `208` tests pasando
- `74` tests fallando
- `10` archivos fallando
- `4` archivos pasando

Tipos de fallo detectados:
- tests que esperan contratos viejos de stores/composables
- tests que usan Pinia sin `setActivePinia(createPinia())`
- expectativas de APIs que ya no existen en `useAuth` y `useApi`

Conclusión:
- La cobertura de código está "medible", pero no "presentable" todavía.
- Antes de reportar porcentaje de líneas/branches hay que sanear esa suite.

## Resultado operativo actual

### Barrido E2E

- `npm run test:e2e`
- Resultado actual: `73/73` passing

### Build

- `npm run build`
- Resultado actual: passing

### Coverage de Vitest

- `npm run test:coverage`
- Estado actual: ejecuta, pero falla por deuda en tests unitarios.

## Cómo leer el porcentaje real hoy

Si se resume en una sola frase:

- Cobertura de rutas funcionales: `100%`
- Cobertura de auditoría admin: `100%`
- Cobertura CRUD profunda del negocio: `parcial`
- Cobertura de código instrumentada: `bloqueada por tests obsoletos`

## Qué falta para acercarse al "100%"

### Fase 1: cerrar cobertura funcional

1. Agregar CRUD E2E para:
   - quotes
   - appointments
   - tickets
   - purchase-requests
   - manuals
2. Cubrir estados de error:
   - `401`
   - `403`
   - `404`
   - `422`
   - `500`
3. Cubrir estados visuales:
   - loading
   - empty
   - forbidden
   - retry/error

### Fase 2: cerrar cobertura técnica

1. Corregir tests Vitest que quedaron fuera de contrato.
2. Crear setup común de Pinia para composables/stores.
3. Reescribir tests que validan APIs eliminadas o contratos viejos.
4. Recién entonces reportar:
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

Hoy el sitio tiene cobertura E2E completa de rutas y una auditoría automatizada de todos los módulos visibles del admin. Eso permite detectar enlaces rotos, endpoints faltantes, errores JS y flujos críticos sin revisar todo a mano. Lo que todavía falta para hablar de "100% total" es completar CRUD profundo en módulos secundarios y sanear la suite unitaria para obtener porcentaje de código confiable.
