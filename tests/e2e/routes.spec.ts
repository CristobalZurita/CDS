import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

const publicRoutes = [
  '/',
  '/license',
  '/policy',
  '/terminos',
  '/privacidad',
  '/login',
  '/register',
  '/password-reset',
  '/cotizador-ia',
  '/calculadoras',
  '/tienda',
  '/calc/555',
  '/calc/resistor-color',
  '/calc/smd-capacitor',
  '/calc/smd-resistor',
  '/calc/ohms-law',
  '/calc/temperature',
  '/calc/number-system',
  '/calc/length',
  '/calc/awg',
]

const clientRoutes = [
  '/dashboard',
  '/ot-payments',
  '/repairs',
  '/profile',
  '/agendar',
]

const adminRoutes = [
  '/admin',
  '/admin/inventory',
  '/admin/inventory/unified',
  '/admin/clients',
  '/admin/repairs',
  '/admin/quotes',
  '/admin/categories',
  '/admin/contact',
  '/admin/newsletter',
  '/admin/appointments',
  '/admin/tickets',
  '/admin/purchase-requests',
  '/admin/manuals',
  '/admin/stats',
  '/admin/archive',
]

test.describe('public routes smoke', () => {
  for (const route of publicRoutes) {
    test(`loads ${route}`, async ({ page }) => {
      const tracker = trackBrowserErrors(page)

      await page.goto(route)
      await waitForAppToSettle(page)
      await expect(page.locator('body')).toBeVisible()
      await expect(page).toHaveURL(new RegExp(route === '/' ? '/$' : route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
      await expectNoBrowserErrors(tracker)
    })
  }
})

test.describe('client routes smoke', () => {
  test.use({ storageState: resolveAuthState('client') })

  for (const route of clientRoutes) {
    test(`loads ${route}`, async ({ page }) => {
      const tracker = trackBrowserErrors(page)

      await page.goto(route)
      await waitForAppToSettle(page)
      await expect(page.locator('body')).toBeVisible()
      await expect(page).toHaveURL(new RegExp(route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
      await expectNoBrowserErrors(tracker)
    })
  }
})

test.describe('admin routes smoke', () => {
  test.use({ storageState: resolveAuthState('admin') })

  for (const route of adminRoutes) {
    test(`loads ${route}`, async ({ page }) => {
      const tracker = trackBrowserErrors(page)

      await page.goto(route)
      await waitForAppToSettle(page)
      await expect(page.locator('body')).toBeVisible()
      await expect(page).toHaveURL(new RegExp(route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
      await expectNoBrowserErrors(tracker)
    })
  }
})
