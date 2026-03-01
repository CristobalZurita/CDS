import { test, expect, type Browser, type Page } from '@playwright/test'
import { apiAs } from './helpers/adminApi'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

async function createRepairForE2EClient(page: Page) {
  const slug = Date.now().toString(36)
  const modelName = `Client Flow ${slug}`

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
  await page.getByTestId('repair-problem').fill('Prueba cliente E2E')
  await page.getByTestId('repair-paid-amount').fill('15000')
  await page.getByTestId('repair-payment-method').selectOption('transfer')
  await page.getByTestId('repair-save').click()

  const createdRow = page.getByTestId('repair-row').filter({ hasText: modelName })
  await expect(createdRow).toBeVisible()
  await createdRow.getByTestId('repair-edit').click()
  await expect(page).toHaveURL(/\/admin\/repairs\/\d+$/)

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

test.describe('public deep flows', () => {
  test('contact form works from the public home page', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const email = `newsletter.${Date.now()}@example.com`

    await page.goto('/')
    await waitForAppToSettle(page)
    await page.getByTestId('contact-form').scrollIntoViewIfNeeded()
    await page.getByTestId('contact-name').fill('Cliente Publico')
    await page.getByTestId('contact-email').fill(email)
    await page.getByTestId('contact-subject').fill(`Consulta ${Date.now().toString(36)}`)
    await page.getByTestId('contact-message').fill('Mensaje E2E de contacto para validar persistencia.')
    await page.locator('#foxy-contact-form button[type="submit"]').click()

    await expect(page.getByTestId('contact-success')).toBeVisible()
    await expect(page.getByTestId('contact-success-email')).toContainText(email)

    const messages = await apiAs('admin', '/contact/messages')
    expect(messages.some((item: any) => item.email === email)).toBe(true)
    await expectNoBrowserErrors(tracker)
  })
})

test.describe('client deep flows', () => {
  test.use({ storageState: resolveAuthState('client') })

  test('client can update profile from the UI and restore original values', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const original = await apiAs('client', '/client/profile')
    const nextPhone = `+569${String(Date.now()).slice(-8)}`
    const nextAddress = `Direccion E2E ${Date.now().toString(36)}`

    try {
      await page.goto('/profile')
      await waitForAppToSettle(page)

      await page.getByTestId('profile-edit-toggle').click()
      await page.getByTestId('profile-phone-input').fill(nextPhone)
      await page.getByTestId('profile-address-input').fill(nextAddress)
      await page.getByTestId('profile-save').click()

      await expect(page.getByText(nextAddress)).toBeVisible()

      await page.goto('/profile')
      await waitForAppToSettle(page)
      await expect(page.getByText(nextAddress)).toBeVisible()
      await expect(page.getByText(nextPhone)).toBeVisible()
      await expectNoBrowserErrors(tracker)
    } finally {
      await apiAs('client', '/client/profile', {
        method: 'PUT',
        body: {
          email: original.email,
          full_name: original.full_name,
          phone: original.phone,
          address: original.address,
        },
      }).catch(() => null)
    }
  })

  test('client can schedule an appointment from the UI and it is persisted in backend', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const before = await apiAs('admin', '/appointments/?limit=200').catch(() => [])
    let createdAppointmentId: number | null = null

    try {
      await page.goto('/agendar')
      await waitForAppToSettle(page)

      await page.getByTestId('schedule-next-month').click()
      const firstAvailableDay = page.locator('[data-testid="schedule-day"][data-disabled="false"]').first()
      await firstAvailableDay.click()
      await page.getByTestId('schedule-date-next').click()
      await page.getByTestId('schedule-time-slot').first().click()
      await page.getByTestId('schedule-time-next').click()
      await page.locator('input[type="checkbox"]').check()
      await expect(page.getByTestId('turnstile-bypass')).toBeVisible()
      await page.getByTestId('schedule-confirm').click()

      await expect(page.getByTestId('schedule-success')).toBeVisible()
      await expect(page.getByTestId('schedule-appointment-number')).toContainText('CIT-')

      const after = await apiAs('admin', '/appointments/?limit=200')
      const created = after.find((item: any) => !before.some((prev: any) => prev.id === item.id))
      expect(created).toBeTruthy()
      createdAppointmentId = created ? Number(created.id) : null
      expect(created?.email).toBe('e2e.client@example.com')
      expect(created?.fecha).toBeTruthy()
      expect(['Cita de diagnóstico', 'Instrumento: Synthesizer']).toContain(created?.mensaje)
      await expectNoBrowserErrors(tracker)
    } finally {
      if (createdAppointmentId) {
        await apiAs('admin', `/appointments/${createdAppointmentId}`, { method: 'DELETE' }).catch(() => null)
      }
    }
  })

  test('client can download closure pdf from a real repair detail page', async ({ browser }) => {
    await withAdminPage(browser, async (adminPage) => {
      const { modelName, repairId } = await createRepairForE2EClient(adminPage)

      const clientContext = await browser.newContext({ storageState: resolveAuthState('client') })
      const clientPage = await clientContext.newPage()
      try {
        const tracker = trackBrowserErrors(clientPage)
        await clientPage.goto(`/repairs/${repairId}`)
        await waitForAppToSettle(clientPage)

        const downloadPromise = clientPage.waitForEvent('download')
        await clientPage.getByTestId('repair-download').click()
        const download = await downloadPromise

        expect(download.suggestedFilename()).toContain('CIERRE_CLIENTE_')
        await expectNoBrowserErrors(tracker)
      } finally {
        await clientContext.close()
        await deleteRepairByModel(adminPage, modelName)
      }
    })
  })
})
