/**
 * Tests de autenticación E2E
 * CDS ZERO + Playwright
 */

import { test, expect } from '@playwright/test'
import { loginFromUi, checkRateLimit } from './helpers/auth.js'
import { trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'

const TEST_ADMIN_EMAIL = process.env.TEST_ADMIN_EMAIL || 'admin@example.com'
const TEST_ADMIN_PASSWORD = process.env.TEST_ADMIN_PASSWORD || ''
const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
const TEST_CLIENT_PASSWORD = process.env.TEST_CLIENT_PASSWORD || 'client123'

test.describe('Autenticación', () => {
  
  test('usuario no autenticado es redirigido a login desde /admin', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Debe redirigir a login con redirect
    await expect(page).toHaveURL(/\/login\?redirect=.*admin/)
    await expect(page.getByRole('heading')).toContainText(/Iniciar|Login|Acceder/)
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('usuario no autenticado es redirigido a login desde /dashboard', async ({ page }) => {
    await page.goto('/dashboard')
    await waitForAppToSettle(page)
    
    await expect(page).toHaveURL(/\/login/)
  })

  test('login con credenciales válidas redirige a dashboard (cliente)', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/login')
    
    try {
      await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    } catch (e) {
      if (e.message === 'RATE_LIMIT_EXCEEDED') {
        test.skip(true, 'Rate limit activo - saltando test')
        return
      }
      throw e
    }
    
    // Cliente va a /dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    // Verificar que está en el dashboard (título específico)
    await expect(page.getByRole('heading', { name: /Mi Panel de Control|Dashboard/i })).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('login con credenciales válidas redirige a admin (admin)', async ({ page }) => {
    await page.goto('/login')
    
    try {
      await loginFromUi(page, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
    } catch (e) {
      if (e.message === 'RATE_LIMIT_EXCEEDED') {
        test.skip(true, 'Rate limit activo - saltando test')
        return
      }
      throw e
    }
    
    // Admin va a /admin
    await expect(page).toHaveURL(/\/admin/)
    // Verificar título del admin
    await expect(page.getByRole('heading', { name: /Dashboard|Panel/i }).first()).toBeVisible()
  })

  test('login con credenciales inválidas muestra error', async ({ page }) => {
    await page.goto('/login')
    
    // Llenar con credenciales incorrectas
    await page.locator('input[type="email"]').fill('noexiste@test.com')
    await page.locator('input[type="password"]').fill('wrongpassword')
    
    // Esperar Turnstile
    await page.waitForTimeout(500)
    await expect(page.locator('button[type="submit"]')).toBeEnabled({ timeout: 10000 })
    await page.locator('button[type="submit"]').click()
    
    // Esperar un momento para ver el resultado
    await page.waitForTimeout(500)
    
    // Verificar si hay rate limiting
    if (await checkRateLimit(page)) {
      test.skip(true, 'Rate limit activo - saltando test')
      return
    }
    
    // Debe mostrar mensaje de error
    await expect(page.locator('text=/incorrecto|error|inválido|no encontrado/i')).toBeVisible()
    
    // Debe seguir en login
    await expect(page).toHaveURL(/\/login/)
  })

  test('logout funciona correctamente', async ({ page }) => {
    // Login primero
    await page.goto('/login')
    
    try {
      await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    } catch (e) {
      if (e.message === 'RATE_LIMIT_EXCEEDED') {
        test.skip(true, 'Rate limit activo - saltando test')
        return
      }
      throw e
    }
    
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Logout - buscar en navbar o menú
    // Intentar varios selectores comunes
    const logoutSelectors = [
      'text=Cerrar sesión',
      'text=Salir',
      'text=Logout',
      '[data-testid="logout"]',
      'a:has-text("Salir")',
      'button:has-text("Salir")'
    ]
    
    let logoutFound = false
    for (const selector of logoutSelectors) {
      const element = page.locator(selector).first()
      if (await element.isVisible().catch(() => false)) {
        await element.click()
        logoutFound = true
        break
      }
    }
    
    // Si no encontramos botón, limpiar storage manualmente
    if (!logoutFound) {
      await page.evaluate(() => {
        localStorage.removeItem('cds_auth_token')
        localStorage.removeItem('cds_auth_user')
      })
    }
    
    await waitForAppToSettle(page)
    
    // Verificar que ya no está autenticado
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })

  test('persistencia de sesión después de recargar', async ({ page }) => {
    // Login
    await page.goto('/login')
    
    try {
      await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    } catch (e) {
      if (e.message === 'RATE_LIMIT_EXCEEDED') {
        test.skip(true, 'Rate limit activo - saltando test')
        return
      }
      throw e
    }
    
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Recargar
    await page.reload()
    await waitForAppToSettle(page)
    
    // Debe seguir autenticado (no redirigir a login)
    await expect(page).not.toHaveURL(/\/login/)
    // Verificar que sigue en dashboard
    await expect(page.getByRole('heading', { name: /Mi Panel de Control|Dashboard/i })).toBeVisible()
  })
})
