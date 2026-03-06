import { expect, test, type Page } from '@playwright/test'
import { waitForAppToSettle } from './helpers/page'

type LinkCandidate = {
  rawHref: string
  absHref: string
  text: string
}

const seedRoutes = ['/', '/tienda', '/calculadoras', '/privacidad']

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

test('store: volver al inicio navega correctamente', async ({ page }) => {
  await page.goto('/tienda')
  await waitForAppToSettle(page)

  const backToHome = page.getByRole('link', { name: /volver al inicio/i })
  await expect(backToHome).toBeVisible()
  await backToHome.click()

  await expect(page).toHaveURL(/\/$/)
})

test('visible internal links do not perform no-op clicks', async ({ page }) => {
  const failures: string[] = []

  for (const route of seedRoutes) {
    await page.goto(route)
    await waitForAppToSettle(page)

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
        failures.push(`${route} -> ${link.rawHref} [no se encontró anchor visible]`)
        continue
      }

      await Promise.race([page.waitForURL((url) => url.href !== before, { timeout: 2500 }).catch(() => null), page.waitForTimeout(1200)])

      const after = page.url()
      if (after === before) {
        failures.push(`${route} -> ${link.rawHref} [${link.text || 'sin texto'}]`)
      }
    }
  }

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
