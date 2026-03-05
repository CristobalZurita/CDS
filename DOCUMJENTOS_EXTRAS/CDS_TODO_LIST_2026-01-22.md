# CDS TODO LIST

Actualizado al estado real del repo al `2026-03-01`.

Este documento no repite lo que ya funciona bien.  
Lista sólo brechas, incoherencias o piezas incompletas respecto de lo esperado por `CDS_DOCUMENTO.pdf`, el repo actual y el flujo real del proyecto.

## 1. Cotizador inteligente incompleto

### Qué falta

- El flujo público no está cerrado de punta a punta como cotizador inteligente real.
- La parte "IA" sigue siendo mayormente placeholder.
- No está validado de forma integral el paso final de generación/persistencia de una cotización completa lista para uso real.

### Evidencia

- [CotizadorIAPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/CotizadorIAPage.vue)
- [useQuotation.js](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/composables/useQuotation.js)
- [quotation.spec.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/e2e/quotation.spec.ts)
- [ai_detector.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/services/ai_detector.py)
- [image_analysis.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/services/image_analysis.py)

### Por qué falta

- El backend actual de análisis está planteado como base/placeholder y no como motor terminado.
- Los tests públicos cubren avance de pasos y consistencia básica, pero no prueban una cotización final inteligente completa con todos sus resultados de negocio.

### Cómo aplicarlo sin romper

- Mantener el flujo actual de UI y endpoints existentes.
- Reemplazar la lógica placeholder detrás de los servicios actuales, sin abrir un segundo sistema paralelo.
- Extender pruebas sobre el flujo actual hasta generación final, guardado y recuperación de la cotización.

## 2. Calculadoras con cobertura superficial

### Qué falta

- Las calculadoras cargan y sus rutas existen, pero no todas tienen validación funcional profunda de sus resultados.
- No está demostrado con test que cada botón, fórmula y resultado numérico sea correcto en cada calculadora.

### Evidencia

- [routes.spec.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/tests/e2e/routes.spec.ts)

### Por qué falta

- La cobertura actual asegura carga de ruta y ausencia de rotura visible.
- No hay todavía una batería matemática/funcional completa por calculadora.

### Cómo aplicarlo sin romper

- Agregar tests por calculadora sobre la implementación actual.
- Validar inputs, resultados esperados, estados vacíos y errores, sin rediseñar las pantallas.

## 3. Captcha real no validado en flujo local real

### Qué falta

- El login funciona, pero en el entorno local de trabajo el captcha está deshabilitado.
- Eso permite probar acceso, pero no valida el flujo real de Turnstile con claves reales.

### Evidencia

- [TurnstileWidget.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/widgets/TurnstileWidget.vue)
- [auth.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/api/v1/endpoints/auth.py)
- [backend/.env](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/.env)

### Por qué falta

- El entorno actual privilegia pruebas y desarrollo.
- No hay una validación local o staging documentada del captcha real extremo a extremo.

### Cómo aplicarlo sin romper

- Mantener bypass sólo para test/desarrollo controlado.
- Validar el flujo real en staging o entorno preparado con claves válidas.
- No cambiar el formulario ni duplicar lógica de auth.

## 4. WhatsApp no operativo en el entorno actual

### Qué falta

- El proyecto contempla notificaciones por WhatsApp, pero el canal no está operativo en el entorno probado.

### Evidencia

- [whatsapp_service.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/services/whatsapp_service.py)

### Por qué falta

- En la corrida real de pruebas quedó deshabilitado por dependencia/configuración incompleta.
- Hoy el canal activo comprobado es correo; WhatsApp no quedó validado de forma equivalente.

### Cómo aplicarlo sin romper

- Completar dependencias y variables del servicio actual.
- Mantener fallback silencioso/no destructivo cuando el canal no esté configurado.
- No crear un segundo sistema de notificaciones.

## 5. Tienda pública, carrito y checkout no existen como flujo real del sitio actual

### Qué falta

- No hay página de tienda pública operativa integrada al sitio actual.
- No existe checkout real ni carrito conectado al backend actual.
- No hay pagos online de tienda integrados.

### Evidencia

- [index.ts](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/router/index.ts)
- [AUDITORIA_ENDPOINTS_CHECKLIST.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/DOCUMJENTOS_EXTRAS/AUDITORIA_ENDPOINTS_CHECKLIST.md)
- [mi-proyecto/package.json](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/mi-proyecto/package.json)

### Por qué falta

