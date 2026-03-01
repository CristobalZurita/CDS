# Testing Status Brief

Fecha de corte: 2026-02-28

## Qué está automatizado hoy

- `npm run test:e2e`
  - `88/88` pruebas pasando
  - cubre rutas públicas, cliente, admin y dinámicas
  - audita enlaces internos visibles
  - detecta errores JS, requests fallidos y respuestas `4xx/5xx`
  - cubre CRUD admin profundo en:
    - usuarios
    - categorías
    - inventario
    - reparaciones
    - cotizaciones
    - citas
    - tickets
    - solicitudes de compra
    - manuales
  - cubre flujos reales de cliente/público:
    - contacto público
    - edición de perfil cliente
    - agendamiento de cita
    - pagos OT con comprobante real
    - descarga de PDF de cierre
    - estados de error visibles:
      - login inválido
      - token inválido de carga de foto
      - redirecciones por permisos/guest routes
      - rutas inexistentes

- `npm run test:coverage`
  - `160/160` pruebas Vitest pasando
  - coverage real actual:
    - statements/lines: `36.99%`
    - branches: `59.76%`
    - functions: `36.85%`
  - reportes para IDE:
    - `coverage/lcov.info`
    - `coverage/coverage-summary.json`

- `npm run build`
  - build de producción pasando

## Qué detecta sin revisar a mano

- enlaces rotos
- botones que disparan errores de front
- endpoints faltantes o mal conectados
- rutas protegidas mal resueltas
- formularios que aparentan éxito pero no persisten
- regresiones en CRUD admin principal

## Qué no está cubierto al 100%

- todos los estados de error posibles (`401`, `403`, `404`, `422`, `500`)
- todos los estados visuales (`loading`, `empty`, `forbidden`, `retry`)
- todos los módulos cliente/público con acciones profundas
- la mayoría de vistas/componentes del front a nivel unitario

## Frase corta para explicarlo

El proyecto ya tiene una auditoría automatizada real del sitio: no sólo revisa que las páginas carguen, sino que prueba rutas, CRUD admin, flujos clave de cliente/público y detecta errores visibles de integración sin tener que recorrer el sistema botón por botón.
