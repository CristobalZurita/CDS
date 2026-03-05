import { test, expect, type Page } from '@playwright/test'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

async function advanceToDiagnosticMarkup(page: Page) {
  await page.goto('/cotizador-ia')
  await waitForAppToSettle(page)

  await page.getByTestId('quotation-brand-card').first().click()
  await page.getByTestId('quotation-instrument-card').first().click()
  await page.getByTestId('quotation-proceed').click()

  await expect(page.getByTestId('diagnostic-power-select')).toBeVisible()
  await page.getByTestId('diagnostic-power-select').selectOption('powers_on')
  await page.getByTestId('diagnostic-audio-select').selectOption('one_side')
  await page.getByTestId('diagnostic-step1-continue').click()
}

async function addMarkerAtCanvasCenter(page: Page) {
  const canvas = page.getByTestId('diagnostic-markup-canvas')

  await expect(canvas).toBeVisible()
  await expect.poll(async () => {
    return canvas.evaluate((node) => (node as HTMLCanvasElement).width)
  }).toBeGreaterThan(0)

  const box = await canvas.boundingBox()
  expect(box).not.toBeNull()

  await canvas.dblclick({
    position: {
      x: box!.width / 2,
      y: box!.height / 2,
    },
  })
}

test('known instrument flow reaches markup with catalog photos loaded', async ({ page }) => {
  const tracker = trackBrowserErrors(page)

  await advanceToDiagnosticMarkup(page)

  await expect(page.getByTestId('diagnostic-photo-tab').first()).toBeVisible()
  await addMarkerAtCanvasCenter(page)
  await expect(page.getByTestId('diagnostic-marker-count')).toContainText('(1)')
  await expect(page.getByTestId('diagnostic-step2-continue')).toBeEnabled()
  await expectNoBrowserErrors(tracker)
})

test('quotation flow reaches disclaimer step without captcha blocking in dev', async ({ page }) => {
  const tracker = trackBrowserErrors(page)

  await advanceToDiagnosticMarkup(page)

  await page.getByTestId('diagnostic-step2-continue').click()
  await page.getByTestId('diagnostic-step3-continue').click()

  await expect(page.getByText('IMPORTANTE - ESTIMACIÓN REFERENCIAL')).toBeVisible()
  await expect(page.getByTestId('turnstile-bypass')).toBeVisible()
  await expectNoBrowserErrors(tracker)
})
