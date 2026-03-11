# 📊 Análisis de Tests - CDS

## Estado Actual

### Tests LEGACY (raíz/tests)

| Aspecto | Estado |
|---------|--------|
| **Cantidad** | 16 archivos E2E + Unit |
| **Cobertura** | Auth, CRUD, Navegación, Quotation, OT Payments |
| **Calidad** | ⭐⭐⭐⭐⭐ Excelente |
| **Setup** | Auth con storageState, webServer automático |
| **Helpers** | auth.ts, page.ts (reutilizables) |
| **Problema** | Están en LEGACY, no en ZERO |

**Archivos importantes:**
- `tests/e2e/auth.spec.ts` - Login/logout
- `tests/e2e/admin-crud.spec.ts` - CRUD de usuarios y categorías
- `tests/e2e/admin-extended-crud.spec.ts` - CRUD extendido
- `tests/e2e/quotation.spec.ts` - Flujo de cotización
- `tests/e2e/helpers/auth.ts` - Helper de autenticación
- `tests/e2e/helpers/page.ts` - Helper de página

### Tests ZERO (CDS_VUE3_ZERO/tests)

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Cantidad** | 1 archivo | 4 archivos |
| **Cobertura** | Solo navegación | Auth, Admin, Navegación |
| **Calidad** | ⭐⭐ Básico | ⭐⭐⭐⭐ Bueno |
| **Setup** | Ninguno | storageState + setup |
| **Helpers** | Ninguno | auth.js, page.js |

---

## Recomendaciones

### Opción A: Migrar tests LEGACY → ZERO (Recomendado)

**Pros:**
- Tests existentes ya son buenos
- Solo hay que adaptar selectores si cambiaron
- Cobertura completa inmediata

**Cómo hacerlo:**

```bash
# 1. Copiar tests de LEGACY a ZERO
cp tests/e2e/auth.spec.ts CDS_VUE3_ZERO/tests/e2e/auth-legacy.spec.js
cp tests/e2e/admin-crud.spec.ts CDS_VUE3_ZERO/tests/e2e/admin-crud.spec.js
# ... etc

# 2. Adaptar sintaxis:
# - Cambiar .ts a .js
# - Cambiar import types
# - Actualizar selectores si es necesario
# - Cambiar testMatch de setup
```

**Adaptaciones necesarias:**
- Cambiar `getByTestId('turnstile-bypass')` → eliminar (en ZERO se desactiva Turnstile)
- Cambiar `getByTestId('login-email')` → `locator('input[type="email"]')` o agregar data-testid
- Cambiar `storageState` path si es diferente

### Opción B: Escribir tests nuevos desde cero

**Pros:**
- Tests específicos para ZERO
- Más mantenible a largo plazo

**Contras:**
- Toma más tiempo
- Duplica esfuerzo

### Opción C: Híbrida (Recomendada a corto plazo)

1. **YA IMPLEMENTADO:** Tests básicos en ZERO (auth, admin, navegación)
2. **PRÓXIMO:** Migrar los tests de CRUD más importantes de LEGACY
3. **MANTENER:** Tests de LEGACY como referencia hasta tener todo migrado

---

## Tests Prioritarios para Migrar

### 🔴 CRÍTICO (Hacer primero)

| Test | Por qué | Complejidad |
|------|---------|-------------|
| `admin-crud.spec.ts` | Tests de usuarios y categorías | Media |
| `quotation.spec.ts` | Flujo de cotización core | Media |

### 🟡 IMPORTANTE (Después)

| Test | Por qué | Complejidad |
|------|---------|-------------|
| `client-ot-payments.spec.ts` | Pagos OT | Media |
| `admin-extended-crud.spec.ts` | Más CRUD | Media |
| `integration-flows.spec.ts` | Flujos integrales | Alta |

### 🟢 OPCIONAL (Más adelante)

| Test | Por qué | Complejidad |
|------|---------|-------------|
| `error-states.spec.ts` | Manejo de errores | Baja |
| `dynamic-routes.spec.ts` | Rutas dinámicas | Baja |
| `navigation-intent.spec.ts` | Navegación avanzada | Baja |

---

## Guía Rápida: Migrar un test de LEGACY a ZERO

### Paso 1: Copiar y renombrar

```bash
cp tests/e2e/admin-crud.spec.ts CDS_VUE3_ZERO/tests/e2e/admin-crud.spec.js
```

### Paso 2: Adaptar imports

```typescript
// LEGACY (TypeScript)
import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

// ZERO (JavaScript)
import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth.js'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'
```

### Paso 3: Adaptar selectores

```typescript
// LEGACY (con data-testid específicos)
await page.getByTestId('users-new').click()
await page.getByTestId('user-email').fill(createdEmail)

// ZERO (más genérico o agregar data-testid a componentes)
await page.getByRole('button', { name: /Nuevo|Crear/ }).click()
await page.locator('input[name="email"]').fill(createdEmail)

// O mejor: agregar data-testid a los componentes Vue
await page.getByTestId('user-form-email').fill(createdEmail)
```

### Paso 4: Verificar paths

```javascript
// En los tests de ZERO, usar resolveAuthState de los helpers nuevos
import { resolveAuthState } from './helpers/auth.js'

test.use({ storageState: resolveAuthState('admin') })
```

### Paso 5: Correr y ajustar

```bash
cd CDS_VUE3_ZERO
npx playwright test admin-crud.spec.js --headed
# Ver qué falla y ajustar
```

---

## Estado de Cobertura Actual

### ✅ Cubierto en ZERO

- [x] Navegación básica (home, calculadoras, tienda)
- [x] Login/logout
- [x] Protección de rutas (/admin, /dashboard)
- [x] Acceso a admin dashboard
- [x] Navegación del sidebar admin

### ⚠️ Parcialmente cubierto

- [ ] CRUD de usuarios (solo create básico)
- [ ] CRUD de categorías
- [ ] CRUD de inventario
- [ ] CRUD de reparaciones

### ❌ No cubierto

- [ ] Flujo completo de cotización
- [ ] Pagos OT
- [ ] Subida de fotos/firmas
- [ ] Calculadoras (funcionalidad)
- [ ] Agendamiento

---

## Scripts útiles

```bash
# Correr tests específicos de LEGACY (para comparar)
cd /mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN
npm run test:e2e -- tests/e2e/auth.spec.ts

# Correr tests de ZERO
cd CDS_VUE3_ZERO
npm run test:e2e

# Correr un test específico con debug
npx playwright test auth.spec.js --debug

# Ver diferencias de screenshots
npx playwright test --update-snapshots
```

---

## Conclusión

**Veredicto:** Los tests de LEGACY son **buenos** y deberían migrarse a ZERO progresivamente.

**Estrategia recomendada:**
1. Mantener los tests nuevos de ZERO (ya implementados)
2. Migrar 2-3 tests de LEGACY por semana
3. Priorizar: auth → admin-crud → quotation → resto
4. Una vez migrados todos, eliminar tests de LEGACY

**Tiempo estimado:**
- Migrar tests críticos: ~4 horas
- Migrar tests importantes: ~8 horas
- Migrar todo: ~16 horas

**Alternativa rápida:** Si el tiempo es limitado, mantener los tests de LEGACY corriendo en CI/CD como "regression tests" mientras se desarrollan tests nuevos para ZERO.
