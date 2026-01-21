# AUDITORIA EXHAUSTIVA DE BASE DE DATOS

**Fecha:** 2026-01-21
**Base de datos:** `backend/cirujano.db`
**Tamaño:** 675,840 bytes

---

## 1. INVENTARIO DE TABLAS

### 1.1 Total de Tablas
**56 tablas** en total (incluyendo 3 vistas)

### 1.2 Tablas con Datos (ordenadas por volumen)

| Tabla | Registros | Descripcion |
|-------|-----------|-------------|
| comp_integrated_circuits | 173 | Circuitos integrados |
| comp_resistors | 168 | Resistencias |
| comp_transistors | 112 | Transistores |
| comp_capacitors | 93 | Capacitores |
| audit_logs | 30 | Logs de auditoria |
| comp_diodes | 28 | Diodos |
| device_brands | 14 | Marcas de dispositivos |
| tool_brands | 12 | Marcas de herramientas |
| device_types | 10 | Tipos de dispositivos |
| repair_statuses | 9 | Estados de reparacion |
| tool_categories | 7 | Categorias de herramientas |
| storage_locations | 6 | Ubicaciones de almacen |
| user_roles | 3 | Roles de usuario |
| products | 3 | Productos |
| users | 2 | Usuarios |
| clients | 2 | Clientes |
| categories | 2 | Categorias |
| newsletter_subscriptions | 1 | Suscripciones newsletter |
| appointments | 1 | Citas |
| alembic_version | 1 | Version migraciones |

### 1.3 Tablas Vacias (0 registros)

```
repairs, devices, invoices, payments, quotes, warranties, warranty_claims,
repair_notes, repair_photos, permissions, roles, role_permissions, tools,
stock, stock_movements, brands, diagnostics, contact_messages,
comp_cables, comp_chassis_hardware, comp_connectors, comp_consumables,
comp_displays, comp_inductors, comp_mechanical, comp_potentiometers,
comp_power_modules, comp_switches, comp_transformers, instruments,
invoice_items, invoice_sequences, repair_component_usage, repair_tool_usage,
tool_maintenance, user_role_assignments
```

---

## 2. INTEGRIDAD DE DATOS

### 2.1 Campos Obligatorios

| Check | Resultado |
|-------|-----------|
| Users sin email | 0 (OK) |
| Clients sin name | 0 (OK) |

### 2.2 Datos de Usuarios

| ID | Username | Email | Role ID | Activo |
|----|----------|-------|---------|--------|
| 1 | admin | admin@cirujanodesintetizadores.cl | 1 | 1 |
| 2 | testuser_5010f99f | testuser_5010f99f@example.com | 3 | 1 |

### 2.3 Datos de Clientes

| ID | Nombre | Email | Telefono |
|----|--------|-------|----------|
| 1 | Test User | testuser_5010f99f@example.com | +56911111111 |
| 2 | Cristóbal Zurita | admin@cirujanodesintetizadores.cl | +56982957538 |

---

## 3. FOREIGN KEYS

### 3.1 Verificacion PRAGMA

```
PRAGMA foreign_key_check: (vacío - sin errores)
```

### 3.2 Cruces de FK

| Check | Resultado |
|-------|-----------|
| Repairs sin device valido | 0 (OK) |
| Devices sin client valido | 0 (OK) |
| Invoices sin client valido | 0 (OK) |
| Payments sin repair valido | 0 (OK) |
| Warranty_claims sin warranty | 0 (OK) |

---

## 4. DUPLICADOS

| Check | Resultado |
|-------|-----------|
| Emails duplicados en users | 0 (OK) |
| Emails duplicados en clients | 0 (OK) |
| Repair_number duplicados | 0 (OK) |
| Invoice_number duplicados | 0 (OK) |

---

## 5. ESTADOS INVALIDOS

| Check | Resultado |
|-------|-----------|
| Repairs con status_id invalido | 0 (OK) |
| Appointments con estado invalido | 0 (OK) |
| Users con role_id invalido | 0 (OK) |

### 5.1 Estados de Reparacion Disponibles

| ID | Codigo | Nombre |
|----|--------|--------|
| 1 | pending_quote | Pendiente Cotización |
| 2 | quoted | Cotizado |
| 3 | approved | Aprobado |
| 4 | in_progress | En Proceso |
| 5 | waiting_parts | Esperando Repuestos |
| 6 | testing | En Pruebas |
| 7 | completed | Completado |
| 8 | delivered | Entregado |
| 9 | cancelled | Cancelado |

---

## 6. CATALOGO DE COMPONENTES

| Tipo | Cantidad |
|------|----------|
| Resistencias | 168 |
| Capacitores | 93 |
| Circuitos Integrados | 173 |
| Transistores | 112 |
| Diodos | 28 |
| **TOTAL** | **574** |

---

## 7. RESUMEN EJECUTIVO

### Estado General: **LIMPIO**

| Categoria | Errores |
|-----------|---------|
| FK Rotas | 0 |
| Duplicados | 0 |
| Estados Invalidos | 0 |
| Nulos en Obligatorios | 0 |

### Observaciones

1. **Base de datos en estado inicial**: Mayoría de tablas operativas vacías (repairs, devices, invoices, etc.)
2. **Catálogo de componentes poblado**: 574 componentes electrónicos listos para uso
3. **Sistema de usuarios funcional**: 2 usuarios (admin + test)
4. **Sistema de clientes funcional**: 2 clientes
5. **Estados de reparación configurados**: 9 estados en flujo correcto
6. **Auditoría activa**: 30 registros de audit_logs

### Recomendaciones

1. **Datos de prueba**: Considerar crear reparaciones de ejemplo para testing
2. **Permisos**: Tabla `permissions` vacía - ejecutar seed si se requiere RBAC
3. **Roles**: Tabla `roles` vacía pero `user_roles` tiene 3 registros - verificar mapeo

---

## 8. QUERIES DE VERIFICACION

```sql
-- Inventario rápido
SELECT name, (SELECT COUNT(*) FROM pragma_table_info(name)) AS cols
FROM sqlite_master WHERE type='table';

-- FK check
PRAGMA foreign_key_check;

-- Duplicados
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

-- Estados válidos
SELECT code, name FROM repair_statuses;
```

---

*Auditoria automatica - ADITIVO NO DESTRUCTIVO*
*Generado: 2026-01-21*
