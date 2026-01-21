# AUDITORIA CDS

## Resumen
- Routers backend encontrados: 22
- Routers con permisos granulares: 2
- Archivos vacíos (solo proyecto): 0
- Archivos muy pequeños (posibles stubs, solo proyecto): 7
- Archivos con TODO/FIXME/HACK (solo proyecto): 3
- Vistas con placeholders (heurístico): 2
- Directorios de referencia en MODELOS: 12

## Backend
### Alembic
- Migraciones con down_revision=None: 0
  - backend/alembic/versions/002_add_columns_to_existing_tables.py: down_revision=unknown
  - backend/alembic/versions/78b5056b2086_initial_baseline_empty.py: down_revision=unknown
  - backend/alembic/versions/001_add_permission_invoice_warranty_models.py: down_revision=unknown

### Permisos granulares en routers
- Routers con require_permission*: 2 / 22
  - ⚠️ backend/app/routers/diagnostic.py
  - ⚠️ backend/app/routers/payments.py
  - ⚠️ backend/app/routers/repair_status.py
  - ⚠️ backend/app/routers/quotation.py
  - ✅ backend/app/routers/invoice.py
  - ⚠️ backend/app/routers/clients.py
  - ⚠️ backend/app/routers/inventory.py
  - ⚠️ backend/app/routers/appointment.py
  - ⚠️ backend/app/routers/uploads.py
  - ⚠️ backend/app/routers/stock_movement.py
  - ⚠️ backend/app/routers/repair.py
  - ⚠️ backend/app/routers/instrument.py
  - ⚠️ backend/app/routers/newsletter.py
  - ⚠️ backend/app/routers/category.py
  - ⚠️ backend/app/routers/user.py
  - ⚠️ backend/app/routers/__init__.py
  - ⚠️ backend/app/routers/warranty.py
  - ⚠️ backend/app/routers/client.py
  - ✅ backend/app/routers/analytics.py
  - ⚠️ backend/app/routers/device.py
  - ⚠️ backend/app/routers/contact.py
  - ⚠️ backend/app/routers/tools.py

## Frontend
### Vistas con placeholders (heurístico)
- src/modules/smdCapacitor/SmdCapacitorView.vue
- src/modules/resistorColor/ResistorColorView.vue

### Archivos vacíos
- No se detectaron archivos vacíos.

### Archivos muy pequeños (posible stub)
- backend/app/core/__init__.py
- backend/app/routers/__init__.py
- backend/app/services/__init__.py
- backend/app/crud/__init__.py
- backend/app/api/__init__.py
- backend/app/api/v1/__init__.py
- backend/tests/__init__.py

### TODO/FIXME/HACK
- src/vue/components/articles/DiagnosticWizard.vue
- src/vue/content/pages/CotizadorIAPage.vue
- backend/app/routers/diagnostic.py

## MODELOS (referencias)
- MODELOS/vue-stripe-main
- MODELOS/Stock-App-master
- MODELOS/fullcalendar-vue-main
- MODELOS/stock-app-main
- MODELOS/qalendar-master
- MODELOS/inventory-system-master
- MODELOS/laravel-tickets-master
- MODELOS/vue-cal-main
- MODELOS/Geeker-Admin-master
- MODELOS/Appointment-Booking-System-master
- MODELOS/Appointment-Booking-System-main
- MODELOS/laravel-inertia-vue-main

## Archivos clave revisados
- src/router/index.js
- src/router/index.ts