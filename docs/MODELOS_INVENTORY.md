# MODELOS inventory & integration plan

Resumen breve: revisé la carpeta `MODELOS` y encontré varios proyectos útiles como **Stock-App**, **vue-manage-system**, y **FixitFastRepairs**. Abajo detallo por proyecto lo que contiene, lo reutilizable, incompatibilidades potenciales y una propuesta de pasos para integrar piezas al POC `InventoryCard` y al frontend actual.

---

## 1) Stock-App / stock-app-main
- Tech: Vue 3, Vite, **Vuex**, TailwindCSS, Axios
- Qué hay: CRUD de productos, categorías, búsquedas, formularios de producto, subida de imágenes, UI de lista/tabla y tarjetas de producto.
- Útil para: UX de inventario (lista, filtros, búsqueda por categoría/keyword), ejemplos de formularios y validación, diseño de flujo CRUD.
- Conflictos: usa **Vuex** (nuestro proyecto usa **Pinia**) y **Tailwind** (nuestro proyecto usa **Bootstrap**). Requiere adaptar store lógica y/o convertir estilos o aislar componentes con CSS adaptador.
- Licencia: no explícita en package.json; verificar antes de copiar código literalmente.

## 2) vue-manage-system
- Tech: Vue 3, TypeScript, Vite, **Pinia**, Element Plus, xlsx
- Qué hay: plantilla de admin completa (tablas, formularios, layouts, componentes reutilizables), soporte para xlsx (útil para importación/validación) y uso de Pinia.
- Útil para: patrones de store + componentes admin, tablas avanzadas, ejemplos de carga/descarga Excel, estructura de permisos UI.
- Conflictos: usa **Element Plus** (UI kit) y TypeScript — puede integrarse más fácilmente por el uso de **Pinia** pero requerirá estilo / CSS harmonization.

## 3) FixitFastRepairs
- Tech: Vue 3, Vite (cliente + server)
- Qué hay: aplicación de reparaciones con pantallas, modales y flujos de trabajo (trabajos, partes, interacciones con piezas)
- Útil para: interacciones modal/UX relativas a selección de piezas, workflows, y examples de arquitectura cliente/servidor.
- Conflictos: ligero; útil más como referencia para widgets que para código directo.

## Otros proyectos (menor prioridad)
- Geeker-Admin, fullcalendar-vue, inventory-system-master, laravel templates: pueden aportar ideas o backends de referencia, pero no son prioridad para `InventoryCard` POC.

---

## Evaluación general y recomendaciones
- Prioridad para POC: **1) vue-manage-system** (Pinia + admin patterns) y **2) Stock-App** (UX/CRUD examples). Combinar: usar vue-manage-system para layout/store patterns y Stock-App para UX de inventario.
- Riesgos: diferencias en UI kits (Bootstrap vs Tailwind vs Element), posible falta de licencia (verificar), y coste de portar Vuex->Pinia y/o TS->JS.
- Reglas a seguir: no copiar sin verificar licencia; preferir adaptación (re-implementar patrones y tests) en vez de verbatim copy.

---

## Concrete next steps (minimal, ordered)
1. Verificar licencias de los proyectos candidatos (Stock-App, vue-manage-system, FixitFastRepairs). Añadir nota de aceptación/contestación a la PR si hay restricciones.
2. Probar extraer el componente de UI más pequeño (Inventory Card) del Stock-App: identificar componentes → portar markup → adaptar estilos a Bootstrap y Pinia → añadir unit test. (Small PR)
3. Alternativa: construir InventoryCard usando patrones de `vue-manage-system` (Pinia + Element/TS) si decidimos adoptar Element o TypeScript para el área admin.
4. Actualizar `docs/` con mapping de archivos a portar y estimación de esfuerzo.

---

## What is missing in the repo to make this low-friction
- License checks and attribution notes para código reutilizado
- Una pequeña capa adaptadora para estilos (Tailwind → Bootstrap) o decidir adoptar Tailwind para el admin area
- Decisión técnica: usar Element Plus (y TS) para admin o mantener Bootstrap y portar componentes
- CI job que haga build mínimo de PRs para detectar rupturas temprano

---

Si confirmas, verifico las licencias y preparo el **mini-POC** (portar `InventoryCard` desde Stock-App o implementar con patterns de vue-manage-system). Indica cuál repo quieres usar como fuente primaria.
