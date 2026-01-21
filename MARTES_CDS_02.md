# MARTES_CDS_02 - Informe extendido + Plan + Prompt

## 1) Diagnostico detallado (Front + Back)

### Backend
- Permisos granulares: presentes en la mayoria de routers; revisar que todos los endpoints sensibles usen require_permission.
- Quotes en diagnostic: endpoints implementados, pero hay posible solapamiento con quotation.py (evitar duplicidad de logica).
- Migraciones Alembic: cadena correcta pero falta evidencia formal (captura de `alembic heads/history`).
- Seed de permisos: existe, pero falta ejecucion documentada y verificacion de roles creados.
- Pruebas: no hay coleccion API versionada ni tests automatizados para endpoints criticos.

### Frontend
- UI de calculadoras operativa; faltan reportes unicos de estado UI/UX.
- TODO aspiracional: PDF en DiagnosticWizard (CSV ya funciona).
- Riesgo: multiples reportes historicos crean confusion (unificar doc vigente).

### Operacion
- Falta evidencia ejecutada (logs de pruebas reales).
- Falta checklist unico de despliegue/validacion runtime.

## 2) Plan de accion (pasos concretos)
1) **Evidencia de seguridad**
   - Ejecutar seed de permisos y capturar salida.
   - Verificar endpoints con token real (listado de rutas criticas).
2) **Evidencia de migraciones**
   - Guardar salida de `alembic heads` y `alembic history` en reporte tecnico.
3) **Pruebas API**
   - Crear coleccion Postman/HTTP con 10 endpoints criticos.
   - Guardar ejemplos de request/response JSON.
4) **Frontend**
   - Definir documento unico de estado UI (pantallas reales vs planificadas).
5) **Mejora opcional**
   - Implementar export PDF en DiagnosticWizard manteniendo CSV.

## 3) Prompt operativo (uso directo)
```
Usa como base los reportes actuales del proyecto y contrasta con el estado real del codigo.
Aplica mejoras de forma 100% ADITIVA (no borrar ni romper nada).

Objetivo:
- Validar permisos granulares en routers.
- Generar evidencia tecnica (alembic heads/history + pruebas API).
- Consolidar un reporte unico de estado real.

Reglas:
- No tocar modelos ni migraciones salvo error critico.
- Si un punto ya esta resuelto, solo documentarlo.
- Si hay contradicciones entre reportes, prioriza el codigo real.

Salida:
- Lista de pendientes confirmados.
- Evidencias (comandos + resultados).
- Nuevo reporte consolidado en raiz.
```

## 4) Indicadores de cierre
- 0 endpoints sin permisos granulares.
- Seed de permisos ejecutado y documentado.
- Reporte unico con evidencia tecnica en raiz.
- 1 solo TODO aspiracional (PDF) o implementado.