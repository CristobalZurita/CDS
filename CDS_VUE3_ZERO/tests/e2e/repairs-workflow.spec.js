/**
 * Tests del flujo de Reparaciones - CDS ZERO
 * Desde creación hasta cambio de estado
 */

import { test, expect } from '@playwright/test'
import { resolveAuthState, loginFromUi } from './helpers/auth.js'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

test.describe('Flujo de Reparaciones', () => {
  
  test.use({ storageState: resolveAuthState('admin') })

  test('debe mostrar lista de reparaciones', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Verificar título o encabezado
    await expect(page.locator('h1, h2')).toContainText(/Reparaciones|Repairs/i)
    
    // Debe haber lista o tabla
    const repairsList = page.locator('.repairs-list, table, [class*="repair"]').first()
    await expect(repairsList).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe crear una nueva reparación', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const timestamp = Date.now()
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Nuevo
    await page.getByRole('button', { name: /Nueva|Nuevo|Crear/i }).click()
    
    // Seleccionar cliente (o crear rápido)
    const clientSelect = page.locator('select[name="client_id"]').first()
    if (await clientSelect.isVisible().catch(() => false)) {
      await clientSelect.selectOption({ index: 1 }) // Primer cliente
    }
    
    // Llenar datos del equipo
    await page.locator('input[name="device_model"], input[name="model"]').fill(`Sintetizador Test ${timestamp}`)
    await page.locator('textarea[name="problem_reported"], input[name="problem"]').fill('No enciende, problema de fuente de poder')
    
    // Prioridad
    const prioritySelect = page.locator('select[name="priority"]').first()
    if (await prioritySelect.isVisible().catch(() => false)) {
      await prioritySelect.selectOption('normal')
    }
    
    // Guardar
    await page.getByRole('button', { name: /Guardar|Crear|Ingresar/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que se creó (debe aparecer en lista o mostrar mensaje de éxito)
    await expect(page.locator('text=/creada|ingresada|éxito|success/i, text=' + timestamp.toString())).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe cambiar estado de una reparación', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Click en primera reparación para ver detalle
    const firstRepair = page.locator('.repair-item, table tbody tr, [class*="repair-row"]').first()
    await expect(firstRepair).toBeVisible()
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
        await expect(page.locator('text=/actualizado|cambiado|éxito/i')).toBeVisible()
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
    const viewButton = page.getByRole('button', { name: /Ver|Editar|Detalle/i }).first()
    await expect(viewButton).toBeVisible()
    await viewButton.click()
    
    await waitForAppToSettle(page)
    
    // Debe mostrar detalles
    await expect(page.locator('text=/Detalle|Información|Estado/i')).toBeVisible()
    
    // Debe tener información del cliente o equipo
    const info = page.locator('.repair-detail, [class*="detail"], [class*="info"]').first()
    await expect(info).toBeVisible()
  })
})

test.describe('Cliente - Mis Reparaciones', () => {
  
  test('cliente puede ver sus reparaciones', async ({ page }) => {
    // Login como cliente
    await page.goto('/login')
    await loginFromUi(page, 'client@example.com', 'client123')
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Ir a reparaciones
    await page.getByRole('link', { name: /Reparaciones|Mis equipos/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar lista
    await expect(page.locator('h1, h2')).toContainText(/Reparaciones|Mis/i)
    
    // Debe mostrar lista (puede estar vacía)
    const content = page.locator('main').first()
    await expect(content).toBeVisible()
  })

  test('cliente NO puede crear reparaciones desde admin', async ({ page }) => {
    // Login como cliente
    await page.goto('/login')
    await loginFromUi(page, 'client@example.com', 'client123')
    
    // Intentar acceder a admin/repairs
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Debe redirigir
    await expect(page).not.toHaveURL(/\/admin/)
  })
})
