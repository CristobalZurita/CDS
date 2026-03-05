import { Buffer } from 'node:buffer'
import { test, expect } from '@playwright/test'
import { loginFromUi, resolveAuthState } from './helpers/auth'
import { waitForAppToSettle } from './helpers/page'

const invalidTokenImage = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn2jVQAAAAASUVORK5CYII=',
  'base64'
)

test('invalid credentials show a visible login error', async ({ page }) => {
  await page.goto('/login')
  await waitForAppToSettle(page)

  await loginFromUi(page, 'e2e.client@example.com', 'wrongpass')

  await expect(page.getByTestId('login-error')).toContainText('Email o contraseña incorrectos')
})

test('unknown routes redirect back to home', async ({ page }) => {
  await page.goto('/ruta-que-no-existe')
  await waitForAppToSettle(page)

  await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/')
})

test('invalid photo upload tokens surface a user-facing error', async ({ page }) => {
  await page.goto('/photo-upload/token-invalido')
  await waitForAppToSettle(page)

  await page.getByTestId('photo-upload-file').setInputFiles({
    name: 'invalid-token.png',
    mimeType: 'image/png',
    buffer: invalidTokenImage,
  })
  await page.getByTestId('photo-upload-caption').fill('Foto de prueba con token inválido')
  await page.getByTestId('photo-upload-submit').click()

  await expect(page.getByTestId('photo-upload-status')).toContainText('No se pudo enviar la foto.')
})

test.describe('authenticated client guards', () => {
  test.use({ storageState: resolveAuthState('client') })

  test('client users are redirected away from admin routes', async ({ page }) => {
    await page.goto('/admin')
    await waitForAppToSettle(page)

    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/')
  })

  test('client users are redirected away from guest-only login route', async ({ page }) => {
    await page.goto('/login')
    await waitForAppToSettle(page)

    await expect.poll(async () => page.evaluate(() => window.location.pathname)).toBe('/dashboard')
  })

  test('schedule page shows backend 422 validation errors without fake success', async ({ page }) => {
    await page.route('**/api/v1/appointments/', async (route) => {
      await route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'La fecha ya no está disponible' }),
      })
    })

    await page.goto('/agendar')
    await waitForAppToSettle(page)

    await page.getByTestId('schedule-next-month').click()
    await page.locator('[data-testid="schedule-day"][data-disabled="false"]').first().click()
    await page.getByTestId('schedule-date-next').click()
    await page.getByTestId('schedule-time-slot').first().click()
    await page.getByTestId('schedule-time-next').click()
    await page.locator('input[type="checkbox"]').check()
    await page.getByTestId('schedule-confirm').click()

    await expect(page.getByTestId('schedule-error')).toContainText('La fecha ya no está disponible')
    await expect(page.getByTestId('schedule-success')).toHaveCount(0)
  })

  test('OT payments page shows a visible error when the backend load fails with 500', async ({ page }) => {
    await page.route('**/api/v1/client/purchase-requests', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Error interno OT' }),
      })
    })

    await page.goto('/ot-payments')
    await waitForAppToSettle(page)

    await expect(page.getByTestId('ot-payments-error')).toContainText('Error interno OT')
  })

  test('OT payments page surfaces 403 errors when a deposit proof is rejected', async ({ page }) => {
    await page.route('**/api/v1/client/purchase-requests', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 99,
            status: 'pending_payment',
            repair_code: 'CDS-010-OT-099',
            requested_amount: 24000,
            payment_due_date: '2026-03-10T00:00:00Z',
            items_count: 1,
            notes: 'Pago pendiente de autorización',
            latest_payment: {
              admin_notes: 'Deposita y sube tu comprobante',
              proof_path: null,
            },
          },
        ]),
      })
    })

    await page.route('**/api/v1/client/purchase-requests/99/deposit-proof', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'No autorizado para esta solicitud de compra' }),
      })
    })

    await page.goto('/ot-payments')
    await waitForAppToSettle(page)

    const requestRow = page.getByTestId('ot-payment-row').filter({ hasText: 'Solicitud #99' })
    await expect(requestRow).toBeVisible()
    await requestRow.getByTestId('ot-payment-reference').fill('DEP-E2E-403')
    await requestRow.getByTestId('ot-payment-submit').click()

    await expect(page.getByTestId('ot-payments-error')).toContainText('No autorizado para esta solicitud de compra')
  })
})
