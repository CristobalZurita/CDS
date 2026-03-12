/**
 * Tests de Cambio de Estado en Detalle de Reparacion - CDS ZERO
 * Flujo completo: cambio de estado, edicion tecnica, firmas
 * Basado en RepairDetailAdminPage.vue
 */

import { test, expect } from '@playwright/test'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

// Usar storageState para tests de admin
test.use({ storageState: 'tests/e2e/.auth/admin.json' })

test.describe('Admin - Detalle de Reparacion', () => {
  

  test('debe cargar detalle de una reparacion', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    // Primero ir al listado y obtener el ID de una reparacion
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    
    // Click en "Abrir" de la primera reparacion
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Verificar que cargo el detalle
    await expect(page.locator('h1')).toContainText(/Detalle de reparacion/i)
    
    // Verificar secciones principales
    await expect(page.locator('text=/Estado|Prioridad|Total OT/i')).toBeVisible()
    await expect(page.locator('text=/Informacion general|Cliente|Instrumento/i')).toBeVisible()
    await expect(page.locator('text=/Estado y costos|Diagnostico/i')).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe mostrar resumen de estado y costos', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Verificar summary cards
    const summaryCards = page.locator('.summary-card, .summary-grid article')
    await expect(summaryCards.first()).toBeVisible()
    
    // Verificar que hay informacion de estado
    await expect(page.locator('text=/Estado/i')).toBeVisible()
    await expect(page.locator('text=/Prioridad/i')).toBeVisible()
    await expect(page.locator('text=/Total|Costo/i')).toBeVisible()
  })
})

test.describe('Admin - Cambio de Estado de Reparacion', () => {
  

  test('debe cambiar el estado de una reparacion', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    // Ir al detalle de una reparacion
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Obtener estado actual
    const statusSelect = page.locator('select').filter({ has: page.locator('option:has-text("-")') }).first()
    const currentStatus = await statusSelect.inputValue()
    
    // Cambiar a otro estado
    const options = await statusSelect.locator('option').all()
    const nextOption = options.find(opt => opt.getAttribute('value') !== currentStatus)
    
    if (nextOption) {
      const newStatusValue = await nextOption.getAttribute('value')
      const newStatusLabel = await nextOption.textContent()
      
      await statusSelect.selectOption(newStatusValue)
      
      // Click en Actualizar estado
      await page.getByRole('button', { name: /Actualizar estado/i }).click()
      await waitForAppToSettle(page)
      
      // Verificar que se actualizo
      await expect(page.locator('text=/actualizado|cambiado|exito/i').first()).toBeVisible()
    }
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe editar diagnostico y trabajo realizado', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Llenar diagnostico
    const diagnosisTextarea = page.locator('textarea').filter({ has: page.locator(':above(:text("Trabajo realizado"))') }).first()
    await diagnosisTextarea.fill('Diagnostico actualizado: problema en fuente de poder')
    
    // Llenar trabajo realizado
    const workTextarea = page.locator('textarea').filter({ has: page.locator(':near(:text("Trabajo realizado"))') }).first()
    await workTextarea.fill('Se reemplazo capacitor C47 y se calibro fuente')
    
    // Guardar cambios
    await page.getByRole('button', { name: /Guardar cambios tecnicos/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar guardado
    await expect(page.locator('text=/guardado|actualizado|exito/i').first()).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe actualizar costos de la reparacion', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Actualizar costo de partes
    const partsInput = page.locator('input[type="number"]').filter({ has: page.locator(':near(:text("partes|mano de obra"))') }).first()
    await partsInput.fill('15000')
    
    // Actualizar abono
    const paidInput = page.locator('input[type="number"]').filter({ has: page.locator(':near(:text("Abonado"))') }).first()
    await paidInput.fill('20000')
    
    // Cambiar medio de pago
    const paymentSelect = page.locator('select').filter({ has: page.locator('option:has-text("Efectivo")') }).first()
    if (await paymentSelect.isVisible()) {
      await paymentSelect.selectOption('cash')
    }
    
    // Guardar
    await page.getByRole('button', { name: /Guardar cambios tecnicos/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar
    await expect(page.locator('text=/guardado|exito/i').first()).toBeVisible()
  })
})

test.describe('Admin - Firmas y Fotos', () => {
  

  test('debe solicitar firma de ingreso', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Click en solicitar firma ingreso
    await page.getByRole('button', { name: /Solicitar firma ingreso/i }).click()
    await waitForAppToSettle(page)
    
    // Debe generar un link
    await expect(page.locator('text=/Link firma|Firma ingreso/i').first()).toBeVisible()
  })

  test('debe solicitar firma de retiro', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    await page.getByRole('button', { name: /Solicitar firma retiro/i }).click()
    await waitForAppToSettle(page)
    
    await expect(page.locator('text=/Link firma|Firma retiro/i').first()).toBeVisible()
  })

  test('debe mostrar estado de firmas', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Verificar que muestra estado de firmas
    await expect(page.locator('text=/Firma ingreso:/i')).toBeVisible()
    await expect(page.locator('text=/Firma retiro:/i')).toBeVisible()
    
    // Debe mostrar OK o Pendiente
    const firmaText = await page.locator('text=/Firma ingreso:/i').textContent()
    expect(firmaText).toMatch(/OK|Pendiente/)
  })

  test('debe mostrar galeria de fotos', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Verificar seccion de fotos
    await expect(page.locator('h2').filter({ hasText: /Fotos/i })).toBeVisible()
    await expect(page.locator('text=/Sin fotos|photos-grid/i').first()).toBeVisible()
  })
})

test.describe('Admin - Notas de Reparacion', () => {
  

  test('debe mostrar seccion de notas', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Verificar seccion de notas
    await expect(page.locator('h2').filter({ hasText: /Notas/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Agregar nota/i })).toBeVisible()
  })

  test('debe mostrar formulario de nueva nota', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Click en agregar nota
    await page.getByRole('button', { name: /Agregar nota/i }).click()
    await waitForAppToSettle(page)
    
    // Debe aparecer formulario
    await expect(page.locator('textarea').filter({ has: page.locator(':near(:text("Nota"))') }).first()).toBeVisible()
  })
})

test.describe('Admin - Navegacion desde Detalle', () => {
  

  test('debe volver al listado desde detalle', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Click en Volver
    await page.getByRole('button', { name: /Volver/i }).click()
    await waitForAppToSettle(page)
    
    // Debe volver al listado
    await expect(page).toHaveURL(/\/admin\/repairs$/)
    await expect(page.locator('h1')).toContainText('Reparaciones')
  })

  test('debe ir a compras OT', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    await page.getByRole('button', { name: /Abrir/i }).first().click()
    await waitForAppToSettle(page)
    
    // Click en Compras OT
    const comprasButton = page.getByRole('button', { name: /Compras OT|Purchase/i })
    if (await comprasButton.isVisible().catch(() => false)) {
      await comprasButton.click()
      await waitForAppToSettle(page)
      
      // Debe navegar a compras
      await expect(page).toHaveURL(/\/admin\/purchase-requests|compras/)
    }
  })
})
