import { test, expect } from '@playwright/test'
import { loginFromUi } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

test('unauthenticated admin route redirects to login', async ({ page }) => {
  const tracker = trackBrowserErrors(page)

  await page.goto('/admin')
  await waitForAppToSettle(page)

  await expect(page).toHaveURL(/\/login\?redirect=(%2F|\/)admin$/)
  await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible()
  await expectNoBrowserErrors(tracker)
})

test('admin can log in from UI and reach admin dashboard', async ({ page }) => {
  const tracker = trackBrowserErrors(page)

  await page.goto('/admin')
  await waitForAppToSettle(page)
  await expect(page).toHaveURL(/\/login\?redirect=(%2F|\/)admin$/)

  await loginFromUi(page, 'e2e.admin@example.com', 'admin12')

  await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/admin')
  await waitForAppToSettle(page)
  await expect(page.getByTestId('admin-shell')).toBeVisible()
  await expectNoBrowserErrors(tracker)
})

test('client can log in from UI and reach dashboard', async ({ page }) => {
  const tracker = trackBrowserErrors(page)

  await page.goto('/login')

  await loginFromUi(page, 'e2e.client@example.com', 'client12')

  await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/dashboard')
  await waitForAppToSettle(page)
  await expect(page.getByRole('heading', { name: 'Mi Panel de Control' })).toBeVisible()
  await expectNoBrowserErrors(tracker)
})
