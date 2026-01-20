# AUDITORIA CDS (FIX)

## Contexto
- Basada en AUDITORIA_CDS_01.ms y estado actual del repo.

## Resumen
- Routers backend: 22
- Routers con permisos granulares: 18
- Routers con auth (get_current_user/admin): 18
- Endpoints con auth sin permiso granular: 51
- Archivos vacíos (solo proyecto): 0
- Archivos muy pequeños (posibles stubs): 7
- Archivos con TODO/FIXME/HACK: 3
- Vistas con placeholders: 2
- Imports /src inexistentes: 0
- Archivos muy grandes (>500KB, JS/TS/PY/Vue): 0
- Directorios en MODELOS: 12

## Backend
### Alembic
- Migraciones con down_revision=None: 0
  - backend/alembic/versions/002_add_columns_to_existing_tables.py: down_revision=unknown
  - backend/alembic/versions/78b5056b2086_initial_baseline_empty.py: down_revision=unknown
  - backend/alembic/versions/001_add_permission_invoice_warranty_models.py: down_revision=unknown

### Permisos granulares (cuello de botella)
- Routers con require_permission*: 18 / 22
  - ✅ backend/app/routers/diagnostic.py
  - ✅ backend/app/routers/payments.py
  - ✅ backend/app/routers/repair_status.py
  - ⚠️ backend/app/routers/quotation.py
  - ✅ backend/app/routers/invoice.py
  - ✅ backend/app/routers/clients.py
  - ✅ backend/app/routers/inventory.py
  - ✅ backend/app/routers/appointment.py
  - ⚠️ backend/app/routers/uploads.py
  - ✅ backend/app/routers/stock_movement.py
  - ✅ backend/app/routers/repair.py
  - ✅ backend/app/routers/instrument.py
  - ✅ backend/app/routers/newsletter.py
  - ✅ backend/app/routers/category.py
  - ✅ backend/app/routers/user.py
  - ⚠️ backend/app/routers/__init__.py
  - ✅ backend/app/routers/warranty.py
  - ⚠️ backend/app/routers/client.py
  - ✅ backend/app/routers/analytics.py
  - ✅ backend/app/routers/device.py
  - ✅ backend/app/routers/contact.py
  - ✅ backend/app/routers/tools.py

### Endpoints con auth sin permisos granulares (riesgo)
- backend/app/routers/invoice.py:65 @router.post("/from-repair/{repair_id}", status_code=status.HTTP_201_CREATED)
- backend/app/routers/invoice.py:127 @router.get("/summary")
- backend/app/routers/invoice.py:143 @router.get("/overdue")
- backend/app/routers/invoice.py:153 @router.get("/{invoice_id}")
- backend/app/routers/invoice.py:164 @router.get("/by-number/{invoice_number}")
- backend/app/routers/invoice.py:182 @router.post("/{invoice_id}/items", status_code=status.HTTP_201_CREATED)
- backend/app/routers/invoice.py:215 @router.delete("/{invoice_id}/items/{item_id}")
- backend/app/routers/invoice.py:232 @router.post("/{invoice_id}/send")
- backend/app/routers/invoice.py:246 @router.post("/{invoice_id}/mark-viewed")
- backend/app/routers/invoice.py:282 @router.post("/{invoice_id}/payments", status_code=status.HTTP_201_CREATED)
- backend/app/routers/invoice.py:318 @router.post("/maintenance/mark-overdue")
- backend/app/routers/clients.py:39 @router.get("/{client_id}", response_model=Dict)
- backend/app/routers/clients.py:110 @router.get("/{client_id}/devices", response_model=List[Dict])
- backend/app/routers/repair.py:201 @router.get("/{repair_id}/audit")
- backend/app/routers/repair.py:223 @router.post("/{repair_id}/components", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:248 @router.get("/{repair_id}/components")
- backend/app/routers/repair.py:254 @router.delete("/{repair_id}/components/{usage_id}", status_code=status.HTTP_200_OK)
- backend/app/routers/repair.py:268 @router.post("/{repair_id}/notes", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:287 @router.get("/{repair_id}/notes")
- backend/app/routers/repair.py:298 @router.post("/{repair_id}/photos", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:317 @router.get("/{repair_id}/photos")
- backend/app/routers/warranty.py:66 @router.post("/auto-create/{repair_id}", status_code=status.HTTP_201_CREATED)
- backend/app/routers/warranty.py:108 @router.get("/expiring-soon")
- backend/app/routers/warranty.py:119 @router.get("/by-repair/{repair_id}")
- backend/app/routers/warranty.py:133 @router.get("/check-coverage/{repair_id}")
- backend/app/routers/warranty.py:150 @router.get("/{warranty_id}")
- backend/app/routers/warranty.py:184 @router.post("/{warranty_id}/claims", status_code=status.HTTP_201_CREATED)
- backend/app/routers/warranty.py:215 @router.get("/claims")
- backend/app/routers/warranty.py:228 @router.get("/{warranty_id}/claims")
- backend/app/routers/warranty.py:239 @router.get("/claims/{claim_id}")
- backend/app/routers/warranty.py:284 @router.post("/claims/{claim_id}/process")
- backend/app/routers/warranty.py:311 @router.post("/claims/{claim_id}/complete")
- backend/app/routers/warranty.py:327 @router.post("/maintenance/update-expired")
- backend/app/routers/client.py:103 @router.get("/dashboard")
- backend/app/routers/client.py:172 @router.get("/repairs")
- backend/app/routers/client.py:205 @router.get("/repairs/{repair_id}/timeline")
- backend/app/routers/client.py:229 @router.get("/repairs/{repair_id}/details")
- backend/app/routers/client.py:292 @router.get("/profile")
- backend/app/routers/client.py:312 @router.put("/profile")
- backend/app/routers/analytics.py:49 @router.get("/alerts")
- backend/app/routers/analytics.py:67 @router.get("/repairs")
- backend/app/routers/analytics.py:98 @router.get("/repairs/timeline")
- backend/app/routers/analytics.py:155 @router.get("/revenue")
- backend/app/routers/analytics.py:177 @router.get("/revenue/timeline")
- backend/app/routers/analytics.py:197 @router.get("/clients")
- backend/app/routers/analytics.py:219 @router.get("/inventory")
- backend/app/routers/analytics.py:242 @router.get("/technicians")
- backend/app/routers/analytics.py:274 @router.get("/warranties")
- backend/app/routers/analytics.py:297 @router.get("/kpis/summary")
- backend/app/routers/tools.py:110 @router.get("/{tool_id}", response_model=ToolRead)
- backend/app/routers/tools.py:186 @router.delete("/{tool_id}")

## Frontend
### Vistas con placeholders (heurístico)
- src/modules/smdCapacitor/SmdCapacitorView.vue
- src/modules/resistorColor/ResistorColorView.vue

### Imports /src inexistentes
- No se detectaron imports inválidos /src.

### Archivos muy grandes (>500KB)
- No se detectaron archivos JS/TS/PY/Vue >500KB.

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