/**
 * Tests CRUD de Usuarios - CDS ZERO
 * Escritos desde cero para la implementación actual
 */

import { test, expect } from '@playwright/test'
import { resolveAuthState, loginFromUi } from './helpers/auth.js'
import { waitForAppToSettle, trackBrowserErrors } from './helpers/page.js'

test.describe('Admin - Gestión de Usuarios', () => {
  
  test.use({ storageState: resolveAuthState('admin') })

  test('debe mostrar lista de usuarios', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Navegar a usuarios
    await page.getByRole('link', { name: /Usuarios|Users|Administración/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar que hay tabla o lista de usuarios
    const userList = page.locator('table, .user-list, [class*="user"]').first()
    await expect(userList).toBeVisible()
    
    // Debe haber al menos un usuario (el admin actual)
    const rows = page.locator('table tbody tr, .user-item, [class*="user-row"]').first()
    await expect(rows).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe crear un nuevo usuario', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const timestamp = Date.now()
    const userData = {
      name: `Test User ${timestamp}`,
      email: `testuser_${timestamp}@example.com`,
      username: `testuser_${timestamp}`,
      password: 'SecurePass123!'
    }
    
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Ir a usuarios
    await page.getByRole('link', { name: /Usuarios|Users/i }).click()
    await waitForAppToSettle(page)
    
    // Click en Nuevo
    await page.getByRole('button', { name: /Nuevo|Crear|Agregar/i }).click()
    
    // Llenar formulario
    await page.locator('input[name="name"], input[name="full_name"], input[placeholder*="nombre"]').fill(userData.name)
    await page.locator('input[name="email"], input[type="email"]').fill(userData.email)
    await page.locator('input[name="username"]').fill(userData.username)
    await page.locator('input[name="password"], input[type="password"]').fill(userData.password)
    
    // Seleccionar rol
    const roleSelect = page.locator('select[name="role"]').first()
    if (await roleSelect.isVisible().catch(() => false)) {
      await roleSelect.selectOption('technician')
    }
    
    // Guardar
    await page.getByRole('button', { name: /Guardar|Save|Crear/i }).click()
    
    // Verificar que aparece en la lista
    await waitForAppToSettle(page)
    await expect(page.locator('text=' + userData.name)).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe editar un usuario existente', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const newName = `Updated User ${Date.now()}`
    
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Ir a usuarios
    await page.getByRole('link', { name: /Usuarios|Users/i }).click()
    await waitForAppToSettle(page)
    
    // Buscar y editar el primer usuario
    const editButton = page.getByRole('button', { name: /Editar|Edit/i }).first()
    await expect(editButton).toBeVisible()
    await editButton.click()
    
    // Cambiar nombre
    const nameInput = page.locator('input[name="name"], input[name="full_name"]').first()
    await nameInput.fill(newName)
    
    // Guardar
    await page.getByRole('button', { name: /Guardar|Save/i }).click()
    await waitForAppToSettle(page)
    
    // Verificar cambio
    await expect(page.locator('text=' + newName)).toBeVisible()
    
    expect(tracker.getErrors()).toHaveLength(0)
  })

  test('debe buscar usuarios', async ({ page }) => {
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Ir a usuarios
    await page.getByRole('link', { name: /Usuarios|Users/i }).click()
    await waitForAppToSettle(page)
    
    // Buscar "admin"
    const searchInput = page.locator('input[type="search"], input[placeholder*="buscar"], input[name="search"]').first()
    if (await searchInput.isVisible().catch(() => false)) {
      await searchInput.fill('admin')
      await page.waitForTimeout(500) // Esperar debounce
      
      // Debe filtrar resultados
      const results = page.locator('table tbody tr, .user-item').first()
      await expect(results).toBeVisible()
    }
  })
})

test.describe('Protección de rutas de Admin', () => {
  
  test('cliente no autenticado no puede acceder a admin', async ({ page }) => {
    // Sin storageState - usuario anónimo
    
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Debe redirigir a login
    await expect(page).toHaveURL(/\/login/)
  })

  test('cliente autenticado no puede acceder a admin', async ({ page }) => {
    // Login como cliente
    await page.goto('/login')
    await loginFromUi(page, 'client@example.com', 'client123')
    await expect(page).toHaveURL(/\/dashboard/)
    
    // Intentar ir a admin
    await page.goto('/admin')
    await waitForAppToSettle(page)
    
    // Debe redirigir a home o dashboard (no admin)
    await expect(page).not.toHaveURL(/\/admin/)
  })
})
