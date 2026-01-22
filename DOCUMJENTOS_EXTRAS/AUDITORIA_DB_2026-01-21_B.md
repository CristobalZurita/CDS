# AUDITORIA EXHAUSTIVA DE BASE DE DATOS (REVISION B)

**Fecha:** 2026-01-21
**Base de datos:** `backend/cirujano.db`
**Tamaño:** 675,840 bytes
**Metodo:** Queries con esquema real verificado

---

## 1. ESQUEMAS REALES UTILIZADOS

### 1.1 users
```
id, email (NOT NULL), username, hashed_password (NOT NULL), first_name, last_name,
phone, avatar_url, role_id (NOT NULL, default 3), is_active (default 1),
is_verified (default 0), verification_token, reset_token, reset_token_expires,
created_at, updated_at, last_login
```

### 1.2 clients
```
id, user_id, name (NOT NULL), email, phone, phone_alt, address, city, region,
country (default 'Chile'), preferred_contact (default 'whatsapp'), notes,
total_repairs (default 0), total_spent (default 0), created_at, updated_at
```

### 1.3 repairs
```
id, repair_number (NOT NULL), device_id (NOT NULL), quote_id, status_id (NOT NULL, default 1),
assigned_to, intake_date, diagnosis_date, approval_date, start_date, completion_date,
delivery_date, problem_reported (NOT NULL), diagnosis, work_performed, parts_cost,
labor_cost, additional_cost, discount, total_cost, payment_status (default 'pending'),
payment_method, paid_amount, warranty_days (default 90), warranty_until, priority (default 2),
created_at, updated_at
```

### 1.4 devices
```
id, client_id (NOT NULL), device_type_id (NOT NULL), brand_id, brand_other,
model (NOT NULL), serial_number, year_manufactured, description, condition_notes,
photos, total_repairs (default 0), first_repair_date, last_repair_date, created_at, updated_at
```

### 1.5 payments
```
id, user_id, repair_id, amount (NOT NULL), payment_method (NOT NULL),
transaction_id, status (NOT NULL), notes, created_at (NOT NULL), updated_at (NOT NULL)
```

---

## 2. INVENTARIO DE TABLAS

### 2.1 Total
- **56 tablas** (incluyendo 3 vistas)
- **20 tablas con datos**
- **36 tablas vacías**

### 2.2 Tablas con Datos (ordenadas por volumen)

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| comp_integrated_circuits | 173 | Circuitos integrados |
| comp_resistors | 168 | Resistencias |
| comp_transistors | 112 | Transistores |
| comp_capacitors | 93 | Capacitores |
| audit_logs | 30 | Logs de auditoría |
| comp_diodes | 28 | Diodos |
| device_brands | 14 | Marcas de dispositivos |
| tool_brands | 12 | Marcas de herramientas |
| device_types | 10 | Tipos de dispositivos |
| repair_statuses | 9 | Estados de reparación |
| tool_categories | 7 | Categorías de herramientas |
| storage_locations | 6 | Ubicaciones de almacén |
| user_roles | 3 | Roles de usuario |
| products | 3 | Productos |
| users | 2 | Usuarios |
| clients | 2 | Clientes |
| categories | 2 | Categorías |
| newsletter_subscriptions | 1 | Suscripciones newsletter |
| appointments | 1 | Citas |
| alembic_version | 1 | Versión migraciones |

### 2.3 Tablas Vacías (operativas)
```
repairs (0), devices (0), invoices (0), payments (0), quotes (0),
warranties (0), warranty_claims (0), repair_notes (0), repair_photos (0),
permissions (0), roles (0), role_permissions (0), tools (0), stock (0),
stock_movements (0), diagnostics (0), contact_messages (0)
```

---

## 3. INTEGRIDAD DE CAMPOS OBLIGATORIOS

| Check | Query | Resultado |
|-------|-------|-----------|
| Users sin email | `WHERE email IS NULL OR email = ''` | **0** |
| Users sin hashed_password | `WHERE hashed_password IS NULL` | **0** |
| Clients sin name | `WHERE name IS NULL OR name = ''` | **0** |
| Quotes sin quote_number | `WHERE quote_number IS NULL` | **0** |
| Quotes sin client_id | `WHERE client_id IS NULL` | **0** |

### Datos de Users

| ID | Username | Email | Role ID | Activo | Verificado |
|----|----------|-------|---------|--------|------------|
| 1 | admin | admin@cirujanodesintetizadores.cl | 1 | 1 | 1 |
| 2 | testuser_5010f99f | testuser_5010f99f@example.com | 3 | 1 | 0 |

