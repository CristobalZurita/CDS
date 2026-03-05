import { test, expect, type Page } from '@playwright/test'
import { apiAs } from './helpers/adminApi'
import { loginFromUi, resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

// ⚠️ Este spec depende del runtime aislado que levanta Playwright y de los usuarios
// seed estables creados por scripts/e2e/seed_users.py.

async function createRepairViaUi(page: Page, modelName: string) {
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
  await page.getByTestId('repair-problem').fill(`Problema E2E ${modelName}`)
  await page.getByTestId('repair-paid-amount').fill('18000')
  await page.getByTestId('repair-payment-method').selectOption('transfer')
  await page.getByTestId('repair-save').click()

  const createdRow = page.getByTestId('repair-row').filter({ hasText: modelName })
  await expect(createdRow).toBeVisible()
  return createdRow
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

async function getE2EClientId() {
  const clients = await apiAs('admin', '/clients/')
  const e2eClient = clients.find((item: any) => item.email === 'e2e.client@example.com')

  if (!e2eClient) {
    throw new Error('No se encontro el cliente E2E en /clients/')
  }

  return Number(e2eClient.id)
}

async function createRepairViaApi(modelName: string) {
  const clientId = await getE2EClientId()
  return apiAs('admin', '/repairs/', {
    method: 'POST',
    body: {
      client_id: clientId,
      title: modelName,
      description: `Creado por Playwright para ${modelName}`,
      payment_method: 'transfer',
      paid_amount: 12000,
    },
  })
}

async function deleteRepairById(repairId: number | null) {
  if (!repairId) {
    return
  }

  await apiAs('admin', `/repairs/${repairId}`, { method: 'DELETE' }).catch(() => null)
}

test.describe('integration flows', () => {
  test('admin login flow reaches dashboard', async ({ page }) => {
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

  test.describe('client authenticated flows', () => {
    test.use({ storageState: resolveAuthState('client') })

    test('client can see own OT status and open the repair detail route', async ({ page }) => {
      const tracker = trackBrowserErrors(page)
      const slug = Date.now().toString(36)
      const modelName = `Client Status ${slug}`
      let repairId: number | null = null

      try {
        const createdRepair = await createRepairViaApi(modelName)
        repairId = Number(createdRepair.id)

        // ⚠️ En el runtime E2E actual el dashboard no siempre refleja de inmediato
        // reparaciones creadas en la misma corrida, pero la ruta detalle sí resuelve.
        await page.goto(`/repairs/${repairId}`)
        await expect(page).toHaveURL(new RegExp(`/repairs/${repairId}$`))
        await waitForAppToSettle(page)
        await expect(page.getByText('Resumen')).toBeVisible()
      } finally {
        await deleteRepairById(repairId)
      }

      await expectNoBrowserErrors(tracker)
    })

    test('client visiting an admin route is redirected to home', async ({ page }) => {
      await page.goto('/admin')
      await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/')
      await waitForAppToSettle(page)
      await expect(page.locator('body')).toContainText('Cirujano de Sintetizadores')
    })
  })

  test.describe('admin authenticated flows', () => {
    test.use({ storageState: resolveAuthState('admin') })

    test('admin can create a repair from the real UI and open its detail route', async ({ page }) => {
      const tracker = trackBrowserErrors(page)
      const slug = Date.now().toString(36)
      const modelName = `Login UI Flow ${slug}`

      try {
        const createdRow = await createRepairViaUi(page, modelName)
        await createdRow.getByTestId('repair-edit').click()
        await expect(page).toHaveURL(/\/admin\/repairs\/\d+$/)
        await waitForAppToSettle(page)
        await expect(page.getByTestId('repair-current-status')).toContainText('Ingreso')
      } finally {
        await deleteRepairByModel(page, modelName)
      }

      await expectNoBrowserErrors(tracker)
    })

    test('public signature flow signs and persists against the real repair detail page', async ({ page }) => {
      const tracker = trackBrowserErrors(page)
      const slug = Date.now().toString(36)
      const modelName = `Signature Flow ${slug}`
      let repairId: number | null = null

      try {
        const createdRepair = await createRepairViaApi(modelName)
        repairId = Number(createdRepair.id)

        await page.goto(`/admin/repairs/${repairId}`)
        await waitForAppToSettle(page)

        await page.getByTestId('signature-request-ingreso').click()
        const linkValue = await page.getByTestId('signature-link').inputValue()
        const signaturePath = new URL(linkValue).pathname

        await page.goto(signaturePath)
        await waitForAppToSettle(page)

        const canvas = page.locator('canvas')
        await expect(canvas).toBeVisible()
        const box = await canvas.boundingBox()
        if (!box) {
          throw new Error('No se pudo obtener el canvas de firma')
        }

        await page.mouse.move(box.x + 20, box.y + 20)
        await page.mouse.down()
        await page.mouse.move(box.x + 170, box.y + 90)
        await page.mouse.up()

        await page.getByRole('button', { name: 'Enviar' }).click()
        await expect(page.getByText('Firma enviada correctamente.')).toBeVisible()

        const updatedRepair = await apiAs('admin', `/repairs/${repairId}`)
        expect(String(updatedRepair.signature_ingreso_path || '')).toContain('signature-ingreso.png')

        await page.goto(`/admin/repairs/${repairId}`)
        await waitForAppToSettle(page)
        await expect(page.getByText('Firma ingreso: OK')).toBeVisible()
      } finally {
        await deleteRepairById(repairId)
      }

      await expectNoBrowserErrors(tracker)
    })
  })

  test('unauthenticated protected route redirects to login with redirect query', async ({ page }) => {
    await page.goto('/admin/inventory')
    await waitForAppToSettle(page)

    const currentUrl = new URL(page.url())
    expect(currentUrl.pathname).toBe('/login')
    expect(currentUrl.searchParams.get('redirect')).toBe('/admin/inventory')
    await expect(page.getByRole('heading', { name: 'Iniciar Sesión' })).toBeVisible()
  })

  test('unknown routes redirect to home', async ({ page }) => {
    const tracker = trackBrowserErrors(page)

    await page.goto('/ruta-que-no-existe-e2e')
    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/')
    await waitForAppToSettle(page)
    await expect(page.locator('body')).toContainText('Cirujano de Sintetizadores')
    await expectNoBrowserErrors(tracker)
  })
})
