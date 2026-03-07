# CDS Vue 3 Zero

Reconstrucción de frontend Vue 3 desde cero en carpeta separada.

## 1) Referentes y alcance
- Referente funcional completo (legacy): `/tmp/CDS_VIEJA`
- Proyecto nuevo (este): `/tmp/CDS_VUE3_ZERO`
- Fuente legacy usada por alias: `/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/src`
- Regla: aditivo/deconstructivo, sin inventar contratos de datos ni rutas.

## 2) Estado actual (hecho)
1. Estructura base nueva creada:
   - `src/app`, `src/layouts`, `src/pages`, `src/router/routes`, `src/components`, `src/stores`, `src/composables`, `src/services`, `src/styles`.
2. Router nuevo modular creado con paridad de paths/names respecto a legacy.
3. Base de estilos inicial creada (`tokens/typography/layout/utilities/main`).
4. Fase Auth implementada en Vue real (sin wrapper legacy en páginas auth):
   - `src/components/auth/LoginForm.vue`
   - `src/components/auth/RegisterForm.vue`
   - `src/components/auth/PasswordResetForm.vue`
   - `src/pages/auth/LoginPage.vue`
   - `src/pages/auth/RegisterPage.vue`
   - `src/pages/auth/PasswordResetPage.vue`
5. Componentes UI base implementados:
   - `src/components/ui/BaseInput.vue`
   - `src/components/ui/BaseButton.vue`
6. Mejoras Vue aplicadas en Auth:
   - `v-model.trim` en campos clave.
   - Validación reactiva con `computed + watch`.
   - Composable dedicado: `src/composables/useAuthForms.js`.
   - `BaseInput` con soporte de modifiers (`trim/number`) y slots (`prefix/suffix`).
   - `BaseButton` con slots (`prefix/suffix`) y validación básica de `emits`.
7. Inicio de Fase Public (sin wrapper de página legacy):
   - `src/pages/public/TermsPage.vue` migrada a implementación Vue real + composable (`useTermsPage`).
   - `src/pages/public/PrivacyPage.vue` migrada a implementación Vue real + composable (`usePrivacyPage`).
   - `src/pages/public/LicensePage.vue` migrada a página Vue real usando composable (`useLicensePage`).
   - `src/pages/public/PolicyPage.vue` migrada a página Vue real usando composable (`usePolicyPage`).
   - `src/pages/public/CalculatorsPage.vue` migrada a implementación Vue real + composable (`useCalculatorsPage`).
8. Desacople adicional aplicado (eliminando dependencia puntual de `@legacy`):
   - Nuevo widget local: `src/components/widgets/TurnstileWidget.vue`.
   - Auth actualizado para usar widget local:
     - `src/components/auth/LoginForm.vue:69`
     - `src/components/auth/RegisterForm.vue:29`
   - Se eliminó `@legacy` en 4 páginas públicas legales + 4 composables legales.

## 3) Qué falta y orden obligatorio
1. **Auth (cerrar)**
   - Ejecutar validación runtime completa login/register/reset con backend real.
   - Ajustar detalles de UX según resultados de prueba real (si aparecen).
2. **Public**
   - Reemplazar wrappers restantes de páginas públicas por implementación nueva.
   - Montar navegación/sections preservando rutas y anchors funcionales.
3. **Client**
   - Dashboard, repairs, repair detail, profile, pagos OT.
   - Mantener contratos actuales de stores/composables.
4. **Admin**
   - Migración por módulos: inventory, clients, repairs, quotes, tickets, stats, wizards.
   - Evitar cambios masivos; avanzar por submódulo verificable.
5. **Calculadoras**
   - Reemplazo de wrappers por vistas nuevas sin cambiar comportamiento matemático.
6. **Token flows**
   - Signature + photo upload (rutas y payloads intactos).
7. **QA de paridad**
   - Navegación, rutas rotas, formularios, auth guards y flows críticos.
8. **Documentación final**
   - Actualizar este README con estado final, gaps, y checklist de traspaso.

## 4) Política de actualización del README
- Este archivo se actualiza al final de cada fase ejecutada.
- Debe responder siempre:
  1. Qué se hizo.
  2. Qué falta.
  3. En qué orden exacto sigue.
  4. Riesgos abiertos.

## 5) Riesgos abiertos ahora
1. Validación pendiente de build/install en este entorno (`npm install` colgado previamente).
2. Turnstile depende de backend/keys de entorno para validación real.
3. Coexistencia temporal de wrappers y componentes nuevos hasta completar cada módulo.
4. En este entorno no hay dependencias instaladas aún en `CDS_VUE3_ZERO` (`npm run build` falla: `vite: not found`).
5. Aún quedan referencias `@legacy` en módulos no migrados (conteo actual: 42 en `src/*`).

## 6) Evidencia por archivo/línea (fase actual)

1. Widget local Turnstile creado:
   - `src/components/widgets/TurnstileWidget.vue:1`
   - `src/components/widgets/TurnstileWidget.vue:14`
   - `src/components/widgets/TurnstileWidget.vue:75`
2. Auth desacoplado de `@legacy`:
   - `src/components/auth/LoginForm.vue:69`
   - `src/components/auth/RegisterForm.vue:29`
3. Public legal en Vue real (sin wrapper `LegacyView`):
   - `src/pages/public/TermsPage.vue:1`, `src/pages/public/TermsPage.vue:186`
   - `src/pages/public/PrivacyPage.vue:1`, `src/pages/public/PrivacyPage.vue:169`
   - `src/pages/public/LicensePage.vue:1`, `src/pages/public/LicensePage.vue:23`
   - `src/pages/public/PolicyPage.vue:1`, `src/pages/public/PolicyPage.vue:23`
4. Composables legales con `computed` (sin `@legacy`):
   - `src/composables/useTermsPage.js:4`
   - `src/composables/usePrivacyPage.js:3`
   - `src/composables/useLicensePage.js:3`
   - `src/composables/usePolicyPage.js:3`
5. Calculadoras en Vue real (sin `LegacyView`):
   - `src/pages/public/CalculatorsPage.vue:1`
   - `src/pages/public/CalculatorsPage.vue:34`
   - `src/composables/useCalculatorsPage.js:3`
6. Verificación de remanente `@legacy`:
   - Comando: `rg -n "@legacy" src | wc -l`
   - Resultado: `42` (pendientes por fases Public/Client/Admin/Calculadoras/Token).
