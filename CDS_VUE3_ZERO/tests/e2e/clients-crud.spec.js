/**
 * Tests CRUD de Clientes - CDS ZERO
 */

import { test, expect } from '@playwright/test'
import { loginFromUi, checkRateLimit } from './helpers/auth.js'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
const TEST_CLIENT_PASS = process.env.TEST_CLIENT_PASSWORD || 'client123'

// Usar storageState para tests de admin
test.use({ storageState: 'tests/e2e/.auth/admin.json' })

test.describe('Admin - CRUD de Clientes', () => {
  
  test('debe cargar pagina de clientes con listado', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Verificar titulo
    await expect(page.getByRole('heading', { name: /Clientes/i }).first()).toBeVisible()
    
    // Verificar botones principales
    await expect(page.getByRole('button', { name: /Nuevo cliente/i })).toBeVisible()
    
    // Verificar que hay listado
    await expect(page.locator('text=/Listado|Audit Test/i').first()).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe crear un nuevo cliente', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const timestamp = Date.now()
    const clientName = `Test Client ${timestamp}`
    
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Click en "Nuevo cliente"
    await page.getByRole('button', { name: /Nuevo cliente/i }).click()
    
    // Llenar formulario (primeros inputs de texto)
    const textInputs = page.locator('input[type="text"]')
    await textInputs.nth(0).fill(clientName)
    await page.locator('input[type="email"]').fill(`client_${timestamp}@test.com`)
    
    // Guardar
    await page.getByRole('button', { name: /Guardar cliente/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que el cliente aparece en el listado
    await expect(page.locator(`text=${clientName}`).first()).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe seleccionar un cliente y ver detalles', async ({ page }) => {
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Click en primer cliente del listado
    const firstClient = page.locator('.list-item, li').filter({ hasText: /CDS-\d+|\w+@/ }).first()
    await expect(firstClient).toBeVisible()
    await firstClient.click()
    await waitForAppToSettle(page)
    
    // Verificar que hay botones de accion en detalle
    await expect(page.getByRole('button', { name: /Agregar dispositivo|Crear OT/i }).first()).toBeVisible()
  })
})

test.describe('Protección de rutas de Clientes', () => {
  // Este test no usa storageState porque necesita probar sin auth
  test.use({ storageState: undefined })
  
  test('cliente no autenticado no puede acceder a /admin/clients', async ({ page }) => {
    // Limpiar storage para este test
    await page.context().clearCookies()
    
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    await expect(page).toHaveURL(/\/login/)
  })

  test('cliente autenticado no puede acceder a /admin/clients', async ({ page }) => {
    // Limpiar storage y hacer login como cliente
    await page.context().clearCookies()
    await page.goto('/login')
    
    try {
      await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASS)
    } catch (e) {
      if (e.message === 'RATE_LIMIT_EXCEEDED') {
        test.skip(true, 'Rate limit activo - saltando test')
        return
      }
      throw e
    }
    
    await expect(page).toHaveURL(/\/dashboard/)
    
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    await expect(page).not.toHaveURL(/\/admin\/clients/)
  })
})
