/**
 * Helpers de autenticación para tests E2E
 * Playwright + CDS ZERO
 */

import { expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Directorio para guardar estados de autenticación
const AUTH_DIR = process.env.PLAYWRIGHT_AUTH_DIR || path.join(__dirname, '..', '.auth')

/**
 * Resuelve la ruta al archivo de estado de autenticación
 * @param {'admin' | 'client'} profile 
 * @returns {string}
 */
export function resolveAuthState(profile) {
  return path.join(AUTH_DIR, `${profile}.json`)
}

/**
 * Verifica si hay rate limiting en la página
 * @param {import('@playwright/test').Page} page 
 * @returns {Promise<boolean>}
 */
export async function checkRateLimit(page) {
  const pageContent = await page.content()
  return pageContent.includes('Rate limit exceeded')
}

/**
 * Login desde la UI
 * @param {import('@playwright/test').Page} page 
 * @param {string} email 
 * @param {string} password 
 * @param {Object} options
 * @param {boolean} options.skipRateLimitCheck - Si es true, no verifica rate limiting
 * @throws {Error} Si hay rate limiting o el login falla
 */
export async function loginFromUi(page, email, password, options = {}) {
  const { skipRateLimitCheck = false } = options
  
  // Verificar que estamos en login
  await expect(page.locator('input[type="email"]')).toBeVisible()
  
  // Llenar formulario
  await page.locator('input[type="email"]').fill(email)
  await page.locator('input[type="password"]').fill(password)
  
  // Pequeña pausa para dar tiempo a Vue a propagar el evento de Turnstile
  await page.waitForTimeout(500)
  
  // Esperar a que el botón esté habilitado (Turnstile puede tardar en emitir token)
  const submitButton = page.locator('button[type="submit"]')
  await expect(submitButton).toBeEnabled({ timeout: 10000 })
  
  // Submit
  await submitButton.click()
  
  // Esperar un momento para ver si aparece rate limit
  await page.waitForTimeout(500)
  
  // Verificar rate limiting
  if (!skipRateLimitCheck && await checkRateLimit(page)) {
    throw new Error('RATE_LIMIT_EXCEEDED')
  }
  
  // Esperar redirección (login exitoso va a dashboard o admin)
  // Aumentado timeout y agregado waitForLoadState para estabilidad
  await page.waitForURL(/\/(dashboard|admin)/, { timeout: 10000 })
  await page.waitForLoadState('networkidle')
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
