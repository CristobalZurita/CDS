import { expect, test, type Browser, type Page } from '@playwright/test'
import { waitForAppToSettle } from './helpers/page'
import { resolveAuthState } from './helpers/auth'

type LinkCandidate = {
  rawHref: string
  absHref: string
  text: string
}

// Rutas públicas base del sitio (sin autenticación obligatoria).
// Se mantienen explícitas para auditar navegación real de punta a punta.
const seedRoutes = [
  '/',
  '/tienda',
  '/calculadoras',
  '/cotizador-ia',
  '/privacidad',
  '/terminos',
  '/login',
]

const clientSeedRoutes = ['/dashboard', '/repairs', '/profile', '/ot-payments']
const adminSeedRoutes = ['/admin', '/admin/repairs', '/admin/inventory', '/admin/clients']

async function collectInternalLinks(page: Page): Promise<LinkCandidate[]> {
  return page.locator('a[href]:visible').evaluateAll((nodes) => {
    const currentOrigin = window.location.origin
    const seen = new Set<string>()
    const links: LinkCandidate[] = []

    const toText = (node: Element) => (node.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80)

    for (const node of nodes) {
      const hrefAttr = (node.getAttribute('href') || '').trim()
      const target = (node.getAttribute('target') || '').trim().toLowerCase()
      if (!hrefAttr || target === '_blank') {
        continue
      }

      if (!hrefAttr.startsWith('/') && !hrefAttr.startsWith('http')) {
        continue
      }

      let resolved: URL
      try {
        resolved = new URL(hrefAttr, window.location.href)
      } catch {
        continue
      }

      if (resolved.origin !== currentOrigin) {
        continue
      }

      if (seen.has(hrefAttr)) {
        continue
      }
      seen.add(hrefAttr)

      links.push({
        rawHref: hrefAttr,
        absHref: resolved.href,
        text: toText(node),
      })
    }

    return links.slice(0, 12)
  })
}

async function clickFirstVisibleAnchorByHref(page: Page, rawHref: string): Promise<boolean> {
  return page.evaluate((href) => {
    const isVisible = (el: Element) => {
      const rect = (el as HTMLElement).getBoundingClientRect()
      return rect.width > 0 && rect.height > 0
    }

    const anchors = Array.from(document.querySelectorAll('a[href]'))
    const target = anchors.find((anchor) => anchor.getAttribute('href') === href && isVisible(anchor))
    if (!target) {
      return false
    }

    ;(target as HTMLElement).click()
    return true
  }, rawHref)
}

function normalizeRoutePath(pathOrUrl: string) {
  const parsed = new URL(pathOrUrl, 'http://127.0.0.1')
  const normalized = parsed.pathname.replace(/\/+$/, '')
  return normalized || '/'
}

async function collectNoOpFailures(
  browser: Browser,
  routes: string[],
  scopeLabel: string,
  storageState?: string,
): Promise<string[]> {
  const failures: string[] = []
  const context = await browser.newContext(storageState ? { storageState } : {})

  try {
    for (const route of routes) {
      const page = await context.newPage()
      await page.goto(route)
      await waitForAppToSettle(page)

      const landedPath = normalizeRoutePath(page.url())
      const expectedPath = normalizeRoutePath(route)
      if (landedPath !== expectedPath) {
        failures.push(
          `[${scopeLabel}] ${route} [redirigido inesperadamente a ${landedPath}]`,
        )
        await page.close()
        continue
      }

      try {
        const links = await collectInternalLinks(page)
        for (const link of links) {
          await page.goto(route)
          await waitForAppToSettle(page)

          const before = page.url()
          if (link.absHref === before) {
            continue
          }

          const clicked = await clickFirstVisibleAnchorByHref(page, link.rawHref)
          if (!clicked) {
            await page.goto(link.absHref)
            await waitForAppToSettle(page)
            const afterFallback = page.url()
            if (afterFallback === before) {
              failures.push(`[${scopeLabel}] ${route} -> ${link.rawHref} [no se encontró anchor visible]`)
            }
            continue
          }

          await Promise.race([
            page.waitForURL((url) => url.href !== before, { timeout: 1800 }).catch(() => null),
            page.waitForTimeout(700),
          ])

          const after = page.url()
          if (after === before) {
            failures.push(`[${scopeLabel}] ${route} -> ${link.rawHref} [${link.text || 'sin texto'}]`)
          }
        }
      } catch (error: any) {
        failures.push(`[${scopeLabel}] ${route} [error de auditoria: ${error?.message || String(error)}]`)
      } finally {
        await page.close()
      }
    }
  } finally {
    await context.close()
  }

  return failures
}

test('store: volver al inicio navega correctamente', async ({ page }) => {
  await page.goto('/tienda')
  await waitForAppToSettle(page)

  const backToHome = page.getByRole('link', { name: /volver al inicio/i })
  await expect(backToHome).toBeVisible()
  await backToHome.click()

  await expect(page).toHaveURL(/\/$/)
})

test('visible internal links do not perform no-op clicks', async ({ browser }) => {
  const failures = await collectNoOpFailures(browser, seedRoutes, 'public')

  expect(
    failures,
    failures.length
      ? `Links con click no-op detectados:\n${failures.join('\n')}`
      : 'Sin links no-op',
  ).toEqual([])
})

test('authenticated client links do not perform no-op clicks', async ({ browser }) => {
  const failures = await collectNoOpFailures(browser, clientSeedRoutes, 'client', resolveAuthState('client'))
  expect(
    failures,
    failures.length
      ? `Links con click no-op detectados:\n${failures.join('\n')}`
      : 'Sin links no-op',
  ).toEqual([])
})

test('authenticated admin links do not perform no-op clicks', async ({ browser }) => {
  const failures = await collectNoOpFailures(browser, adminSeedRoutes, 'admin', resolveAuthState('admin'))

  expect(
    failures,
    failures.length
      ? `Links con click no-op detectados:\n${failures.join('\n')}`
      : 'Sin links no-op',
  ).toEqual([])

})

test('store navbar keeps real escape routes and avoids stale section links', async ({ page }) => {
  await page.goto('/')
  await waitForAppToSettle(page)

  await page.goto('/tienda')
  await waitForAppToSettle(page)

  const nav = page.locator('nav').first()
  await expect(nav).toBeVisible()
  await expect(nav.locator('a[href="/"]').first()).toBeVisible()
  await expect(nav.locator('a[href="/calculadoras"]').first()).toBeVisible()
  await expect(nav.locator('a[href^="#"]')).toHaveCount(0)
})

test('social links point to real external destinations', async ({ page }) => {
  await page.goto('/')
  await waitForAppToSettle(page)

  const instagram = page.locator('a[href*="instagram.com/cirujanodesintetizadores"]').first()
  const facebook = page.locator('a[href*="facebook.com/Cirujanodesintetizadores"]').first()
  const whatsapp = page.locator('a[href*="wa.me/56982957538"]').first()

  await expect(instagram).toBeVisible()
  await expect(facebook).toBeVisible()
  await expect(whatsapp).toHaveAttribute('href', /https:\/\/wa\.me\/56982957538\/?/)

  await expect(instagram).toHaveAttribute('href', /https:\/\/www\.instagram\.com\/cirujanodesintetizadores\/?/)
  await expect(facebook).toHaveAttribute('href', /https:\/\/www\.facebook\.com\/Cirujanodesintetizadores\/?/)
  await expect(instagram).toHaveAttribute('target', '_blank')
  await expect(facebook).toHaveAttribute('target', '_blank')
  await expect(whatsapp).toHaveAttribute('target', '_blank')
})
