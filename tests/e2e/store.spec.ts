import { test, expect } from '@playwright/test'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

test.describe('public store flows', () => {
  test('catalog loads and global cart persists across navigation', async ({ page }) => {
    const tracker = trackBrowserErrors(page)

    await page.goto('/tienda')
    await waitForAppToSettle(page)

    await expect(page.getByTestId('store-cart')).toBeVisible()
    await expect(page.getByTestId('global-cart-trigger')).toBeVisible()
    await expect(page.getByTestId('store-product-card').first()).toBeVisible()

    const firstSku = await page.locator('.product-sku').first().innerText()
    await page.getByTestId('store-search-input').fill(firstSku.slice(0, Math.min(8, firstSku.length)))
    await expect(page.getByTestId('store-product-card').first()).toBeVisible()

    await page.locator('[data-testid="store-add-to-cart"]:not([disabled])').first().click()
    await expect(page.getByTestId('store-cart-item').first()).toBeVisible()
    await expect(page.getByTestId('store-checkout')).toBeEnabled()

    await page.getByTestId('store-shipping-select').selectOption('manual')
    await page.goto('/')
    await waitForAppToSettle(page)

    await page.getByTestId('global-cart-trigger').click()
    await expect(page.getByTestId('global-cart-item').first()).toBeVisible()
    await expect(page.getByTestId('global-cart-shipping-select')).toHaveValue('manual')
    await expectNoBrowserErrors(tracker)
  })
})

test.describe('authenticated store request flow', () => {
  test.use({ storageState: resolveAuthState('client') })

  test('client can submit a real purchase request from the global cart', async ({ page }) => {
    const tracker = trackBrowserErrors(page)

    await page.goto('/tienda')
    await waitForAppToSettle(page)

    await page.locator('[data-testid="store-add-to-cart"]:not([disabled])').first().click()
    await page.goto('/')
    await waitForAppToSettle(page)

    await page.getByTestId('global-cart-trigger').click()
    await expect(page.getByTestId('global-cart-item').first()).toBeVisible()
    await page.getByTestId('global-cart-checkout').click()

    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/ot-payments')
    await waitForAppToSettle(page)
    await expect(page.getByTestId('ot-payment-row').first()).toBeVisible()
    await expect(page.getByText(/TIENDA \/ SIN_OT|SIN_OT/).first()).toBeVisible()
    await expectNoBrowserErrors(tracker)
  })
})
