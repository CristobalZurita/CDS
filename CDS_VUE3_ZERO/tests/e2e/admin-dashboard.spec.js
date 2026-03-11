/**
 * Tests del Admin Dashboard E2E
 * CDS ZERO + Playwright
 */

import { test, expect } from '@playwright/test'
import { resolveAuthState, loginFromUi } from './helpers/auth.js'
import { trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'

// Usar storageState para reutilizar autenticación
test.describe('Admin Dashboard', () => {
  
  // Setup: Crear archivo de auth antes de todos los tests
  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext()
    const page = await context.newPage()
    
    // Login como admin
    await page.goto('/login')
    await loginFromUi(page, 'admin@example.com', 'admin123')
    
    // Guardar estado
    const authFile = resolveAuthState('admin')
    await context.storageState({ path: authFile })
    
    await context.close()
  })

  test.describe('con autenticación de admin', () => {
    // Usar el estado guardado
    test.use({ storageState: resolveAuthState('admin') })

    test('carga el dashboard admin correctamente', async ({ page }) => {
      const tracker = trackBrowserErrors(page)
      
      await page.goto('/admin')
      await waitForAppToSettle(page)
      
      // Verificar elementos del AdminShellLayout
      await expect(page.locator('.admin-sidebar, aside')).toBeVisible()
      await expect(page.locator('.admin-content, main')).toBeVisible()
      
      // Debe tener estadísticas o indicadores
      const stats = page.locator('.stat-card, .kpi-card, [class*="stat"], [class*="kpi"]')
      await expect(stats.first()).toBeVisible()
      
      expect(tracker.getErrors()).toHaveLength(0)
    })

    test('navegación del sidebar funciona', async ({ page }) => {
      await page.goto('/admin')
      await waitForAppToSettle(page)
      
      // Probar navegación a diferentes secciones
      const sections = [
        { link: /Clientes|Clients/, url: /clients/ },
        { link: /Repairs|Reparaciones/, url: /repairs/ },
        { link: /Inventory|Inventario/, url: /inventory/ },
        { link: /Quotes|Cotizaciones/, url: /quotes/ },
      ]
      
      for (const section of sections) {
        const link = page.getByRole('link').filter({ hasText: section.link })
        if (await link.isVisible().catch(() => false)) {
          await link.click()
          await expect(page).toHaveURL(section.url)
          await page.goto('/admin') // Volver
        }
      }
    })

    test('crear nuevo cliente desde admin', async ({ page }) => {
      await page.goto('/admin/clients')
      await waitForAppToSettle(page)
      
      // Click en "Nuevo" o "Crear"
      const newButton = page.getByRole('button').filter({ hasText: /Nuevo|Crear|New/ }).first()
      await expect(newButton).toBeVisible()
      await newButton.click()
      
      // Llenar formulario
      const timestamp = Date.now()
      await page.locator('input[name="name"], input[name="full_name"]').fill(`Test Client ${timestamp}`)
      await page.locator('input[name="email"]').fill(`test${timestamp}@example.com`)
      await page.locator('input[name="phone"]').fill('+56912345678')
      
      // Guardar
      await page.getByRole('button').filter({ hasText: /Guardar|Save/ }).click()
      
      // Verificar que aparece en la lista
      await expect(page.locator('text=' + `Test Client ${timestamp}`)).toBeVisible()
    })

    test('stats cards muestran datos', async ({ page }) => {
      await page.goto('/admin')
      await waitForAppToSettle(page)
      
      // Buscar cards de estadísticas
      const statValues = page.locator('.stat-value, [class*="stat-value"], .kpi-value')
      const count = await statValues.count()
      
      expect(count).toBeGreaterThan(0)
      
      // Verificar que tienen contenido numérico
      for (let i = 0; i < Math.min(count, 3); i++) {
        const text = await statValues.nth(i).textContent()
        expect(text).toBeTruthy()
      }
    })
  })

  test.describe('protección de rutas admin', () => {
    // Sin storageState - usuario no autenticado
    
    test('cliente no puede acceder a /admin', async ({ page }) => {
      // Login como cliente
      await page.goto('/login')
      await loginFromUi(page, 'client@example.com', 'client123')
      
      // Intentar ir a admin
      await page.goto('/admin')
      
      // Debe ser redirigido (a home o dashboard)
      await expect(page).not.toHaveURL(/\/admin/)
    })
  })
})
