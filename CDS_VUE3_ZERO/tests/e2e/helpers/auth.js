/**
 * Helpers de autenticación para tests E2E
 * Playwright + CDS ZERO
 */

import { expect } from '@playwright/test'
import path from 'path'
import os from 'os'

// Directorio para guardar estados de autenticación
const AUTH_DIR = process.env.PLAYWRIGHT_AUTH_DIR || path.join(os.tmpdir(), 'cds_zero_auth')

/**
 * Resuelve la ruta al archivo de estado de autenticación
 * @param {'admin' | 'client'} profile 
 * @returns {string}
 */
export function resolveAuthState(profile) {
  return path.join(AUTH_DIR, `${profile}.json`)
}

/**
 * Login desde la UI
 * @param {import('@playwright/test').Page} page 
 * @param {string} email 
 * @param {string} password 
 */
export async function loginFromUi(page, email, password) {
  // Verificar que estamos en login
  await expect(page.locator('input[type="email"]')).toBeVisible()
  
  // Llenar formulario
  await page.locator('input[type="email"]').fill(email)
  await page.locator('input[type="password"]').fill(password)
  
  // Submit
  await page.locator('button[type="submit"]').click()
  
  // Esperar redirección (login exitoso va a dashboard o admin)
  await page.waitForURL(/\/(dashboard|admin)/, { timeout: 5000 })
}

/**
 * Logout desde la UI
 * @param {import('@playwright/test').Page} page 
 */
export async function logoutFromUi(page) {
  // Buscar botón de logout (en navbar o menú)
  const logoutButton = page.locator('text=Cerrar sesión, text=Logout, button:has-text("Salir")').first()
  
  if (await logoutButton.isVisible().catch(() => false)) {
    await logoutButton.click()
    await page.waitForURL(/\/login/, { timeout: 5000 })
  }
}

/**
 * Setup de autenticación para tests
 * Guarda el estado para reutilizar en otros tests
 * @param {import('@playwright/test').Page} page 
 * @param {'admin' | 'client'} profile
 * @param {Object} credentials
 */
export async function setupAuth(page, profile, credentials) {
  await page.goto('/login')
  await loginFromUi(page, credentials.email, credentials.password)
  
  // Guardar estado de autenticación
  const authFile = resolveAuthState(profile)
  await page.context().storageState({ path: authFile })
  
  return authFile
}
