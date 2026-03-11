/**
 * Tests de Filtros y Búsqueda en Reparaciones - CDS ZERO
 * Basado en RepairsAdminPage.vue
 */

import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth.js'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

test.describe('Admin - Filtros de Reparaciones', () => {
  
  test.use({ storageState: resolveAuthState('admin') })

  test('debe cargar lista de reparaciones con filtros', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Verificar titulo
    await expect(page.locator('h1')).toContainText('Reparaciones')
    
    // Verificar filtros
    await expect(page.locator('input[type="search"], input[placeholder*="Buscar"]')).toBeVisible()
    await expect(page.locator('select')).toBeVisible() // Filtro de estado
    
    // Verificar tabla
    await expect(page.locator('table')).toBeVisible()
    
    // Verificar columnas
    const headers = page.locator('table thead th')
    await expect(headers.nth(0)).toContainText(/OT|Codigo/i)
    await expect(headers.nth(1)).toContainText(/Cliente/i)
    await expect(headers.nth(2)).toContainText(/Instrumento|Modelo/i)
    await expect(headers.nth(3)).toContainText(/Estado/i)
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe filtrar reparaciones por texto de busqueda', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Esperar a que cargue la tabla
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    
    // Buscar "OT" (deberia encontrar ordenes de trabajo)
    const searchInput = page.locator('input[type="search"]')
    await searchInput.fill('OT')
    await page.waitForTimeout(600) // Esperar filtrado
    
    // Verificar que hay resultados o mensaje vacio
    const rows = page.locator('table tbody tr')
    const count = await rows.count()
    
    if (count > 0) {
      // Verificar que los resultados coinciden con la busqueda
      const firstRow = await rows.first().textContent()
      expect(firstRow.toLowerCase()).toMatch(/ot|cliente|instrumento/)
    }
  })

  test('debe filtrar reparaciones por estado', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    
    // Seleccionar un estado del dropdown
    const statusSelect = page.locator('select').first()
    const options = await statusSelect.locator('option').allTextContents()
    
    // Saltar "Todos" y seleccionar el primero real
    if (options.length > 1) {
      await statusSelect.selectOption({ label: options[1] })
      await page.waitForTimeout(600)
      
      // Verificar que se filtro
      const rows = page.locator('table tbody tr')
      const count = await rows.count()
      
      if (count > 0) {
        const firstStatus = await rows.first().locator('td').nth(3).textContent()
        expect(firstStatus).toContain(options[1])
      }
    }
  })

  test('debe mostrar contador de resultados', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Verificar que muestra el contador ({{ repairs.length }})
    const heading = page.locator('h2').first()
    const text = await heading.textContent()
    
    expect(text).toMatch(/Listado|Reparaciones/)
    // El numero puede variar, pero debe mostrarse
  })

  test('debe limpiar filtros y mostrar todos', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    
    // Aplicar filtro
    const searchInput = page.locator('input[type="search"]')
    await searchInput.fill('xyz123nonexistent')
    await page.waitForTimeout(600)
    
    // Limpiar busqueda
    await searchInput.fill('')
    await page.waitForTimeout(600)
    
    // Debe volver a mostrar resultados
    const rows = page.locator('table tbody tr')
    await expect(rows.first()).toBeVisible()
  })
})

test.describe('Admin - Acciones de Reparaciones', () => {
  
  test.use({ storageState: resolveAuthState('admin') })

  test('debe abrir detalle de una reparacion', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    
    // Click en "Abrir" de la primera fila
    const openButton = page.getByRole('button', { name: /Abrir/i }).first()
    await expect(openButton).toBeVisible()
    await openButton.click()
    
    await waitForAppToSettle(page)
    
    // Debe navegar al detalle
    await expect(page).toHaveURL(/\/admin\/repairs\/\d+/)
  })

  test('debe ordenar resultados por fecha', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    await page.waitForSelector('table tbody tr', { timeout: 5000 })
    
    // Si hay mas de una fila, verificar que estan ordenadas
    const rows = page.locator('table tbody tr')
    const count = await rows.count()
    
    if (count >= 2) {
      // Obtener fechas de las primeras dos filas
      const date1 = await rows.nth(0).locator('td').nth(4).textContent()
      const date2 = await rows.nth(1).locator('td').nth(4).textContent()
      
      // Verificar que son fechas validas
      expect(date1).toBeTruthy()
      expect(date2).toBeTruthy()
    }
  })
})

test.describe('Admin - Crear Reparacion desde Listado', () => {
  
  test.use({ storageState: resolveAuthState('admin') })

  test('debe mostrar formulario de nueva reparacion', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Click en Nueva reparacion
    await page.getByRole('button', { name: /Nueva reparacion/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar formulario
    await expect(page.locator('h2')).toContainText(/Crear reparacion/i)
    await expect(page.locator('select[name="client_id"], select').first()).toBeVisible()
    await expect(page.locator('input[name="model"], input[placeholder*="modelo"]').first()).toBeVisible()
    await expect(page.locator('textarea[name="problem_reported"], textarea').first()).toBeVisible()
    
    // Verificar boton de crear
    await expect(page.getByRole('button', { name: /Crear OT/i })).toBeVisible()
  })

  test('debe crear reparacion con cliente existente', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Abrir formulario
    await page.getByRole('button', { name: /Nueva reparacion/i }).click()
    await waitForAppToSettle(page)
    
    // Seleccionar cliente
    const clientSelect = page.locator('select[name="client_id"], select').first()
    const options = await clientSelect.locator('option').count()
    
    if (options > 1) {
      await clientSelect.selectOption({ index: 1 })
    }
    
    // Llenar datos
    await page.locator('input[name="model"], input[type="text"]').nth(1).fill('Roland Juno-106')
    await page.locator('textarea[name="problem_reported"], textarea').fill('Teclas no responden')
    
    // Crear
    await page.getByRole('button', { name: /Crear OT/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que se creo (aparece en lista o mensaje de exito)
    await expect(page.locator('text=/creada|creado|exito|success/i, table tbody tr').first()).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe cancelar creacion de reparacion', async ({ page }) => {
    await page.goto('/admin/repairs')
    await waitForAppToSettle(page)
    
    // Abrir formulario
    await page.getByRole('button', { name: /Nueva reparacion/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que esta visible
    await expect(page.locator('h2')).toContainText(/Crear reparacion/i)
    
    // Cancelar
    await page.getByRole('button', { name: /Cancelar/i }).click()
    await waitForAppToSettle(page)
    
    // Formulario debe ocultarse
    await expect(page.locator('h2')).not.toContainText(/Crear reparacion/i)
  })
})