- `mi-proyecto` contiene lógica útil de front en JavaScript, pero trabaja como demo/flujo local y no como comercio conectado al backend real.
- El repo principal no expone hoy rutas públicas de tienda, carrito ni checkout equivalentes.

### Cómo aplicarlo sin romper

- Deconstruir `mi-proyecto` para rescatar reglas de carrito, envío y UX.
- Reusar la lógica que sirva, pero conectándola a modelos/endpoints reales del proyecto actual.
- No copiar y pegar DOM/manual JS como sistema final.
- Montarlo como extensión del sitio actual, no como segundo front paralelo.

### Qué parte de `mi-proyecto` sí se puede reutilizar

- Normalización de cantidades y límites por producto.
- Cálculo de subtotal, total, envío y cantidad de ítems.
- Persistencia local del carrito en `localStorage`.
- Selección de envío y actualización reactiva del resumen.
- UX de tarjetas, drawer de carrito, estado vacío y feedback al agregar/quitar.

### Qué parte de `mi-proyecto` no se puede copiar y pegar literal

- Catálogo hardcodeado de productos Mario.
- Generación local de números de orden.
- Checkout local que hoy sólo persiste una orden falsa en `localStorage`.
- Manipulación directa del DOM con `onclick`, `innerHTML`, `querySelector`.
- HTML standalone como sistema final dentro del repo principal.

### Cómo se proyecta al backend real

- **Catálogo**: usar `products` + `stock` como fuente de verdad, no el arreglo `products[]` de `mi-proyecto`.
- **Estado del carrito**: rearmarlo en Vue/Pinia sobre el front actual, conservando la lógica útil de sumatorias, cantidades y persistencia local.
- **Envío**: mantener reglas simples de selección/costo en front mientras no exista cálculo de despacho real en backend.
- **Checkout**: no simular orden real hasta tener endpoint/flujo real. Primero catálogo + carrito; después solicitud/orden; luego pago.
- **Imágenes**: usar `image_url` y catálogo real; si faltan imágenes, no falsear fotos comerciales que no existen en la BD operativa.
- **Pagos**: conectar después sobre la capa actual de `payments`/`purchase_requests`, no inventar una pasarela paralela.

### Orden correcto de integración de `mi-proyecto`

1. Exponer catálogo público real desde `products`.
2. Montar página pública de tienda en el front actual.
3. Reusar lógica de carrito y envío en Vue.
4. Agregar creación real de solicitud/orden en backend.
5. Integrar pago real sobre esa orden, no antes.

## 6. Pagos online reales no integrados

### Qué falta

- No hay integración comprobada con pasarela real de pago web para tienda o pago general online.
- El flujo actual de pagos está más orientado a comprobantes, registros internos o pagos asociados a OT, no a e-commerce completo con gateway.

### Evidencia

- [payments.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers/payments.py)
- [purchase_requests.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers/purchase_requests.py)

### Por qué falta

- No aparece pasarela real integrada ni validada con webhook/confirmación.
- El propio `CDS_DOCUMENTO.pdf` lo deja como área proyectada/incompleta.

### Cómo aplicarlo sin romper

- Conservar el modelo actual de pagos/OT.
- Añadir adaptador de pasarela sobre la capa existente, no por fuera.
- Definir si el pago online será de OT, tienda, repuestos o ambos antes de conectar.

## 7. Importación e inventario unificado todavía no están cerrados como flujo único de producción

### Qué falta

- La base de inventario existe y hay CRUD.
- Pero la importación/unificación masiva sigue mostrando señales de POC y no de pipeline final totalmente unificado a la BD operativa principal.

### Evidencia

- [InventoryUnified.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/views/InventoryUnified.vue)
- [imports.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/api/v1/endpoints/imports.py)

### Por qué falta

- La vista misma se declara como POC.
- El endpoint de importación sigue trabajando con una base/flujo separado de la ruta operativa principal.

### Cómo aplicarlo sin romper

- Mantener el inventario principal actual.
- Redirigir la importación masiva hacia la misma ruta/modelo/BD operativa que usa el CRUD real.
- No sostener dos verdades distintas del inventario.

## 8. Sincronización automática de fotos e instrumentos no cubre todavía una tienda comercial completa

### Qué falta

- Sí existe sincronización de catálogo/instrumentos/fotos.
- No está cerrada la parte comercial donde eso genere automáticamente todas las tarjetas/páginas de tienda/repuestos para venta pública.

### Evidencia

