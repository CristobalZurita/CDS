/**
 * Tests del flujo de Reparaciones - CDS ZERO
 * Desde creación hasta cambio de estado
 */

import { test, expect } from '@playwright/test'
import { loginFromUi } from './helpers/auth.js'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
const TEST_CLIENT_PASS = process.env.TEST_CLIENT_PASSWORD || ''

// Usar storageState para tests de admin
test.use({ storageState: 'tests/e2e/.auth/admin.json' })

test.describe('Flujo de Reparaciones', () => {
  
  test('debe mostrar lista de reparaciones', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Verificar título o encabezado
    await expect(page.getByRole('heading', { name: /Reparaciones|Repairs/i }).first()).toBeVisible()
    
    // Debe haber lista o tabla o mensaje vacío
    const content = page.locator('main, .repairs-list, table, [class*="repair"]').first()
    await expect(content).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe crear una nueva reparación', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const timestamp = Date.now()
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Buscar botón Nuevo
    const nuevoButton = page.getByRole('button', { name: /Nueva|Nuevo|Crear/i }).first()
    if (!await nuevoButton.isVisible().catch(() => false)) {
      test.skip(true, 'Botón de crear reparación no disponible')
      return
    }
    
    await nuevoButton.click()
    
    // Seleccionar cliente (o crear rápido)
    const clientSelect = page.locator('select[name="client_id"]').first()
    if (await clientSelect.isVisible().catch(() => false)) {
      await clientSelect.selectOption({ index: 1 }) // Primer cliente
    }
    
    // Llenar datos del equipo
    const modelInput = page.locator('input[name="device_model"], input[name="model"]').first()
    if (await modelInput.isVisible().catch(() => false)) {
      await modelInput.fill(`Sintetizador Test ${timestamp}`)
    }
    
    const problemInput = page.locator('textarea[name="problem_reported"], input[name="problem"]').first()
    if (await problemInput.isVisible().catch(() => false)) {
      await problemInput.fill('No enciende, problema de fuente de poder')
    }
    
    // Prioridad
    const prioritySelect = page.locator('select[name="priority"]').first()
    if (await prioritySelect.isVisible().catch(() => false)) {
      await prioritySelect.selectOption('normal')
    }
    
    // Guardar
    const saveButton = page.getByRole('button', { name: /Guardar|Crear|Ingresar/i }).first()
    if (await saveButton.isVisible().catch(() => false)) {
      await saveButton.click()
      await waitForAppToSettle(page)
      
      // Verificar que se creó (debe aparecer en lista o mostrar mensaje de éxito)
      const successMessage = page.locator('text=/creada|ingresada|éxito|success/i')
      const newItem = page.locator(`text=${timestamp}`)
      await expect(successMessage.or(newItem).first()).toBeVisible()
    }
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe cambiar estado de una reparación', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Click en primera reparación para ver detalle
    const firstRepair = page.locator('.repair-item, table tbody tr, [class*="repair-row"]').first()
    if (!await firstRepair.isVisible().catch(() => false)) {
      test.skip(true, 'No hay reparaciones para cambiar estado')
      return
    }
    
    await firstRepair.click()
    await waitForAppToSettle(page)
    
    // Buscar selector de estado
    const statusSelect = page.locator('select[name="status"], select[name="status_id"]').first()
    if (await statusSelect.isVisible().catch(() => false)) {
      const currentValue = await statusSelect.inputValue()
      
      // Cambiar a otro estado
      const options = await statusSelect.locator('option').allTextContents()
      const nextOption = options.find(o => o !== currentValue && o.trim() !== '')
      
      if (nextOption) {
        await statusSelect.selectOption({ label: nextOption })
        await page.getByRole('button', { name: /Guardar|Actualizar/i }).click()
        await waitForAppToSettle(page)
        
        // Verificar mensaje de éxito
        await expect(page.locator('text=/actualizado|cambiado|éxito/i').first()).toBeVisible()
      }
    }
  })

  test('debe buscar reparaciones por código o cliente', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Buscar
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar"]').first()
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('OT')
      await page.waitForTimeout(500)
      
      // Los resultados deben mostrarse
      const results = page.locator('.repair-item, table tbody tr').first()
      await expect(results).toBeVisible()
    }
  })

  test('debe ver detalle de una reparación', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Click en ver/editar
    const viewButton = page.getByRole('button', { name: /Ver|Editar|Detalle|Abrir/i }).first()
    if (!await viewButton.isVisible().catch(() => false)) {
      test.skip(true, 'No hay reparaciones para ver detalle')
      return
    }
    
    await viewButton.click()
    await waitForAppToSettle(page)
    
    // Debe mostrar detalles
    await expect(page.locator('text=/Detalle|Información|Estado/i').first()).toBeVisible()
  })
})

test.describe('Cliente - Mis Reparaciones', () => {
  // Estos tests no usan storageState porque necesitan login como cliente
  test.use({ storageState: undefined })
  
  test('cliente puede ver sus reparaciones', async ({ page }) => {
    // Login como cliente
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
    
    // Ir a reparaciones
    const repairsLink = page.getByRole('link', { name: /Reparaciones|Mis equipos/i }).first()
    if (await repairsLink.isVisible().catch(() => false)) {
      await repairsLink.click()
      await waitForAppToSettle(page)
      
      // Verificar lista
      await expect(page.getByRole('heading').first()).toBeVisible()
    }
    
    // Debe mostrar contenido
    const content = page.locator('main').first()
    await expect(content).toBeVisible()
  })

  test('cliente NO puede crear reparaciones desde admin', async ({ page }) => {
    // Login como cliente
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
    
    // Intentar acceder a admin/repairs
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Debe redirigir
    await expect(page).not.toHaveURL(/\/admin\/repairs/)
  })
})