### Datos de Clients

| ID | User ID | Nombre | Email | Teléfono | Repairs | Spent |
|----|---------|--------|-------|----------|---------|-------|
| 1 | 2 | Test User | testuser_5010f99f@example.com | +56911111111 | 0 | 0.0 |
| 2 | 1 | Cristóbal Zurita | admin@cirujanodesintetizadores.cl | +56982957538 | 0 | 0.0 |

---

## 4. FOREIGN KEYS

### 4.1 PRAGMA foreign_key_check
```
Resultado: (vacío - sin errores)
```

### 4.2 Checks Manuales

| Tabla Origen | FK | Tabla Destino | Rotas |
|--------------|-----|---------------|-------|
| repairs | device_id | devices | **0** |
| repairs | status_id | repair_statuses | **0** |
| repairs | assigned_to | users | **0** |
| devices | client_id | clients | **0** |
| clients | user_id | users | **0** |
| quotes | client_id | clients | **0** |
| invoices | client_id | clients | **0** |
| invoices | repair_id | repairs | **0** |
| payments | repair_id | repairs | **0** |
| payments | user_id | users | **0** |
| warranties | repair_id | repairs | **0** |
| warranties | client_id | clients | **0** |
| warranty_claims | warranty_id | warranties | **0** |
| repair_notes | repair_id | repairs | **0** |
| repair_photos | repair_id | repairs | **0** |

**Total FK rotas: 0**

---

## 5. DUPLICADOS

| Check | Query | Resultado |
|-------|-------|-----------|
| Emails duplicados en users | `GROUP BY email HAVING COUNT(*) > 1` | **0** |
| Usernames duplicados en users | `GROUP BY username HAVING COUNT(*) > 1` | **0** |
| Emails duplicados en clients | `GROUP BY email HAVING COUNT(*) > 1` | **0** |
| repair_number duplicados | `GROUP BY repair_number HAVING COUNT(*) > 1` | **0** |
| quote_number duplicados | `GROUP BY quote_number HAVING COUNT(*) > 1` | **0** |
| invoice_number duplicados | `GROUP BY invoice_number HAVING COUNT(*) > 1` | **0** |
| claim_number duplicados | `GROUP BY claim_number HAVING COUNT(*) > 1` | **0** |

**Total duplicados: 0**

---

## 6. ESTADOS INVÁLIDOS

### 6.1 Repair Statuses Disponibles

| ID | Código | Nombre | Orden |
|----|--------|--------|-------|
| 1 | pending_quote | Pendiente Cotización | 1 |
| 2 | quoted | Cotizado | 2 |
| 3 | approved | Aprobado | 3 |
| 4 | in_progress | En Proceso | 4 |
| 5 | waiting_parts | Esperando Repuestos | 5 |
| 6 | testing | En Pruebas | 6 |
| 7 | completed | Completado | 7 |
| 8 | delivered | Entregado | 8 |
| 9 | cancelled | Cancelado | 9 |

### 6.2 Validaciones de Estado

| Check | Resultado |
|-------|-----------|
| Repairs con status_id inválido | **0** |
| Users con role_id inválido (no 1,2,3) | **0** |
| Appointments con estado inválido | **0** |
| Invoices con status inválido | **0** |
| Warranties con status inválido | **0** |
| Warranty_claims con status inválido | **0** |
| Payments con status inválido | **0** |

**Total estados inválidos: 0**

---

## 7. DATOS DE REFERENCIA

### 7.1 User Roles

| ID | Nombre | Descripción |
|----|--------|-------------|
| 1 | admin | Administrador - acceso total |
| 2 | technician | Técnico - gestión de trabajos |
| 3 | client | Cliente - ver estado de equipos |

### 7.2 Device Brands (muestra)

| ID | Nombre |
|----|--------|
| 1 | Korg |
| 4 | Moog |
| 6 | Novation |
| 7 | Arturia |
| 8 | Behringer |
| 9 | Akai |
| 10 | Native Instruments |
| 11 | Elektron |
| 12 | Access |
| 13 | Nord |

### 7.3 Device Types

| ID | Nombre |
|----|--------|
| 1 | Sintetizador |
| 2 | Teclado/Workstation |
| 3 | Caja de Ritmos |
| 4 | Sampler |
| 5 | Efectos/Pedal |
| 6 | Amplificador |
| 7 | Mezclador |
| 8 | Interfaz de Audio |
| 9 | Controlador MIDI |
| 10 | Otro |

