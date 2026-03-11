/**
 * Tests del Admin Dashboard E2E
 * CDS ZERO + Playwright
 */

import { test, expect } from '@playwright/test'
import { loginFromUi } from './helpers/auth.js'
import { trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'

const TEST_ADMIN_EMAIL = process.env.TEST_ADMIN_EMAIL || 'admin@example.com'
const TEST_ADMIN_PASSWORD = process.env.TEST_ADMIN_PASSWORD || ''
const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
const TEST_CLIENT_PASSWORD = process.env.TEST_CLIENT_PASSWORD || ''

test.describe('Admin Dashboard', () => {
  
  test('carga el dashboard admin correctamente', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    // Login primero
    await page.goto('/login')
    await loginFromUi(page, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
    
    // Ir al admin
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
    // Login
    await page.goto('/login')
    await loginFromUi(page, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
    
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

  test('stats cards muestran datos', async ({ page }) => {
    // Login
    await page.goto('/login')
    await loginFromUi(page, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
    
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

test.describe('Protección de rutas admin', () => {
  
  test('cliente no puede acceder a /admin', async ({ page }) => {
    // Login como cliente
    await page.goto('/login')
    await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    
    // Intentar ir a admin
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Debe ser redirigido (a home o dashboard)
    await expect(page).not.toHaveURL(/\/admin/)
  })
})