- [uploads.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/routers/uploads.py)
- [instrument_sync_service.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/services/instrument_sync_service.py)

### Por qué falta

- La automatización actual resuelve catálogo interno y relación con instrumentos, no un sistema de e-commerce completo.

### Cómo aplicarlo sin romper

- Reusar el pipeline actual de sync como fuente de verdad.
- Construir encima el mapeo hacia productos/comercio, sin duplicar carga de imágenes ni catálogos.

## 9. Flujo completo UI de intake multi-instrumento + OT + materiales no está cubierto extremo a extremo

### Qué falta

- La lógica backend y varias piezas de UI existen.
- Falta asegurar con una prueba E2E profunda el recorrido completo desde intake admin hasta creación agrupada de OT, materiales y seguimiento final.

### Evidencia

- [test_ot_workflow.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/tests/test_ot_workflow.py)
- [ot_code_service.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/services/ot_code_service.py)
- [UnifiedIntakeForm.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/UnifiedIntakeForm.vue)
- [RepairComponentsManager.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/components/admin/repair/RepairComponentsManager.vue)
- [RepairDetailAdminPage.vue](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src/vue/content/pages/admin/RepairDetailAdminPage.vue)

### Por qué falta

- Las piezas están, pero no todo el recorrido está asegurado como una sola historia de negocio por test UI profundo.

### Cómo aplicarlo sin romper

- Crear una sola suite profunda sobre la UI actual.
- Cubrir cliente con varios instrumentos, separación por OT, materiales asociados y stock descontado.
- No reescribir formularios ni modelos para testearlo.

## 10. PDF/documentos finales todavía están parciales según lo prometido por la documentación

### Qué falta

- Existen PDFs y documentos de cierre/OT.
- No está completamente claro/cerrado el conjunto documental prometido en la narrativa más ambiciosa del proyecto, especialmente para cotización comercial y flujos asociados.

### Evidencia

- [pdf_generator.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/app/services/pdf_generator.py)

### Por qué falta

- La base actual está orientada a documentos de reparación/cierre.
- No está consolidado un mapa documental completo para cotización, venta, cierre y comprobantes.

### Cómo aplicarlo sin romper

- Extender el servicio PDF actual.
- No crear un generador PDF paralelo.
- Definir primero qué documentos faltan realmente en el ciclo de negocio y recién luego implementarlos.

## 11. El documento `CDS_DOCUMENTO.pdf` mezcla estado actual con estado proyectado

### Qué falta

- Falta separar claramente qué está implementado hoy y qué está sólo proyectado.

### Evidencia

- [CDS_DOCUMENTO.pdf](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/CDS_DOCUMENTO.pdf)

### Por qué falta

- El documento presenta parte del sistema real, pero también mezcla aspiraciones o arquitectura no totalmente visible/operativa hoy.
- Eso puede confundir al explicar el proyecto.

### Cómo aplicarlo sin romper

- Mantener el documento como visión general si sirve.
- Crear o actualizar una versión ejecutiva separando:
  - implementado hoy
  - parcialmente implementado
  - proyectado

## 12. Testing fuerte, pero todavía no total sobre todos los botones y ramas de negocio

### Qué falta

- La cobertura actual es sólida en rutas, auth, CRUD, flujos críticos y smoke general.
- No equivale a validación exhaustiva de cada botón, cada CTA, cada enlace externo y cada rama de negocio del sitio entero.

### Evidencia

- [TESTING.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/TESTING.md)
- [TESTING_COVERAGE_MATRIX.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/TESTING_COVERAGE_MATRIX.md)
- [TESTING_STATUS_BRIEF.md](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/docs/TESTING_STATUS_BRIEF.md)

### Por qué falta

- Eso requiere ampliar casos específicos de negocio, no sólo smoke y CRUD.

### Cómo aplicarlo sin romper

- Priorizar por riesgo:
  - cotizador
  - intake profundo
  - calculadoras
  - pagos
  - tienda cuando exista

## Orden recomendado de trabajo

1. Cerrar cotizador inteligente real.
2. Unificar importación/inventario con la BD operativa principal.
3. Definir e implementar tienda/carrito/checkout real usando `mi-proyecto` sólo como base lógica.
4. Integrar pagos online reales sobre la capa existente.
5. Reactivar y validar WhatsApp real.
6. Completar E2E profundo de intake multi-instrumento y calculadoras.
7. Ajustar `CDS_DOCUMENTO.pdf` o su equivalente ejecutivo para separar realidad actual de proyección.
