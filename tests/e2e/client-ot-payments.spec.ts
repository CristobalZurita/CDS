import { Buffer } from 'node:buffer'
import { test, expect } from '@playwright/test'
import { apiAs } from './helpers/adminApi'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

const proofImage = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn2jVQAAAAASUVORK5CYII=',
  'base64'
)

test.describe('client OT payment flows', () => {
  test.use({ storageState: resolveAuthState('client') })

  test('client can submit a deposit proof from OT payments', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const clients = await apiAs('admin', '/clients/')
    const client = clients.find((entry: any) => entry.email === 'e2e.client@example.com')

    expect(client).toBeTruthy()

    const purchaseRequest = await apiAs('admin', '/purchase-requests/', {
      method: 'POST',
      body: {
        client_id: client.id,
        notes: `Solicitud cliente ${slug}`,
        items: [
          {
            sku: `E2E-${slug}`,
            name: `Modulo ${slug}`,
            quantity: 1,
            unit_price: 24990,
          },
        ],
      },
    })

    const requestId = Number(purchaseRequest.id)
    const depositReference = `DEP-${slug}`

    try {
      await apiAs('admin', `/purchase-requests/${requestId}/request-payment`, {
        method: 'POST',
        body: {
          amount: 24990,
          due_days: 4,
          instruction: 'Deposita y sube comprobante desde tu panel.',
        },
      })

      await page.goto('/ot-payments')
      await waitForAppToSettle(page)

      const requestRow = page.getByTestId('ot-payment-row').filter({ hasText: `Solicitud #${requestId}` })
      await expect(requestRow).toBeVisible()

      await requestRow.getByTestId('ot-payment-amount').fill('24990')
      await requestRow.getByTestId('ot-payment-reference').fill(depositReference)
      await requestRow.getByTestId('ot-payment-notes').fill('Comprobante enviado desde Playwright')
      await requestRow.getByTestId('ot-payment-file').setInputFiles({
        name: 'deposito.png',
        mimeType: 'image/png',
        buffer: proofImage,
      })
      await requestRow.getByTestId('ot-payment-submit').click()

      const submittedRow = page.getByTestId('ot-payment-row').filter({ hasText: `Solicitud #${requestId}` })
      await expect(submittedRow).toContainText('proof_submitted')
      await expect(submittedRow.getByTestId('ot-payment-proof-link')).toBeVisible()

      const detail = await apiAs('admin', `/purchase-requests/${requestId}/detail`)
      expect(detail.latest_payment?.deposit_reference).toBe(depositReference)
      expect(detail.latest_payment?.proof_path).toBeTruthy()
      await expectNoBrowserErrors(tracker)
    } finally {
      await apiAs('admin', `/purchase-requests/${requestId}`, { method: 'DELETE' }).catch(() => null)
    }
  })
})
