/**
 * Tests del Admin Dashboard E2E
 * CDS ZERO + Playwright
 */

import { test, expect } from '@playwright/test'
import { loginFromUi } from './helpers/auth.js'
import { trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'

const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
const TEST_CLIENT_PASSWORD = process.env.TEST_CLIENT_PASSWORD || 'client123'

// Usar storageState para tests de admin (evita rate limiting)
test.use({ storageState: 'tests/e2e/.auth/admin.json' })

test.describe('Admin Dashboard', () => {
  
  test('carga el dashboard admin correctamente', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    // Ya estamos autenticados, ir directo al admin
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Verificar elementos del AdminShellLayout
    await expect(page.locator('.admin-sidebar, aside')).toBeVisible()
    await expect(page.locator('main.admin-main')).toBeVisible()
    
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
    ]
    
    for (const section of sections) {
      // Click en el link del sidebar
      await page.getByRole('link').filter({ hasText: section.link }).first().click()
      await waitForAppToSettle(page)
      
      // Verificar URL
      await expect(page).toHaveURL(section.url)
    }
  })

  test('stats cards muestran datos', async ({ page }) => {
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Verificar que hay cards con números
    const statCards = page.locator('.stat-card, .kpi-card, [class*="stat"], [class*="kpi"]')
    const count = await statCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Cada card debe tener un número o valor
    for (let i = 0; i < Math.min(count, 4); i++) {
      const text = await statCards.nth(i).textContent()
      expect(text).toBeTruthy()
    }
  })
})

test.describe('Protección de rutas admin', () => {
  // Este test no usa storageState porque necesita un cliente sin permisos de admin
  test.use({ storageState: undefined })
  
  test('cliente no puede acceder a /admin', async ({ page }) => {
    // Login como cliente
    await page.goto('/login')
    await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Intentar acceder a admin
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Debe ser redirigido o mostrar error de acceso
    const currentUrl = page.url()
    const hasAccess = currentUrl.includes('/admin') && !currentUrl.includes('/admin/')
    expect(hasAccess).toBeFalsy()
  })
})
