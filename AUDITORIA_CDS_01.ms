# AUDITORIA CDS (Exhaustiva)

## Resumen
- Routers backend: 22
- Routers con permisos granulares: 2
- Routers con auth (get_current_user/admin): 18
- Endpoints con auth sin permiso granular: 97
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

### Permisos granulares
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

### Endpoints con auth sin permisos granulares
- backend/app/routers/payments.py:15 @router.post("/", response_model=PaymentRead)
- backend/app/routers/repair_status.py:12 @router.get("/", response_model=List[Dict])
- backend/app/routers/repair_status.py:18 @router.post("/", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair_status.py:35 @router.put("/{status_id}")
- backend/app/routers/repair_status.py:48 @router.delete("/{status_id}")
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
- backend/app/routers/clients.py:13 @router.get("/", response_model=List[Dict])
- backend/app/routers/clients.py:30 @router.get("/{client_id}", response_model=Dict)
- backend/app/routers/clients.py:47 @router.post("/", status_code=status.HTTP_201_CREATED)
- backend/app/routers/clients.py:65 @router.put("/{client_id}")
- backend/app/routers/clients.py:78 @router.delete("/{client_id}")
- backend/app/routers/clients.py:88 @router.get("/{client_id}/devices", response_model=List[Dict])
- backend/app/routers/inventory.py:19 @router.get("/")
- backend/app/routers/inventory.py:90 @router.get("/{product_id}")
- backend/app/routers/inventory.py:126 @router.get("/low-stock/alerts")
- backend/app/routers/stock_movement.py:9 @router.get("/")
- backend/app/routers/stock_movement.py:13 @router.post("/")
- backend/app/routers/repair.py:21 @router.get("/")
- backend/app/routers/repair.py:26 @router.post("/", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:116 @router.put("/{repair_id}")
- backend/app/routers/repair.py:159 @router.delete("/{repair_id}")
- backend/app/routers/repair.py:179 @router.get("/{repair_id}/audit")
- backend/app/routers/repair.py:201 @router.post("/{repair_id}/components", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:226 @router.get("/{repair_id}/components")
- backend/app/routers/repair.py:232 @router.delete("/{repair_id}/components/{usage_id}", status_code=status.HTTP_200_OK)
- backend/app/routers/repair.py:246 @router.post("/{repair_id}/notes", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:265 @router.get("/{repair_id}/notes")
- backend/app/routers/repair.py:276 @router.post("/{repair_id}/photos", status_code=status.HTTP_201_CREATED)
- backend/app/routers/repair.py:295 @router.get("/{repair_id}/photos")
- backend/app/routers/instrument.py:9 @router.get("/")
- backend/app/routers/instrument.py:13 @router.post("/")
- backend/app/routers/instrument.py:21 @router.put("/{instrument_id}")
- backend/app/routers/instrument.py:32 @router.delete("/{instrument_id}")
- backend/app/routers/newsletter.py:37 @router.get("/subscriptions", response_model=List[NewsletterSubscriptionOut])
- backend/app/routers/category.py:9 @router.get("/")
- backend/app/routers/category.py:13 @router.post("/")
- backend/app/routers/category.py:21 @router.put("/{category_id}")
- backend/app/routers/category.py:32 @router.delete("/{category_id}")
- backend/app/routers/user.py:20 @router.get("/", response_model=list[UserRead])
- backend/app/routers/user.py:24 @router.post("/", response_model=UserRead)
- backend/app/routers/user.py:41 @router.put("/{user_id}", response_model=UserRead)
- backend/app/routers/user.py:57 @router.delete("/{user_id}")
- backend/app/routers/warranty.py:23 @router.post("/", status_code=status.HTTP_201_CREATED)
- backend/app/routers/warranty.py:61 @router.post("/auto-create/{repair_id}", status_code=status.HTTP_201_CREATED)
- backend/app/routers/warranty.py:74 @router.get("/")
- backend/app/routers/warranty.py:103 @router.get("/expiring-soon")
- backend/app/routers/warranty.py:114 @router.get("/by-repair/{repair_id}")
- backend/app/routers/warranty.py:128 @router.get("/check-coverage/{repair_id}")
- backend/app/routers/warranty.py:145 @router.get("/{warranty_id}")
- backend/app/routers/warranty.py:156 @router.post("/{warranty_id}/void")
- backend/app/routers/warranty.py:179 @router.post("/{warranty_id}/claims", status_code=status.HTTP_201_CREATED)
- backend/app/routers/warranty.py:210 @router.get("/claims")
- backend/app/routers/warranty.py:223 @router.get("/{warranty_id}/claims")
- backend/app/routers/warranty.py:234 @router.get("/claims/{claim_id}")
- backend/app/routers/warranty.py:245 @router.post("/claims/{claim_id}/evaluate")
- backend/app/routers/warranty.py:279 @router.post("/claims/{claim_id}/process")
- backend/app/routers/warranty.py:306 @router.post("/claims/{claim_id}/complete")
- backend/app/routers/warranty.py:322 @router.post("/maintenance/update-expired")
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
- backend/app/routers/device.py:24 @router.get("/", response_model=List[Dict])
- backend/app/routers/device.py:30 @router.get("/{device_id}", response_model=Dict)
- backend/app/routers/device.py:46 @router.post("/", status_code=status.HTTP_201_CREATED)
- backend/app/routers/device.py:75 @router.put("/{device_id}")
- backend/app/routers/device.py:88 @router.delete("/{device_id}")
- backend/app/routers/contact.py:48 @router.get("/messages", response_model=List[ContactMessageOut])
- backend/app/routers/contact.py:57 @router.get("/messages/{message_id}", response_model=ContactMessageOut)
- backend/app/routers/tools.py:90 @router.get("/", response_model=List[ToolRead])
- backend/app/routers/tools.py:109 @router.get("/{tool_id}", response_model=ToolRead)
- backend/app/routers/tools.py:125 @router.post("/", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
- backend/app/routers/tools.py:148 @router.put("/{tool_id}", response_model=ToolRead)
- backend/app/routers/tools.py:185 @router.delete("/{tool_id}")
- backend/app/routers/tools.py:206 @router.post("/{tool_id}/calibrate", response_model=ToolRead)

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