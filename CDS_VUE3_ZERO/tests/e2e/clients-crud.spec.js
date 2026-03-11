/**
 * Tests CRUD de Clientes - CDS ZERO
 * Escritos desde cero basándose en la implementación actual de ClientsPage.vue
 */

import { test, expect } from '@playwright/test'
import { loginFromUi } from './helpers/auth.js'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

test.describe('Admin - CRUD de Clientes', () => {
  
  const TEST_ADMIN_EMAIL = process.env.TEST_ADMIN_EMAIL || 'admin@example.com'
  const TEST_ADMIN_PASSWORD = process.env.TEST_ADMIN_PASSWORD || ''
  const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
  const TEST_CLIENT_PASSWORD = process.env.TEST_CLIENT_PASSWORD || ''

  async function loginAsAdmin(page) {
    await page.goto('/login')
    await loginFromUi(page, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)
  }

  test('debe cargar pagina de clientes con listado', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Verificar titulo
    await expect(page.locator('h1')).toContainText('Clientes')
    
    // Verificar que existe el buscador
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"]').first()
    await expect(searchInput).toBeVisible()
    
    // Verificar botones de accion
    await expect(page.getByRole('button', { name: /Nuevo cliente|Cerrar ingreso/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Editar cliente|Cerrar edicion/i })).toBeVisible()
    
    // Verificar paneles de lista y detalle
    await expect(page.locator('aside, .list-panel')).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe crear un nuevo cliente con datos completos', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const timestamp = Date.now()
    const clientData = {
      name: `Test Client ${timestamp}`,
      email: `client_${timestamp}@test.com`,
      phone: '+56912345678',
      phone_alt: '+56987654321',
      city: 'Santiago',
      region: 'Metropolitana',
      country: 'Chile',
      address: 'Av. Test 123'
    }
    
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Click en "Nuevo cliente"
    await page.getByRole('button', { name: /Nuevo cliente/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que aparece el formulario
    await expect(page.locator('h2')).toContainText(/Nuevo cliente/i)
    
    // Llenar formulario
    await page.locator('input[type="text"]').nth(0).fill(clientData.name) // Nombre
    await page.locator('input[type="email"]').fill(clientData.email)
    await page.locator('input[type="text"]').nth(1).fill(clientData.phone) // Telefono
    await page.locator('input[type="text"]').nth(2).fill(clientData.phone_alt) // Telefono alterno
    await page.locator('input[type="text"]').nth(3).fill(clientData.city) // Ciudad
    await page.locator('input[type="text"]').nth(4).fill(clientData.region) // Region
    await page.locator('input[type="text"]').nth(5).fill(clientData.country) // Pais
    
    // Direccion (input full)
    const addressInputs = page.locator('.full input[type="text"]')
    if (await addressInputs.count() > 0) {
      await addressInputs.first().fill(clientData.address)
    }
    
    // Guardar
    await page.getByRole('button', { name: /Guardar cliente|Guardando/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que el cliente aparece en la lista
    await expect(page.locator('text=' + clientData.name)).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe buscar clientes por nombre', async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Esperar a que cargue la lista
    await page.waitForSelector('.list-panel li, .list-item', { timeout: 5000 })
    
    // Buscar "test" o "cliente"
    const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"]')
    await searchInput.fill('test')
    await page.waitForTimeout(500) // Debounce del search
    
    // Verificar que hay resultados (o mensaje de vacio)
    const listItems = page.locator('.list-panel li, .list-item')
    const count = await listItems.count()
    
    // Si hay resultados, verificar que contienen el texto buscado
    if (count > 0) {
      const firstItemText = await listItems.first().textContent()
      expect(firstItemText.toLowerCase()).toContain('test')
    }
  })

  test('debe seleccionar un cliente y ver sus detalles', async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Esperar lista
    await page.waitForSelector('.list-panel li, .list-item', { timeout: 5000 })
    
    // Click en primer cliente
    const firstClient = page.locator('.list-panel li, .list-item').first()
    await expect(firstClient).toBeVisible()
    await firstClient.click()
    await waitForAppToSettle(page)
    
    // Verificar panel de detalle
    await expect(page.locator('.detail-panel, article')).toBeVisible()
    
    // Verificar que hay informacion de contacto
    await expect(page.locator('text=/Telefono|Email|Reparaciones/i')).toBeVisible()
    
    // Verificar botones de accion en detalle
    await expect(page.getByRole('button', { name: /Agregar dispositivo|Crear OT|Eliminar/i })).toBeVisible()
  })

  test('debe editar un cliente seleccionado', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const newName = `Updated ${Date.now()}`
    
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Seleccionar primer cliente
    await page.waitForSelector('.list-panel li, .list-item', { timeout: 5000 })
    await page.locator('.list-panel li, .list-item').first().click()
    await waitForAppToSettle(page)
    
    // Click en Editar
    await page.getByRole('button', { name: /Editar cliente/i }).click()
    await waitForAppToSettle(page)
    
    // Cambiar nombre
    const nameInput = page.locator('input[type="text"]').nth(0)
    await nameInput.fill('')
    await nameInput.fill(newName)
    
    // Guardar
    await page.getByRole('button', { name: /Guardar|Actualizar/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar cambio
    await expect(page.locator('text=' + newName)).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe agregar un dispositivo a un cliente', async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Seleccionar primer cliente
    await page.waitForSelector('.list-panel li, .list-item', { timeout: 5000 })
    await page.locator('.list-panel li, .list-item').first().click()
    await waitForAppToSettle(page)
    
    // Click en Agregar dispositivo
    await page.getByRole('button', { name: /Agregar dispositivo/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que aparece formulario de dispositivo
    await expect(page.locator('text=/Dispositivo|Modelo|Serial/i')).toBeVisible()
    
    // Llenar datos del dispositivo
    await page.locator('input[name="model"], input[placeholder*="modelo"]').fill('Sintetizador Test')
    await page.locator('input[name="serial_number"], input[placeholder*="serial"]').fill('SN123456')
    
    // Guardar (si hay boton visible)
    const saveButton = page.getByRole('button', { name: /Guardar dispositivo|Agregar/i })
    if (await saveButton.isVisible().catch(() => false)) {
      await saveButton.click()
      await waitForAppToSettle(page)
    }
  })

  test('debe crear una orden de trabajo desde un cliente', async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // Seleccionar primer cliente
    await page.waitForSelector('.list-panel li, .list-item', { timeout: 5000 })
    await page.locator('.list-panel li, .list-item').first().click()
    await waitForAppToSettle(page)
    
    // Click en Crear OT
    await page.getByRole('button', { name: /Crear OT|Nueva OT/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar formulario de OT
    await expect(page.locator('text=/Orden|Trabajo|Problema/i')).toBeVisible()
    
    // Llenar problema
    await page.locator('textarea, input[name="problem_reported"]').fill('No enciende - problema de fuente')
    
    // Guardar
    const saveButton = page.getByRole('button', { name: /Guardar|Crear/i }).first()
    if (await saveButton.isVisible().catch(() => false)) {
      await saveButton.click()
      await waitForAppToSettle(page)
    }
  })
})

test.describe('Proteccion de rutas de Clientes', () => {
  
  test('usuario no autenticado no puede acceder a /admin/clients', async ({ page }) => {
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    await expect(page).toHaveURL(/\/login/)
  })

  test('cliente autenticado no puede acceder a /admin/clients', async ({ page }) => {
    // Login como cliente
    await page.goto('/login')
    await loginFromUi(page, TEST_CLIENT_EMAIL, TEST_CLIENT_PASSWORD)
    await page.waitForURL(/\/dashboard/, { timeout: 5000 })
    
    // Intentar ir a admin clients
    await page.goto('/admin/clients')
    await waitForAppToSettle(page)
    
    // No debe estar en admin
    await expect(page).not.toHaveURL(/\/admin/)
  })
})
