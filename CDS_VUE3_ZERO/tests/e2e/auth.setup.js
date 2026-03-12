/**
 * Setup de autenticación para tests E2E
 * Crea estados de autenticación reutilizables para admin y cliente
 */

import { test as setup, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const authDir = path.join(__dirname, '.auth')

const adminAuthFile = path.join(authDir, 'admin.json')
const clientAuthFile = path.join(authDir, 'client.json')

const TEST_ADMIN_EMAIL = process.env.TEST_ADMIN_EMAIL || 'admin@example.com'
const TEST_ADMIN_PASSWORD = process.env.TEST_ADMIN_PASSWORD || 'Admin123!'
const TEST_CLIENT_EMAIL = process.env.TEST_CLIENT_EMAIL || 'cliente@test.com'
const TEST_CLIENT_PASSWORD = process.env.TEST_CLIENT_PASSWORD || 'client123'

setup('authenticate as admin', async ({ page }) => {
  // Ir a login y autenticar
  await page.goto('/login')
  
  await page.locator('input[type="email"]').fill(TEST_ADMIN_EMAIL)
  await page.locator('input[type="password"]').fill(TEST_ADMIN_PASSWORD)
  
  // Esperar Turnstile
  await page.waitForTimeout(500)
  await expect(page.locator('button[type="submit"]')).toBeEnabled({ timeout: 10000 })
  await page.locator('button[type="submit"]').click()
  
  // Esperar redirección
  await page.waitForURL(/\/admin/, { timeout: 10000 })
  
  // Guardar estado
  await page.context().storageState({ path: adminAuthFile })
})

setup('authenticate as client', async ({ page }) => {
  // Ir a login y autenticar
  await page.goto('/login')
  
  await page.locator('input[type="email"]').fill(TEST_CLIENT_EMAIL)
  await page.locator('input[type="password"]').fill(TEST_CLIENT_PASSWORD)
  
  // Esperar Turnstile
  await page.waitForTimeout(500)
  await expect(page.locator('button[type="submit"]')).toBeEnabled({ timeout: 10000 })
  await page.locator('button[type="submit"]').click()
  
  // Esperar redirección
  await page.waitForURL(/\/dashboard/, { timeout: 10000 })
  
  // Guardar estado
  await page.context().storageState({ path: clientAuthFile })
})
