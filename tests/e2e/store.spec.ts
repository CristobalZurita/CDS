import { test, expect } from '@playwright/test'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

test.describe('public store flows', () => {
  test('catalog loads and cart persists locally', async ({ page }) => {
    const tracker = trackBrowserErrors(page)

    await page.goto('/tienda')
    await waitForAppToSettle(page)

    await expect(page.getByTestId('store-cart')).toBeVisible()
    await expect(page.getByTestId('store-product-card').first()).toBeVisible()

    const firstSku = await page.locator('.product-sku').first().innerText()
    await page.getByTestId('store-search-input').fill(firstSku.slice(0, Math.min(8, firstSku.length)))
    await expect(page.getByTestId('store-product-card').first()).toBeVisible()

    await page.getByTestId('store-add-to-cart').first().click()
    await expect(page.getByTestId('store-cart-item').first()).toBeVisible()
    await expect(page.getByTestId('store-checkout')).toBeEnabled()

    await page.getByTestId('store-shipping-select').selectOption('manual')
    await page.reload()
    await waitForAppToSettle(page)

    await expect(page.getByTestId('store-cart-item').first()).toBeVisible()
    await expect(page.getByTestId('store-shipping-select')).toHaveValue('manual')
    await expectNoBrowserErrors(tracker)
  })
})
