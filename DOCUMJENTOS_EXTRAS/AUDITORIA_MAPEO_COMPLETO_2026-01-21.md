# AUDITORIA MAPEO COMPLETO: ENDPOINTS - DB - FRONTEND

**Fecha:** 2026-01-21
**Método:** Análisis de imports reales y grep de consumo API

---

## 1. MAPEO ROUTER -> MODELO -> TABLA DB

| Router | Modelo Importado | Tabla DB Real |
|--------|------------------|---------------|
| `analytics.py` | (usa ReportingService) | Agregaciones de: repairs, clients, invoices, warranties |
| `appointment.py` | Appointment | `appointments` |
| `category.py` | Category | `categories` |
| `client.py` | User, Client, Device, Repair, RepairStatus | `users`, `clients`, `devices`, `repairs`, `repair_statuses` |
| `clients.py` | Client, Device | `clients`, `devices` |
| `contact.py` | ContactMessage | `contact_messages` |
| `device.py` | Device, DeviceType, DeviceBrand, Client | `devices`, `device_types`, `device_brands`, `clients` |
| `diagnostic.py` | Diagnostic, Quote, Client | `diagnostics`, `quotes`, `clients` |
| `instrument.py` | Instrument | `instruments` |
| `inventory.py` | Product, Stock, Category | `products`, `stock`, `categories` |
| `invoice.py` | Invoice, InvoiceItem | `invoices`, `invoice_items` |
| `newsletter.py` | NewsletterSubscription | `newsletter_subscriptions` |
| `payments.py` | Payment | `payments` |
| `quotation.py` | (sin modelo - usa JSON) | N/A (lee de assets/data/) |
| `repair.py` | Repair, RepairStatus, AuditLog, RepairNote, RepairPhoto, Device | `repairs`, `repair_statuses`, `audit_logs`, `repair_notes`, `repair_photos`, `devices` |
| `repair_status.py` | RepairStatus | `repair_statuses` |
| `stock_movement.py` | StockMovement | `stock_movements` |
| `tools.py` | Tool | `tools` |
| `uploads.py` | (sin modelo) | N/A (solo archivos) |
| `user.py` | User | `users` |
| `warranty.py` | Warranty, WarrantyClaim | `warranties`, `warranty_claims` |

---

## 2. CONSUMO DE API EN FRONTEND

### 2.1 Endpoints Consumidos (verificado en código)

| Endpoint | Método | Archivo Frontend |
|----------|--------|------------------|
| `/repairs` | GET | stores/repairs.js |
| `/repairs` | POST | stores/repairs.js |
| `/repairs/:id` | PUT | stores/repairs.js, RepairDetailAdminPage.vue |
| `/repairs/:id` | DELETE | stores/repairs.js |
| `/repairs/:id/notes` | GET | RepairDetailAdminPage.vue |
| `/repairs/:id/notes` | POST | RepairDetailAdminPage.vue |
| `/repairs/:id/photos` | GET | RepairDetailAdminPage.vue |
| `/repairs/:id/photos` | POST | RepairDetailAdminPage.vue |
| `/repairs/:id/components` | GET | RepairComponentsManager.vue |
| `/repairs/:id/components` | POST | RepairComponentsManager.vue |
| `/repairs/:id/components/:id` | DELETE | RepairComponentsManager.vue |
| `/clients` | GET | ClientsPage.vue |
| `/clients/:id/devices` | GET | ClientDetail.vue |
| `/client/dashboard` | GET | DashboardPage.vue |
| `/client/repairs` | GET | RepairsPage.vue |
| `/client/repairs/:id/details` | GET | RepairDetailPage.vue |
| `/client/profile` | GET | ProfilePage.vue |
| `/client/profile` | PUT | ProfilePage.vue |
| `/appointments/` | GET | AppointmentsPage.vue |
| `/appointments/` | POST | AppointmentModal.vue |
| `/appointments/:id` | PATCH | AppointmentsPage.vue |
| `/appointments/:id` | DELETE | AppointmentsPage.vue |
| `/contact` | POST | ContactForm.vue |
| `/contact/messages` | GET | ContactMessagesPage.vue |
| `/newsletter/subscribe` | POST | NewsletterSection.vue |
| `/newsletter/subscriptions` | GET | NewsletterSubscriptionsPage.vue |
| `/quotations/estimate` | POST | QuoteGenerator.vue, useQuotation.js |
| `/inventory/` | GET | InventoryPage.vue |
| `/diagnostic` | GET | stores/diagnostics.js |
| `/diagnostic/calculate` | POST | stores/diagnostics.js |
| `/diagnostic/:id` | PUT | stores/diagnostics.js |
| `/diagnostic/:id` | DELETE | stores/diagnostics.js |
| `/categories` | GET | stores/categories.js |
| `/categories` | POST | stores/categories.js |
| `/categories/:id` | PUT | stores/categories.js |
| `/categories/:id` | DELETE | stores/categories.js |
| `/instruments` | GET | stores/instruments.js |
| `/instruments` | POST | stores/instruments.js |
| `/instruments/:id` | PUT | stores/instruments.js |
| `/instruments/:id` | DELETE | stores/instruments.js |
| `/users` | GET | stores/users.js |
| `/users` | POST | stores/users.js |
| `/users/:id` | PUT | stores/users.js |
| `/users/:id` | DELETE | stores/users.js |
| `/stock-movements` | GET | stores/stockMovements.js |
| `/stock-movements` | POST | stores/stockMovements.js, StockMovementsList.vue |
| `/stats` | GET | StatsPage.vue, AdminDashboard.vue |
| `/uploads/images` | POST | (varios componentes) |
| `/auth/forgot-password` | POST | PasswordReset.vue |
| `/auth/reset-password` | POST | PasswordReset.vue |
| `/devices/` | POST | (componentes de dispositivo) |

