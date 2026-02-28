import { test, expect, type Page } from '@playwright/test'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

async function advanceToDiagnosticMarkup(page: Page) {
  await page.goto('/cotizador-ia')
  await waitForAppToSettle(page)

  await page.getByTestId('quotation-brand-card').first().click()
  await page.getByTestId('quotation-instrument-card').first().click()
  await page.getByTestId('quotation-proceed').click()

  const brandSelect = page.getByTestId('diagnostic-brand-select')
  await brandSelect.selectOption({ index: 1 })

  const modelSelect = page.getByTestId('diagnostic-model-select')
  await expect.poll(async () => modelSelect.locator('option').count()).toBeGreaterThan(1)
  await modelSelect.selectOption({ index: 1 })

  await page.getByTestId('diagnostic-step0-continue').click()
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
  await addMarkerAtCanvasCenter(page)

  await page.getByTestId('diagnostic-step2-continue').click()
  await page.getByLabel('He leído y acepto que esta es una cotización preliminar').check()
  await page.getByRole('button', { name: 'Enviar diagnóstico' }).click()

  await expect(page.getByText('IMPORTANTE - LEA ANTES DE CONTINUAR')).toBeVisible()
  await expect(page.getByTestId('turnstile-bypass')).toBeVisible()
  await expectNoBrowserErrors(tracker)
})
