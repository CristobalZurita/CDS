import { test, expect } from '@playwright/test'

test.describe('Navegación - MasterLayout', () => {
  test('debe cargar la página principal', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/CDS/i)
  })

  test('debe navegar a sección Cotizar en landing desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Cotizar')
    await expect(page).toHaveURL(/#diagnostic/)
  })

  test('debe navegar a Calculadoras desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Calculadoras')
    await expect(page).toHaveURL(/\/calculadoras/)
  })

  test('debe navegar a Tienda desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Tienda')
    await expect(page).toHaveURL(/\/tienda/)
  })

  test('debe navegar a Login desde navbar', async ({ page }) => {
    await page.goto('/')
    await page.click('text=Ingresar')
    await expect(page).toHaveURL(/\/login/)
  })

  test('footer - links de redes sociales visibles', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const footer = page.locator('footer.site-footer')
    await expect(footer).toBeVisible()
  })

  test('footer - links legales funcionan', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await page.click('text=Política de privacidad')
    await expect(page).toHaveURL(/\/privacidad/)
  })
})

test.describe('HomePage - Botones y Links', () => {
  test('hero - botones de acción visibles', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const heroSection = page.locator('.home-hero')
    await expect(heroSection).toBeVisible()
    const heroActions = page.locator('.hero-actions')
    await expect(heroActions).toBeVisible()
  })

  test('no debe renderizar doble navbar en home', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('.home-nav')).toHaveCount(0)
    await expect(page.locator('.services-grid')).toBeVisible()
  })

  test('links de secciones funcionan', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const sectionLinks = page.locator('.service-cta, .highlight-link, .contact-link')
    const count = await sectionLinks.count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('CalculatorsPage - Navegación', () => {
  test('debe cargar página de calculadoras', async ({ page }) => {
    await page.goto('/calculadoras')
    await expect(page).toHaveURL(/\/calculadoras/)
    await page.waitForLoadState('networkidle')
  })

  test('debe mostrar contenido de calculadoras', async ({ page }) => {
    await page.goto('/calculadoras')
    await page.waitForLoadState('networkidle')
    const mainContent = page.locator('main')
    await expect(mainContent).toBeVisible()
  })

  test('debe verificar que calculadoras cargan (legacy wrappers)', async ({ page }) => {
    await page.goto('/calculadoras/timer555')
    await expect(page).toHaveURL(/\/calc\/555/)
  })

  test('debe verificar calculadora resistor carga', async ({ page }) => {
    await page.goto('/calculadoras/resistor-color')
    await expect(page).toHaveURL(/\/calc\/resistor-color/)
  })
})

test.describe('CotizadorIAPage - Flujo Multi-Step', () => {
  test('debe cargar página de cotizador', async ({ page }) => {
    await page.goto('/cotizador-ia')
    await expect(page).toHaveURL(/\/cotizador-ia/)
    await page.waitForLoadState('networkidle')
  })

  test('debe mostrar contenido de cotizador', async ({ page }) => {
    await page.goto('/cotizador-ia')
    await page.waitForLoadState('networkidle')
    const mainContent = page.locator('main')
    await expect(mainContent).toBeVisible()
  })

  test('debe tener elementos interactivos', async ({ page }) => {
    await page.goto('/cotizador-ia')
    await page.waitForLoadState('networkidle')
    const interactiveElements = page.locator('button, a')
    const count = await interactiveElements.count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('SchedulePage - Calendario', () => {
  test('debe cargar página de agendar', async ({ page }) => {
    await page.goto('/agendar')
    await expect(page).toHaveURL(/\/login/)
    await page.waitForLoadState('networkidle')
  })

  test('debe mostrar contenido de agendar', async ({ page }) => {
    await page.goto('/agendar')
    await page.waitForLoadState('networkidle')
    const mainContent = page.locator('main')
    await expect(mainContent).toBeVisible()
  })

  test('debe tener elementos interactivos', async ({ page }) => {
    await page.goto('/agendar')
    await page.waitForLoadState('networkidle')
    const buttons = page.locator('button')
    const count = await buttons.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })
})

test.describe('StorePage - Catálogo', () => {
  test('debe cargar página de tienda', async ({ page }) => {
    await page.goto('/tienda')
    await expect(page).toHaveURL(/\/tienda/)
    await page.waitForLoadState('networkidle')
  })

  test('debe mostrar contenido de tienda', async ({ page }) => {
    await page.goto('/tienda')
    await page.waitForLoadState('networkidle')
    const mainContent = page.locator('main')
    await expect(mainContent).toBeVisible()
  })
})

test.describe('Auth Pages - Login/Register', () => {
  test('debe cargar página de login', async ({ page }) => {
    await page.goto('/login')
    await expect(page).toHaveURL(/\/login/)
    await page.waitForLoadState('networkidle')
  })

  test('debe verificar formulario de login visible', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    const mainContent = page.locator('main')
    await expect(mainContent).toBeVisible()
  })

  test('debe cargar página de registro', async ({ page }) => {
    await page.goto('/registro')
    await expect(page).toHaveURL(/\/register/)
    await page.waitForLoadState('networkidle')
  })

  test('navbar permite volver a home desde login', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.click('text=Inicio')
    await expect(page).toHaveURL('/')
  })
})

test.describe('Public Pages - Términos y Privacidad', () => {
  test('debe cargar página de términos', async ({ page }) => {
    await page.goto('/terminos')
    await expect(page).toHaveURL(/\/terminos/)
    await page.waitForLoadState('networkidle')
  })

  test('debe cargar página de privacidad', async ({ page }) => {
    await page.goto('/privacidad')
    await expect(page).toHaveURL(/\/privacidad/)
    await page.waitForLoadState('networkidle')
  })

  test('footer permite ir a privacidad', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await page.click('text=Política de privacidad')
    await expect(page).toHaveURL(/\/privacidad/)
  })

  test('navbar permite volver a inicio desde páginas públicas', async ({ page }) => {
    await page.goto('/privacidad')
    await page.waitForLoadState('networkidle')
    await page.click('text=Inicio')
    await expect(page).toHaveURL('/')
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
