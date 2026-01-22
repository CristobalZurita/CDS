# AUDITORIA MODELOS (CARPETA MODELOS)
**Fecha:** 2026-01-21
**Ruta:** `/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/MODELOS`

---

## Resultado General
- Los directorios en `MODELOS/` **no contienen código fuente listo para aplicar** (no hay `src/`, `package.json` ni README).
- Hay principalmente **assets sueltos** (fonts, dist, build) y carpetas `storage` vacías.
- Esto impide “aplicar lo que ya está resuelto” porque **faltan los fuentes**.

---

## Estado por carpeta

- `Appointment-Booking-System-main/` → solo `storage/`.
- `Appointment-Booking-System-master/` → solo `.vscode/` y `storage/`.
- `Geeker-Admin-master/` → solo `.env`, `.vscode/`, `build/`.
- `Stock-App-master/` → solo `.vscode/`.
- `stock-app-main/` → solo `.vscode/`.
- `inventory-system-master/` → assets de `semantic` y build estáticos (sin app).
- `fullcalendar-vue-main/` → solo `.vscode/`.
- `qalendar-master/` → solo `.vscode/`.
- `vue-cal-main/` → solo `dist/` (bundle, sin fuentes).
- `vue-stripe-main/` → contiene algunos `.ts` sueltos (no app completa).
- `laravel-inertia-vue-main/` → sin fuentes visibles.
- `laravel-tickets-master/` → solo `resources/js/lib` (utilidades, no app completa).

---

## Conclusion
Actualmente **no hay modelos completos** para reutilizar “tal cual”.
Si quieres aplicar esos modelos, necesitamos **las versiones completas** (con `src/`, `package.json`, etc.).

---

## Accion sugerida
- Proveer los repos completos o exportar los `src/` originales.
- Luego evaluamos integración con este proyecto.
