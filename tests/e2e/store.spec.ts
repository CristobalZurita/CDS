import { test, expect } from '@playwright/test'
import { apiAs } from './helpers/adminApi'
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

  test('store checkout reserves stock and admin completion consumes it', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const category = await apiAs('admin', '/categories/', {
      method: 'POST',
      body: {
        name: `Categoria tienda ${slug}`,
        description: 'Categoria E2E para tienda',
      },
    })

    const product = await apiAs('admin', '/inventory/', {
      method: 'POST',
      body: {
        name: `000 Resistencia tienda ${slug}`,
        sku: `STORE-${slug.toUpperCase()}`,
        category_id: category.id,
        price: 2490,
        stock: 12,
        min_quantity: 3,
        enabled: true,
        store_visible: true,
      },
    })
    const initialInventory = await apiAs('admin', `/inventory/${product.id}`)

    await page.goto('/tienda')
    await waitForAppToSettle(page)
    await page.getByTestId('store-search-input').fill(product.sku)
    await expect(page.getByTestId('store-product-card').filter({ hasText: product.sku })).toBeVisible()
    await page.getByTestId('store-add-to-cart').click()
    await page.getByTestId('store-add-to-cart').click()
    await page.getByTestId('global-cart-trigger').click()
    await expect(page.getByTestId('global-cart-item').filter({ hasText: product.sku })).toContainText(product.sku)
    await page.getByTestId('global-cart-checkout').click()

    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/ot-payments')
    await waitForAppToSettle(page)

    const requests = await apiAs('admin', '/purchase-requests/')
    const createdRequest = [...requests]
      .reverse()
      .find((request: any) => Array.isArray(request.items) && request.items.some((item: any) => item.sku === product.sku))

    expect(createdRequest).toBeTruthy()
    const createdItem = createdRequest.items.find((item: any) => item.sku === product.sku)
    expect(createdItem.quantity).toBe(2)
    expect(createdItem.reserved_quantity).toBe(2)

    const reservedInventory = await apiAs('admin', `/inventory/${product.id}`)
    expect(reservedInventory.quantity_reserved).toBe(2)
    expect(reservedInventory.stock).toBe(initialInventory.stock)

    await apiAs('admin', `/purchase-requests/${createdRequest.id}`, {
      method: 'PATCH',
      body: {
        status: 'received',
      },
    })

    const fulfilledInventory = await apiAs('admin', `/inventory/${product.id}`)
    expect(fulfilledInventory.quantity_reserved).toBe(0)
    expect(fulfilledInventory.stock).toBe(initialInventory.stock - 2)
    await expectNoBrowserErrors(tracker)
  })
})
