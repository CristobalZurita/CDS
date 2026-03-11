/**
 * Tests de autenticación E2E
 * CDS ZERO + Playwright
 */

import { test, expect } from '@playwright/test'
import { loginFromUi, logoutFromUi } from './helpers/auth.js'
import { trackBrowserErrors, waitForAppToSettle } from './helpers/page.js'

const TEST_ADMIN_EMAIL = process.env.TEST_ADMIN_EMAIL || 'admin@example.com'
const TEST_ADMIN_PASSWORD = process.env.TEST_ADMIN_PASSWORD || 'Admin123!'
const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'test@example.com'
const TEST_CLIENT_PASSWORD = process.env.TEST_CLIENT_PASSWORD || 'Client123!'

test.describe('Autenticación', () => {
  
  test('usuario no autenticado es redirigido a login desde /admin', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Debe redirigir a login con redirect
    await expect(page).toHaveURL(/\/login\?redirect=.*admin/)
    await expect(page.locator('h1, h2')).toContainText(/Iniciar|Login|Acceder/)
    
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
    await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    
    // Cliente va a /dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1, h2')).toContainText(/Dashboard|Panel|Bienvenido/)
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('login con credenciales válidas redirige a admin (admin)', async ({ page }) => {
    // Nota: Este test requiere un usuario admin en la base de datos
    await page.goto('/login')
    await loginFromUi(page, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
    
    // Admin va a /admin
    await expect(page).toHaveURL(/\/admin/)
    await expect(page.locator('h1, h2')).toContainText(/Admin|Panel|Dashboard/)
  })

  test('login con credenciales inválidas muestra error', async ({ page }) => {
    await page.goto('/login')
    
    // Llenar con credenciales incorrectas
    await page.locator('input[type="email"]').fill('noexiste@test.com')
    await page.locator('input[type="password"]').fill('wrongpassword')
    await page.locator('button[type="submit"]').click()
    
    // Debe mostrar mensaje de error
    await expect(page.locator('text=/incorrecto|error|inválido|no encontrado/i')).toBeVisible()
    
    // Debe seguir en login
    await expect(page).toHaveURL(/\/login/)
  })

  test('logout funciona correctamente', async ({ page }) => {
    // Login primero
    await page.goto('/login')
    await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Logout
    await logoutFromUi(page)
    
    // Verificar que ya no está autenticado
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })

  test('persistencia de sesión después de recargar', async ({ page }) => {
    // Login
    await page.goto('/login')
    await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Recargar
    await page.reload()
    await waitForAppToSettle(page)
    
    // Debe seguir autenticado (no redirigir a login)
    await expect(page).not.toHaveURL(/\/login/)
  })
})
