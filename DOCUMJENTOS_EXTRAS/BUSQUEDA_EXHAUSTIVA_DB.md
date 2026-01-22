# BUSQUEDA_EXHAUSTIVA_DB.md

## Objetivo
Ejecutar una auditoria real de la base de datos para detectar:
- Que hay (inventario de tablas y volumen de datos)
- Que falta (nulos/obligatorios)
- Incongruencias (FK rotas, estados invalidos, duplicados)

## Requisitos
- Base de datos local: `backend/cirujano.db`
- Herramienta: `sqlite3` disponible en el sistema

## Paso 1: Inventario (que hay)
```bash
sqlite3 backend/cirujano.db ".tables"
sqlite3 backend/cirujano.db "SELECT name FROM sqlite_master WHERE type='table';"
sqlite3 backend/cirujano.db "SELECT 'users' AS tabla, COUNT(*) FROM users;"
sqlite3 backend/cirujano.db "SELECT 'clients' AS tabla, COUNT(*) FROM clients;"
sqlite3 backend/cirujano.db "SELECT 'repairs' AS tabla, COUNT(*) FROM repairs;"
```

## Paso 2: Integridad (que falta)
```bash
sqlite3 backend/cirujano.db "SELECT id FROM users WHERE email IS NULL OR email = '';"
sqlite3 backend/cirujano.db "SELECT id FROM clients WHERE name IS NULL OR name = '';"
```

## Paso 3: Incongruencias (FK rotas)
```bash
sqlite3 backend/cirujano.db "PRAGMA foreign_key_check;"
sqlite3 backend/cirujano.db "SELECT r.id FROM repairs r LEFT JOIN clients c ON c.id = r.client_id WHERE c.id IS NULL;"
```

## Paso 4: Duplicados
```bash
sqlite3 backend/cirujano.db "SELECT email, COUNT(*) c FROM users GROUP BY email HAVING c > 1;"
```

## Paso 5: Estados invalidos
```bash
sqlite3 backend/cirujano.db "SELECT id, status FROM repairs WHERE status NOT IN ('pending','in_progress','completed','cancelled');"
```

## Paso 6: Cruces de negocio
```bash
sqlite3 backend/cirujano.db "SELECT p.id FROM payments p LEFT JOIN invoices i ON i.id = p.invoice_id WHERE p.invoice_id IS NOT NULL AND i.id IS NULL;"
```

## Resultado esperado
- Listado de incongruencias con IDs concretos.
- Lista de tablas con volumen real.
- Evidencia de limpieza (0 resultados en queries de error).