### 2.2 Archivos con Llamadas API

| Archivo | Tipo | Endpoints Usados |
|---------|------|------------------|
| `src/services/api.js` | Config | Base axios |
| `src/composables/useApi.js` | Config | Wrapper axios |
| `src/composables/useAuth.js` | Auth | login, logout, refresh |
| `src/composables/useQuotation.js` | Feature | /quotations/estimate |
| `src/stores/repairs.js` | Store | /repairs CRUD |
| `src/stores/diagnostics.js` | Store | /diagnostic CRUD |
| `src/stores/inventory.js` | Store | /inventory |
| `src/stores/categories.js` | Store | /categories CRUD |
| `src/stores/instruments.js` | Store | /instruments CRUD |
| `src/stores/users.js` | Store | /users CRUD |
| `src/stores/stockMovements.js` | Store | /stock-movements |

---

## 3. TABLAS DB SIN ENDPOINT DIRECTO

| Tabla DB | Razón |
|----------|-------|
| `comp_resistors` | Catálogo estático |
| `comp_capacitors` | Catálogo estático |
| `comp_integrated_circuits` | Catálogo estático |
| `comp_transistors` | Catálogo estático |
| `comp_diodes` | Catálogo estático |
| `comp_*` (otros) | Catálogos estáticos |
| `device_brands` | Lookup via device.py |
| `device_types` | Lookup via device.py |
| `tool_brands` | Lookup via tools.py |
| `tool_categories` | Lookup via tools.py |
| `storage_locations` | Lookup |
| `user_roles` | Lookup |
| `permissions` | Via dependencies.py |
| `role_permissions` | Via dependencies.py |
| `repair_component_usage` | Via repair.py components |
| `repair_tool_usage` | Via repair.py |
| `invoice_sequences` | Auto-generado |
| `audit_logs` | Auto-generado |

---

## 4. ENDPOINTS BACKEND SIN CONSUMO FRONTEND

| Router | Endpoint | Probable Razón |
|--------|----------|----------------|
| `analytics.py` | GET /dashboard | Admin dashboard interno |
| `analytics.py` | GET /repairs/export | Exportar CSV |
| `analytics.py` | GET /revenue/* | Reportes financieros |
| `analytics.py` | GET /technicians | Métricas técnicos |
| `analytics.py` | GET /warranties | Métricas garantías |
| `analytics.py` | GET /kpis/summary | KPIs resumen |
| `invoice.py` | Todos | Módulo facturación pendiente |
| `warranty.py` | Todos | Módulo garantías pendiente |
| `tools.py` | Todos | Módulo herramientas pendiente |
| `payments.py` | Todos | Módulo pagos pendiente |
| `repair_status.py` | POST/PUT/DELETE | Admin solo |

---

## 5. FLUJO DE DATOS VERIFICADO

### 5.1 Flujo Reparaciones
```
Frontend                    Backend                     DB
─────────                   ─────────                   ──
RepairsPage.vue ──────────> /repairs ──────────────────> repairs
  └─ useRepairsStore        repair.py
                              └─ Repair model

RepairDetailPage.vue ─────> /repairs/:id/notes ────────> repair_notes
                            /repairs/:id/photos ───────> repair_photos
                            /repairs/:id/components ───> repair_component_usage
```

### 5.2 Flujo Clientes
```
Frontend                    Backend                     DB
─────────                   ─────────                   ──
ClientsPage.vue ──────────> /clients ──────────────────> clients
ClientDetail.vue ─────────> /clients/:id/devices ──────> devices
DashboardPage.vue ────────> /client/dashboard ─────────> (agregación)
```

### 5.3 Flujo Cotizaciones
```
Frontend                    Backend                     DB
─────────                   ─────────                   ──
QuoteGenerator.vue ───────> /quotations/estimate ──────> (cálculo, no DB)
DiagnosticWizard.vue ─────> /diagnostic/quotes ────────> quotes
```

---

## 6. RESUMEN

### Cobertura

| Métrica | Valor |
|---------|-------|
| Routers backend | 22 |
| Tablas DB | 55 |
| Archivos frontend con API | 46 |
| Endpoints consumidos | ~45 |
| Endpoints sin consumo | ~30 (admin/reportes) |

### Estado de Módulos

| Módulo | Backend | Frontend | DB |
|--------|---------|----------|-----|
| Repairs | ✅ | ✅ | ✅ |
| Clients | ✅ | ✅ | ✅ |
| Devices | ✅ | ✅ | ✅ |
| Appointments | ✅ | ✅ | ✅ |
| Contact | ✅ | ✅ | ✅ |
| Newsletter | ✅ | ✅ | ✅ |
| Quotations | ✅ | ✅ | Parcial |
| Diagnostic | ✅ | ✅ | ✅ |
| Inventory | ✅ | ✅ | ✅ |
| Categories | ✅ | ✅ | ✅ |
| Users | ✅ | ✅ | ✅ |
| Analytics | ✅ | Parcial | N/A |
| Invoices | ✅ | ❌ | ✅ |
| Warranties | ✅ | ❌ | ✅ |
| Payments | ✅ | ❌ | ✅ |
| Tools | ✅ | ❌ | ✅ |

---

## 7. RECOMENDACIONES

1. **Módulos pendientes de UI**: invoices, warranties, payments, tools
2. **Analytics**: Completar integración con dashboard admin
3. **Componentes electrónicos**: Crear CRUD si se requiere administración
4. **Endpoints /stats**: Verificar mapeo real (puede ser alias de analytics)

---

*Mapeo verificado contra código real - ADITIVO NO DESTRUCTIVO*
*Generado: 2026-01-21*
