/**
 * Helpers de página para tests E2E
 * Captura de errores, esperas, etc.
 */

/**
 * Espera a que la aplicación se "asiente" (cargue completamente)
 * @param {import('@playwright/test').Page} page 
 * @param {number} timeout 
 */
export async function waitForAppToSettle(page, timeout = 2000) {
  // Esperar a que no haya requests de red pendientes
  await page.waitForLoadState('networkidle')
  
  // Esperar un poco más para que Vue termine de renderizar
  await page.waitForTimeout(500)
}

/**
 * Trackea errores de consola del navegador
 * @param {import('@playwright/test').Page} page 
 * @returns {Object} Tracker con método getErrors()
 */
export function trackBrowserErrors(page) {
  const errors = []
  const warnings = []
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text())
    } else if (msg.type() === 'warning') {
      warnings.push(msg.text())
    }
  })
  
  page.on('pageerror', error => {
    errors.push(error.message)
  })
  
  return {
    getErrors: () => errors,
    getWarnings: () => warnings,
    getAll: () => ({ errors, warnings })
  }
}

/**
 * Verifica que no haya errores de consola
 * @param {Object} tracker 
 * @param {Object} options 
 */
export function expectNoBrowserErrors(tracker, options = {}) {
  const { allow = [] } = options
  const errors = tracker.getErrors()
  
  // Filtrar errores permitidos (ej: favicon 404)
  const filteredErrors = errors.filter(error => {
    return !allow.some(allowed => error.includes(allowed))
  })
  
  if (filteredErrors.length > 0) {
    console.log('Errores de consola detectados:', filteredErrors)
  }
  
  // En tests, usar expect directamente
  return filteredErrors.length === 0
}

/**
 * Toma screenshot solo si el test falla
 * @param {import('@playwright/test').Page} page 
 * @param {import('@playwright/test').TestInfo} testInfo 
 */
export async function screenshotOnFailure(page, testInfo) {
  if (testInfo.status !== testInfo.expectedStatus) {
    await page.screenshot({ 
      path: `test-results/${testInfo.title.replace(/\s+/g, '_')}.png`,
      fullPage: true 
    })
  }
}
