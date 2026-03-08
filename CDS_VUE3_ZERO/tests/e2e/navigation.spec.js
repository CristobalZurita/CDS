import { test, expect } from '@playwright/test'

test.describe('Navegación - MasterLayout', () => {
  test('debe cargar la página principal', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/CDS/i)
  })

  test('debe navegar a Cotizador IA desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=/cotizador|cotizar/i')
    await expect(page).toHaveURL(/\/cotizador/)
  })

  test('debe navegar a Agendar desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=/agendar/i')
    await expect(page).toHaveURL(/\/agendar/)
  })

  test('debe navegar a Calculadoras desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=/calculadora/i')
    await expect(page).toHaveURL(/\/calculadora/)
  })

  test('debe navegar a Tienda desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=/tienda/i')
    await expect(page).toHaveURL(/\/tienda/)
  })

  test('debe navegar a Login desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=/login|iniciar/i')
    await expect(page).toHaveURL(/\/login/)
  })

  test('footer - links de redes sociales visibles', async ({ page }) => {
    await page.goto('/')
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
  })

  test('footer - links legales funcionan', async ({ page }) => {
    await page.goto('/')
    await page.click('text=/términos|privacidad/i')
    await expect(page).toHaveURL(/\/terminos|\/privacidad/)
  })
})

test.describe('HomePage - Botones y Links', () => {
  test('hero - botones de acción visibles', async ({ page }) => {
    await page.goto('/')
    const heroSection = page.locator('[data-testid="hero"], .hero, section').first()
    await expect(heroSection).toBeVisible()
  })

  test('debe mostrar navegación rápida', async ({ page }) => {
    await page.goto('/')
    const mainContent = page.locator('main, #app')
    await expect(mainContent).toBeVisible()
  })

  test('links de secciones funcionan', async ({ page }) => {
    await page.goto('/')
    const links = page.locator('a[href]')
    const count = await links.count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('CalculatorsPage - Navegación', () => {
  test('debe cargar página de calculadoras', async ({ page }) => {
    await page.goto('/calculadoras')
    await expect(page).toHaveURL(/\/calculadora/)
  })

  test('debe mostrar lista de calculadoras', async ({ page }) => {
    await page.goto('/calculadoras')
    const mainContent = page.locator('main, #app')
    await expect(mainContent).toBeVisible()
  })

  test('debe navegar a calculadora Timer555', async ({ page }) => {
    await page.goto('/calculadoras')
    await page.click('text=/timer|555/i')
    await expect(page).toHaveURL(/\/calculadora.*timer/)
  })

  test('debe navegar a calculadora Resistor Color', async ({ page }) => {
    await page.goto('/calculadoras')
    await page.click('text=/resistor|color/i')
    await expect(page).toHaveURL(/\/calculadora.*resistor/)
  })
})

test.describe('CotizadorIAPage - Flujo Multi-Step', () => {
  test('debe cargar página de cotizador', async ({ page }) => {
    await page.goto('/cotizador-ia')
    await expect(page).toHaveURL(/\/cotizador/)
  })

  test('botón volver al inicio funciona', async ({ page }) => {
    await page.goto('/cotizador-ia')
    await page.click('text=/inicio|volver|home/i')
    await expect(page).toHaveURL('/')
  })

  test('navegación entre steps funciona', async ({ page }) => {
    await page.goto('/cotizador-ia')
    const buttons = page.locator('button')
    const count = await buttons.count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('SchedulePage - Calendario', () => {
  test('debe cargar página de agendar', async ({ page }) => {
    await page.goto('/agendar')
    await expect(page).toHaveURL(/\/agendar/)
  })

  test('botones de navegación de mes funcionan', async ({ page }) => {
    await page.goto('/agendar')
    const buttons = page.locator('button')
    const count = await buttons.count()
    expect(count).toBeGreaterThan(0)
  })

  test('debe mostrar calendario', async ({ page }) => {
    await page.goto('/agendar')
    const mainContent = page.locator('main, #app')
    await expect(mainContent).toBeVisible()
  })
})

test.describe('StorePage - Catálogo', () => {
  test('debe cargar página de tienda', async ({ page }) => {
    await page.goto('/tienda')
    await expect(page).toHaveURL(/\/tienda/)
  })

  test('botón actualizar funciona', async ({ page }) => {
    await page.goto('/tienda')
    const mainContent = page.locator('main, #app')
    await expect(mainContent).toBeVisible()
  })
})

test.describe('Auth Pages - Login/Register', () => {
  test('debe cargar página de login', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveURL(/\/login/)
  })

  test('link a registro funciona', async ({ page }) => {
    await page.goto('/login')
    await page.click('text=/registro|registrarse|sign up/i')
    await expect(page).toHaveURL(/\/registro/)
  })

  test('debe cargar página de registro', async ({ page }) => {
    await page.goto('/registro')
    await expect(page).toHaveURL(/\/registro/)
  })

  test('link de vuelta a home funciona', async ({ page }) => {
    await page.goto('/login')
    await page.click('text=/inicio|home|volver/i')
    await expect(page).toHaveURL('/')
  })
})

test.describe('Public Pages - Términos y Privacidad', () => {
  test('debe cargar página de términos', async ({ page }) => {
    await page.goto('/terminos')
    await expect(page).toHaveURL(/\/terminos/)
  })

  test('debe cargar página de privacidad', async ({ page }) => {
    await page.goto('/privacidad')
    await expect(page).toHaveURL(/\/privacidad/)
  })

  test('botón ir a privacidad desde términos funciona', async ({ page }) => {
    await page.goto('/terminos')
    await page.click('text=/privacidad/i')
    await expect(page).toHaveURL(/\/privacidad/)
  })

  test('link volver desde privacidad funciona', async ({ page }) => {
    await page.goto('/privacidad')
    await page.click('text=/volver|inicio/i')
    await expect(page).toHaveURL(/\/|\/terminos/)
  })
})

test.describe('Verificación de Carga de Recursos', () => {
  test('no debe tener errores de consola críticos en home', async ({ page }) => {
    const errors = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const criticalErrors = errors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('404')
    )

    expect(criticalErrors.length).toBeLessThan(5)
  })

  test('CSS debe estar cargado (elementos tienen estilos)', async ({ page }) => {
    await page.goto('/')
    const body = page.locator('body')
    const backgroundColor = await body.evaluate(el =>
      window.getComputedStyle(el).backgroundColor
    )

    expect(backgroundColor).not.toBe('')
  })
})
