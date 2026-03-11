# 🎯 Estrategia de Testing - Todo desde ZERO

## Principio Fundamental

> **LEGACY es referencia, ZERO es realidad.**

- ✅ Se mira LEGACY para entender flujos de negocio
- ✅ Se escribe código nuevo en ZERO desde cero
- ❌ No se migra código de LEGACY automáticamente
- ❌ LEGACY se mantiene como "museo" histórico

---

## ¿Por qué esta estrategia?

| Problema con migrar LEGACY | Solución con ZERO |
|---------------------------|-------------------|
| Código desactualizado | Código moderno (Vue 3, Composition API) |
| Deuda técnica acumulada | Arquitectura limpia desde el inicio |
| Selectores frágiles (data-testid inconsistentes) | Selectores semánticos (roles, ARIA) |
| Tests acoplados a implementación vieja | Tests diseñados para la nueva implementación |
| Difícil de mantener | Mantenible a largo plazo |

---

## Estructura de Tests en ZERO

```
CDS_VUE3_ZERO/tests/e2e/
├── helpers/
│   ├── auth.js          # Login, logout, storageState
│   └── page.js          # Errores, esperas, utilidades
├── auth.setup.js        # Setup: login y guardar estado
├── auth.spec.js         # Tests: autenticación
├── navigation.spec.js   # Tests: navegación pública
├── admin-dashboard.spec.js  # Tests: panel admin
├── users-crud.spec.js   # Tests: gestión de usuarios
├── repairs-workflow.spec.js # Tests: flujo de reparaciones
└── [futuros: inventory, quotes, store, etc.]
```

---

## Cómo escribir un test nuevo (desde cero)

### Paso 1: Entender el flujo en LEGACY (mirar, no copiar)

```bash
# Ver cómo funciona en LEGACY
cat tests/e2e/admin-crud.spec.ts
# Objetivo: "entiendo que debo probar crear usuario"
```

### Paso 2: Explorar la UI de ZERO manualmente

```bash
# Correr ZERO
npm run dev

# Explorar:
# 1. Ir a /admin
# 2. Click en "Usuarios"
# 3. Click en "Nuevo"
# 4. Llenar formulario
# 5. Guardar
# 6. Verificar que aparece en lista
```

### Paso 3: Escribir el test en ZERO

```javascript
// tests/e2e/users-crud.spec.js
import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth.js'

test.use({ storageState: resolveAuthState('admin') })

test('crear usuario', async ({ page }) => {
  // Implementación específica para ZERO:
  await page.goto('/admin')
  await page.getByRole('link', { name: /Usuarios/i }).click()
  await page.getByRole('button', { name: /Nuevo/i }).click()
  
  // Usar selectores semánticos, no data-testid frágiles
  await page.locator('input[name="email"]').fill('test@test.com')
  await page.getByRole('button', { name: /Guardar/i }).click()
  
  // Verificar resultado
  await expect(page.locator('text=test@test.com')).toBeVisible()
})
```

### Paso 4: Correr y ajustar

```bash
npx playwright test users-crud.spec.js --headed
# Ver qué falla, ajustar, repetir
```

---

## Prioridades de Testing (Roadmap)

### 🔴 CRÍTICO (Negocio no funciona sin esto)
- [x] Autenticación (login, logout, protección de rutas)
- [x] Navegación básica
- [x] Admin Dashboard (acceso, stats)
- [x] CRUD Usuarios
- [ ] CRUD Clientes
- [ ] CRUD Reparaciones

### 🟡 IMPORTANTE (Funcionalidad core)
- [ ] Cambio de estados de reparaciones
- [ ] Inventario (lista, búsqueda)
- [ ] Cotizador IA (flujo básico)
- [ ] Subida de fotos/firmas

### 🟢 MEDIO (Completitud)
- [ ] Calculadoras (18)
- [ ] Store/Tienda
- [ ] Agendamiento de citas
- [ ] Perfil de usuario

### ⚪ OPCIONAL (Nice to have)
- [ ] Tests de performance
- [ ] Tests de accesibilidad (a11y)
- [ ] Tests de responsive

