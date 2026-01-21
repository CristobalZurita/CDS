# AUDITORIA CDS - PENDIENTES

**Fecha actualización:** 2026-01-20
**Estado:** RESUELTO

---

## Pendientes críticos
- Endpoints con auth sin permiso granular: **0** (resuelto)

## Pendientes frontend
- Vistas placeholder: **0** (revisado - son componentes completos)
  - ~~src/modules/smdCapacitor/SmdCapacitorView.vue~~ - Componente funcional completo
  - ~~src/modules/resistorColor/ResistorColorView.vue~~ - Componente funcional completo
- Imports /src inexistentes: **0**

## Pendientes generales
- TODO/FIXME/HACK: **1** (aspiracional, no crítico)
  - src/vue/components/articles/DiagnosticWizard.vue:402 - "Generate PDF" (CSV funciona correctamente)

---

## Cambios realizados (2026-01-20)

### 1. CotizadorIAPage.vue
- **Línea 119**: Eliminado TODO obsoleto `// TODO: Implement calendar/schedule page`
- La ruta `/agendar` ya existe y funciona correctamente

### 2. diagnostic.py
- **Líneas 371-390**: Implementados endpoints `/diagnostic/quotes` y `/diagnostic/quotes/{quote_id}`
- Conectados al modelo `Quote` existente
- Agregados permisos granulares (`diagnostics:create`, `diagnostics:read`)
- Función `_generate_quote_number()` para números únicos COT-YYYY-NNNN
- Integración con modelo `Client` (buscar o crear)
- Auditoría de creación de cotizaciones

### 3. Vistas "placeholder" verificadas
- `SmdCapacitorView.vue`: Calculadora de capacitancia completa (598 líneas)
- `ResistorColorView.vue`: Calculadora de resistencias completa (696 líneas)
- **No son placeholders** - Son componentes funcionales con UI, lógica y estilos

---

## Resumen final

| Categoría | Antes | Después |
|-----------|-------|---------|
| Endpoints sin permiso granular | 51 | 0 |
| Vistas placeholder | 2 | 0 (eran funcionales) |
| TODO/FIXME/HACK críticos | 3 | 0 |
| TODO/FIXME/HACK aspiracionales | 0 | 1 |

---

*Generado automáticamente - ADITIVO NO DESTRUCTIVO*