### 7.4 Storage Locations

| ID | Nombre |
|----|--------|
| 1 | Banco Principal |
| 2 | Banco Soldadura |
| 3 | Armario Instrumentos |
| 4 | Armario Componentes |
| 5 | Estantería A |
| 6 | Estantería B |

### 7.5 Catálogo de Componentes

| Tipo | Cantidad |
|------|----------|
| Resistencias | 168 |
| Capacitores | 93 |
| Circuitos Integrados | 173 |
| Transistores | 112 |
| Diodos | 28 |
| **TOTAL** | **574** |

---

## 8. AUDIT LOGS (últimos 10)

| ID | Evento | User ID | Fecha |
|----|--------|---------|-------|
| 30 | payment.list | - | 2026-01-19 21:40:29 |
| 29 | payment.list | - | 2026-01-19 21:40:20 |
| 28 | auth.login.success | 1 | 2026-01-19 10:38:07 |
| 27 | auth.login.failed | 1 | 2026-01-19 10:38:01 |
| 26 | auth.login.success | 1 | 2026-01-18 18:31:48 |
| 25 | auth.login.success | 1 | 2026-01-18 18:30:57 |
| 24 | auth.login.success | 1 | 2026-01-18 18:09:54 |
| 23 | auth.login.success | 1 | 2026-01-18 17:28:06 |
| 22 | auth.login.success | 1 | 2026-01-18 17:21:55 |
| 21 | auth.login.success | 1 | 2026-01-18 16:44:36 |

---

## 9. COMPARATIVA CON AUDITORIA ANTERIOR

| Métrica | AUDITORIA_DB_2026-01-21.md | Esta Auditoría |
|---------|----------------------------|----------------|
| FK rotas | 0 | **0** (confirmado) |
| Duplicados | 0 | **0** (confirmado) |
| Estados inválidos | 0 | **0** (confirmado) |
| Nulos en obligatorios | 0 | **0** (confirmado) |
| Errores de columna | Varios | **0** (corregidos) |

**Diferencias encontradas:** Ninguna en los resultados. La auditoría anterior tenía errores en las queries por columnas inexistentes, pero los resultados finales coinciden.

---

## 10. RESUMEN EJECUTIVO

### Estado: **BASE DE DATOS LIMPIA**

| Categoría | Errores | Notas |
|-----------|---------|-------|
| FK Rotas | 0 | Todas las referencias son válidas |
| Duplicados | 0 | Sin claves duplicadas |
| Estados Inválidos | 0 | Todos los estados son válidos |
| Nulos en Obligatorios | 0 | Campos NOT NULL respetados |
| Errores de Schema | 0 | Queries compatibles con schema real |

### Observaciones

1. **Base de datos en estado inicial**: Tablas operativas vacías (repairs=0, devices=0, invoices=0)
2. **Catálogo de componentes poblado**: 574 componentes electrónicos listos
3. **Sistema de usuarios funcional**: 2 usuarios (admin role_id=1, test role_id=3)
4. **Sistema de clientes funcional**: 2 clientes vinculados a usuarios
5. **Catálogos de referencia completos**: 9 estados, 10 tipos de dispositivo, 14 marcas, 6 ubicaciones
6. **Auditoría activa**: 30 registros de eventos

### Recomendaciones

1. **Seed de permisos**: Tabla `permissions` vacía - ejecutar seed si se requiere RBAC granular
2. **Datos de prueba**: Considerar crear reparaciones de ejemplo para testing E2E
3. **Cliente #2 no verificado**: `testuser_5010f99f` tiene `is_verified=0`

---

## 11. QUERIES DE VERIFICACIÓN RÁPIDA

```sql
-- Inventario
SELECT name, (SELECT COUNT(*) FROM name) FROM sqlite_master WHERE type='table';

-- FK check global
PRAGMA foreign_key_check;

-- Duplicados en users
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

-- Estados válidos
SELECT * FROM repair_statuses ORDER BY sort_order;

-- Usuarios activos
SELECT id, username, email, role_id, is_active FROM users;

-- Clientes
SELECT id, name, email, user_id FROM clients;
```

---

*Auditoría con esquema real verificado - ADITIVO NO DESTRUCTIVO*
*Generado: 2026-01-21*
*Método: Queries SQL compatibles con schema actual*
