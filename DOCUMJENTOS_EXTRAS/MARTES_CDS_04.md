# MARTES_CDS_04 - Informe ultra tecnico (routers/endpoints + ciberseguridad + manual + pendientes)

## 1) Inventario tecnico (routers/endpoints)
- Revisar routers en `backend/app/routers/*.py`.
- Verificar que cada endpoint sensible tenga `require_permission` aplicado.
- Confirmar con: `grep -r "require_permission" backend/app/routers/`

## 2) Permisos granulares (detalle)
- Estado actual: permisos aplicados ampliamente; confirmar en endpoints criticos.
- Checklist por router: read/create/update/delete + acciones especiales (void, export, claims, calibrate).

## 3) Ciberseguridad (nivel aplicacion)
### 3.1 Autenticacion
- Verificar login JWT (token) y expiracion.
- Validar que endpoints protegidos rechacen token invalido.

### 3.2 Autorizacion
- Confirmar que todos los endpoints sensibles usan permisos granulares.
- Confirmar seed de roles y permisos ejecutado en DB real.

### 3.3 Superficie de ataque
- Revisar uploads y sanitizacion de archivos.
- Revisar CORS en backend (configuracion de origenes permitidos).
- Validar rate limiting si existe (slowapi).

### 3.4 HTTPS/SSL
- SSL/HTTPS se maneja en el hosting (no en el codigo).
- Verificar en el panel del hosting: certificado activo, redireccion HTTP->HTTPS.

## 4) Manual de uso de la web
- No se detecta un manual unico en el repo.
- Posibles referencias: `MANUAL_CIRUJANO.pdf`, `README.md`, `QUICK_START.md`.
- Recomendacion: crear un documento unificado con flujos clave (login, calculadoras, admin, citas).

## 5) Que buscar (bueno/malo)
### Bueno
- Permisos granulares aplicados.
- Endpoints criticos implementados (diagnostic/quotes).
- Frontend funcional sin imports rotos.

### Malo / Pendiente
- Falta evidencia ejecutada (logs de pruebas reales).
- Falta manual unico de uso de la web.
- Falta export PDF en DiagnosticWizard (opcional).
- Documentacion dispersa y reportes contradictorios.

## 6) Como generar pendientes (metodologia)
1) Recolectar evidencia tecnica (grep, alembic heads, respuestas API).
2) Marcar gaps: endpoints sin permisos, TODOs, rutas sin UI.
3) Convertir gaps en tareas con prioridad y riesgo.

## 7) Plan de accion (corto plazo)
1) Ejecutar seed de permisos y documentar salida.
2) Crear checklist de endpoints y registrar respuestas reales.
3) Consolidar manual de uso en un solo documento.
4) Revisar CORS/SSL y documentar configuracion real del hosting.
5) Implementar export PDF en DiagnosticWizard si es necesario.

## 8) Prompt operativo (copia y usa)
```
Audita el backend y frontend con foco en seguridad, permisos y endpoints.
Documenta evidencias reales (grep, alembic heads, respuestas API).
Genera un reporte unico con: lo bueno, lo malo, pendientes, plan de accion.
No borres ni rompas nada. Todo aditivo.
```