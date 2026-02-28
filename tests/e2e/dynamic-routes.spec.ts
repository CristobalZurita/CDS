import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { test, expect, type Browser, type Page } from '@playwright/test'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

const currentDir = path.dirname(fileURLToPath(import.meta.url))
const samplePhotoPath = path.resolve(currentDir, '..', '..', 'public', 'images', 'logo', 'logo_square_002.webp')

async function createRepairForE2EClient(page: Page) {
  const slug = Date.now().toString(36)
  const modelName = `Route E2E ${slug}`

  await page.goto('/admin/repairs')
  await waitForAppToSettle(page)

  await page.getByTestId('repairs-new').click()
  const clientValue = await page
    .getByTestId('repair-client')
    .locator('option')
    .filter({ hasText: 'E2E Client' })
    .first()
    .getAttribute('value')

  if (!clientValue) {
    throw new Error('No se encontro el cliente E2E en el selector de reparaciones')
  }

  await page.getByTestId('repair-client').selectOption(clientValue)
  await page.getByTestId('repair-model').fill(modelName)
  await page.getByTestId('repair-problem').fill('Prueba de ruta dinámica E2E')
  await page.getByTestId('repair-paid-amount').fill('10000')
  await page.getByTestId('repair-payment-method').selectOption('transfer')
  await page.getByTestId('repair-save').click()

  const createdRow = page.getByTestId('repair-row').filter({ hasText: modelName })
  await expect(createdRow).toBeVisible()
  await createdRow.getByTestId('repair-edit').click()
  await expect(page).toHaveURL(/\/admin\/repairs\/\d+$/)
  await waitForAppToSettle(page)

  const match = page.url().match(/\/admin\/repairs\/(\d+)$/)
  if (!match) {
    throw new Error(`No se pudo obtener el ID de la reparación desde ${page.url()}`)
  }

  return { modelName, repairId: Number(match[1]) }
}

async function deleteRepairByModel(page: Page, modelName: string) {
  page.on('dialog', (dialog) => dialog.accept())

  await page.goto('/admin/repairs')
  await waitForAppToSettle(page)
  await page.getByTestId('repairs-search').fill(modelName)
  await page.waitForTimeout(300)

  const row = page.getByTestId('repair-row').filter({ hasText: modelName }).first()
  if ((await row.count()) === 0) {
    return
  }

  await row.getByTestId('repair-delete').click()
  await expect(page.getByTestId('repair-row').filter({ hasText: modelName })).toHaveCount(0)
}

async function withAdminPage(browser: Browser, run: (page: Page) => Promise<void>) {
  const context = await browser.newContext({ storageState: resolveAuthState('admin') })
  const page = await context.newPage()
  try {
    await run(page)
  } finally {
    await context.close()
  }
}

test.describe('dynamic routes', () => {
  test('admin repair detail route resolves from a real repair', async ({ browser }) => {
    await withAdminPage(browser, async (page) => {
      const tracker = trackBrowserErrors(page)
      const { modelName } = await createRepairForE2EClient(page)

      await expect(page.getByTestId('repair-current-status')).toBeVisible()
      await expect(page.getByTestId('signature-request-ingreso')).toBeVisible()
      await expect(page.getByTestId('photo-request')).toBeVisible()

      await deleteRepairByModel(page, modelName)
      await expectNoBrowserErrors(tracker)
    })
  })

  test('client repair detail route resolves for an owned repair', async ({ browser }) => {
    let modelName = ''

    await withAdminPage(browser, async (adminPage) => {
      const created = await createRepairForE2EClient(adminPage)
      modelName = created.modelName

      const clientContext = await browser.newContext({ storageState: resolveAuthState('client') })
      const clientPage = await clientContext.newPage()
      try {
        const tracker = trackBrowserErrors(clientPage)
        await clientPage.goto(`/repairs/${created.repairId}`)
        await waitForAppToSettle(clientPage)

        await expect(clientPage.locator('h1')).toBeVisible()
        await expect(clientPage.getByText('Resumen')).toBeVisible()
        await expect(clientPage).toHaveURL(new RegExp(`/repairs/${created.repairId}$`))
        await expectNoBrowserErrors(tracker)
      } finally {
        await clientContext.close()
      }

      await deleteRepairByModel(adminPage, modelName)
    })
  })

  test('signature token route accepts a real signature submission', async ({ browser }) => {
    await withAdminPage(browser, async (page) => {
      const tracker = trackBrowserErrors(page)
      const { modelName } = await createRepairForE2EClient(page)

      await page.getByTestId('signature-request-ingreso').click()
      const linkValue = await page.getByTestId('signature-link').inputValue()
      const routePath = new URL(linkValue).pathname

      await page.goto(routePath)
      await waitForAppToSettle(page)

      const canvas = page.locator('canvas')
      await expect(canvas).toBeVisible()
      const box = await canvas.boundingBox()
      if (!box) {
        throw new Error('No se pudo obtener el canvas de firma')
      }

      await page.mouse.move(box.x + 20, box.y + 20)
      await page.mouse.down()
      await page.mouse.move(box.x + 160, box.y + 80)
      await page.mouse.up()

      await page.getByRole('button', { name: 'Enviar' }).click()
      await expect(page.getByText('Firma enviada correctamente.')).toBeVisible()

      await withAdminPage(browser, async (cleanupPage) => {
        await deleteRepairByModel(cleanupPage, modelName)
      })
      await expectNoBrowserErrors(tracker)
    })
  })

  test('photo upload token route accepts a real image upload', async ({ browser }) => {
    await withAdminPage(browser, async (page) => {
      const tracker = trackBrowserErrors(page)
      const { modelName } = await createRepairForE2EClient(page)

      await page.getByTestId('photo-request').click()
      const linkValue = await page.getByTestId('photo-upload-link').inputValue()
      const routePath = new URL(linkValue).pathname

      await page.goto(routePath)
      await waitForAppToSettle(page)

      await page.locator('input[type="file"]').setInputFiles(samplePhotoPath)
      await page.locator('input[type="text"]').fill('Foto E2E')
      await page.getByRole('button', { name: 'Enviar foto' }).click()
      await expect(page.getByText('Foto enviada correctamente.')).toBeVisible()

      await withAdminPage(browser, async (cleanupPage) => {
        await deleteRepairByModel(cleanupPage, modelName)
      })
      await expectNoBrowserErrors(tracker)
    })
  })
})
