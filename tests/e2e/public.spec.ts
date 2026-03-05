import { test, expect } from '@playwright/test'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

test('home smoke loads without browser errors', async ({ page }) => {
  const tracker = trackBrowserErrors(page)

  await page.goto('/')
  await waitForAppToSettle(page)

  await expect(page.locator('body')).toContainText('Cirujano de Sintetizadores')
  await expectNoBrowserErrors(tracker)
})
