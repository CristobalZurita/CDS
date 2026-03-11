# 🧪 Guía de Testing - CDS ZERO

## Estructura de Tests

```
CDS_VUE3_ZERO/tests/
├── e2e/
│   ├── helpers/
│   │   ├── auth.js          # Helpers de autenticación
│   │   └── page.js          # Helpers de página (errores, esperas)
│   ├── auth.setup.js        # Setup inicial (login y guardar estado)
│   ├── auth.spec.js         # Tests de autenticación
│   ├── admin-dashboard.spec.js  # Tests del admin
│   └── navigation.spec.js   # Tests de navegación básica
└── README.md
```

## Cómo correr los tests

### Requisitos previos
1. Backend corriendo en `http://localhost:8000`
2. Base de datos con usuarios de test

### Usuarios de test necesarios

```sql
-- Crear en la base de datos
INSERT INTO users (email, password, role, is_active) VALUES
('admin@example.com', '<hashed_password>', 'admin', 1),
('client@example.com', '<hashed_password>', 'client', 1);
```

O ejecutar el seed de test:
```bash
cd backend
python scripts/seed_test_users.py
```

### Comandos

```bash
# Ir a la carpeta de ZERO
cd CDS_VUE3_ZERO

# Instalar Playwright (primera vez)
npx playwright install

# Correr todos los tests
npx playwright test

# Correr con UI (modo visual)
npx playwright test --ui

# Correr solo un archivo
npx playwright test auth.spec.js

# Correr en modo headed (ver el navegador)
npx playwright test --headed

# Correr en modo debug
npx playwright test --debug

# Correr tests específicos
npx playwright test -g "login"  # Tests que contienen "login"
```

### Configuración con variables de entorno

```bash
# Usuarios de test personalizados
export TEST_ADMIN_EMAIL="miadmin@test.com"
export TEST_ADMIN_PASSWORD="mipassword"
export TEST_CLIENT_EMAIL="miclient@test.com"
export TEST_CLIENT_PASSWORD="mipassword"

# API del backend
export VITE_API_URL="http://localhost:8000/api/v1"

# Luego correr tests
npx playwright test
```

## Escribir nuevos tests

### Ejemplo básico

```javascript
import { test, expect } from '@playwright/test'
import { trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'

test('mi funcionalidad', async ({ page }) => {
  const tracker = trackBrowserErrors(page)
  
  await page.goto('/mi-ruta')
  await waitForAppToSettle(page)
  
  // Interactuar
  await page.locator('button').click()
  
  // Verificar
  await expect(page.locator('.resultado')).toContainText('Éxito')
  
  // Verificar que no hay errores de consola
  expect(tracker.getErrors()).toHaveLength(0)
})
```

### Test con autenticación

```javascript
import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth.js'

// Usar storageState para reutilizar login
test.use({ storageState: resolveAuthState('admin') })

test('funcionalidad de admin', async ({ page }) => {
  await page.goto('/admin')
  // Ya está autenticado como admin
})
```

### Test sin autenticación

```javascript
import { test, expect } from '@playwright/test'

// No usar storageState
test('página pública', async ({ page }) => {
  await page.goto('/')
  // Usuario no autenticado
})
```

## Buenas prácticas

### 1. Usar data-testid cuando sea posible

```vue
<!-- En tu componente -->
<button data-testid="save-button">Guardar</button>

<!-- En el test -->
await page.getByTestId('save-button').click()
```

### 2. Preferir roles ARIA

```javascript
// ✅ Bien
await page.getByRole('button', { name: 'Guardar' }).click()
await page.getByRole('heading', { name: 'Dashboard' })

// ⚠️  Fragil
await page.locator('.btn-primary').click()
```

### 3. Esperar a la red

```javascript
// Esperar a que terminen las peticiones
await page.waitForLoadState('networkidle')

// O esperar respuesta específica
await page.waitForResponse(/\/api\/users/)
```

### 4. Limpiar después de cada test

```javascript
test.afterEach(async ({ page }) => {
  // Limpiar datos creados
  await page.goto('/admin')
  // ...borrar lo que se creó en el test
})
```

## Solución de problemas

### Tests fallan porque no hay usuarios

```bash
# Seed de usuarios de test
cd backend
python -c "
from app.core.security import hash_password
from app.models import User
from app.core.database import SessionLocal

db = SessionLocal()
# Crear usuarios...
"
```

### Backend no responde

```bash
# Verificar que backend está corriendo
curl http://localhost:8000/health

# Ver logs
tail -f backend/cirujano.log
```

### Errores de timeout

```javascript
// Aumentar timeout en test específico
test('lento', async ({ page }) => {
  test.setTimeout(60000) // 60 segundos
  // ...
})
```

### Ver reporte HTML

```bash
# Después de correr tests
npx playwright show-report
```

## CI/CD (GitHub Actions)

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  test:
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
          npx playwright test
          
      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

## Recursos

- [Playwright Docs](https://playwright.dev/docs/intro)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Selectors](https://playwright.dev/docs/selectors)
- [Assertions](https://playwright.dev/docs/test-assertions)