---

## Principios de Testing en ZERO

### 1. Testear comportamiento, no implementación

```javascript
// ❌ Mal (acoplado a implementación)
await page.locator('.btn-primary.mt-4[data-id="user-123"]').click()

// ✅ Bien (comportamiento)
await page.getByRole('button', { name: 'Guardar' }).click()
```

### 2. Un test, una responsabilidad

```javascript
// ❌ Mal (hace muchas cosas)
test('flujo completo', async () => {
  // login + crear + editar + borrar + logout
})

// ✅ Bien (tests separados)
test('login redirige a dashboard', async () => {})
test('crear usuario lo agrega a la lista', async () => {})
test('editar usuario actualiza datos', async () => {})
```

### 3. Datos de test independientes

```javascript
// ✅ Usar timestamps para evitar colisiones
const email = `test_${Date.now()}@example.com`
```

### 4. Limpiar siempre que sea posible

```javascript
test.afterEach(async ({ page }) => {
  // Borrar datos creados en el test
  // O usar base de datos de test que se resetea
})
```

---

## Cuándo mirar LEGACY

### ✅ SÍ mirar LEGACY:
- Para entender flujos de negocio complejos
- Para ver qué casos edge existen
- Para entender permisos (qué puede hacer cada rol)
- Para ver datos de ejemplo

### ❌ NO mirar LEGACY:
- Para copiar selectores (usar roles ARIA)
- Para copiar lógica de test (puede estar desactualizada)
- Para copiar estructura de archivos (ZERO es diferente)

---

## Comandos útiles

```bash
# Correr tests de ZERO
cd CDS_VUE3_ZERO
npm run test:e2e

# Correr un archivo específico
npx playwright test auth.spec.js

# Modo UI (interactivo)
npm run test:e2e:ui

# Modo debug (pasa paso a paso)
npm run test:e2e:debug

# Generar reporte HTML
npx playwright show-report
```

---

## Base de datos de Test

### Opción A: SQLite dedicada (Recomendada)

```bash
# Crear DB de test
export DATABASE_URL=sqlite:///./test.db

# Correr migrations
alembic upgrade head

# Seed de datos
python scripts/seed_test_data.py

# Correr tests (usará esta DB)
npm run test:e2e
```

### Opción B: Datos en memoria

```javascript
// En cada test, crear datos vía API
const user = await api.post('/users', testUserData)
// Test...
await api.delete(`/users/${user.id}`)
```

---

## Integración CI/CD (Futuro)

```yaml
# .github/workflows/e2e-zero.yml
name: E2E Tests ZERO
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 20
          
      - name: Install dependencies
        run: |
          cd CDS_VUE3_ZERO
          npm ci
          npx playwright install --with-deps
          
      - name: Run tests
        run: |
          cd CDS_VUE3_ZERO
          npm run test:e2e
        env:
          VITE_API_URL: http://localhost:8000/api/v1
          
      - name: Upload results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: CDS_VUE3_ZERO/playwright-report/
```

---

## Métricas de Calidad

### Cobertura mínima objetivo

| Módulo | Cobertura mínima |
|--------|-----------------|
| Auth | 100% (login, logout, 2FA, reset) |
| Admin Dashboard | 80% (navegación, CRUDs) |
| Repairs | 80% (flujo completo) |
| Inventory | 60% (lista, búsqueda, create) |
| Store | 50% (catálogo, carrito) |

### Definición de "cobertura"

- **Happy path**: Funciona con datos válidos
- **Error handling**: Muestra errores correctamente
- **Validación**: Rechaza datos inválidos
- **Permisos**: Usuarios ven lo que deben

---

## Recursos

- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Testing Library Queries](https://testing-library.com/docs/queries/about/#priority) (misma filosofía: roles > testid)
- [GitHub: microsoft/playwright](https://github.com/microsoft/playwright)

---

**Recuerda: Cada test nuevo en ZERO es una inversión en calidad. LEGACY nos enseñó el camino, ZERO lo hace mejor.**
