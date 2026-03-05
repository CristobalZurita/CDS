import { test, expect } from '@playwright/test'
import { apiAs, publicApi } from './helpers/adminApi'
import { resolveAuthState } from './helpers/auth'
import { expectNoBrowserErrors, trackBrowserErrors, waitForAppToSettle } from './helpers/page'

test.describe('admin extended CRUD flows', () => {
  test.use({ storageState: resolveAuthState('admin') })

  test('quotes lifecycle works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const problem = `Problema quote ${slug}`
    let quoteId: number | null = null
    let repairId: number | null = null

    page.on('dialog', (dialog) => dialog.accept())

    try {
      const createdQuote = await apiAs('admin', '/diagnostic/quotes', {
        method: 'POST',
        body: {
          client_name: 'E2E Client',
          client_email: 'e2e.client@example.com',
          client_phone: '+56922222222',
          problem_description: problem,
          diagnosis: 'Fuente intermitente',
          estimated_total: 120000,
          estimated_parts_cost: 20000,
          estimated_labor_cost: 100000,
          items: [
            {
              item_type: 'service',
              name: `Servicio ${slug}`,
              quantity: 1,
              unit_price: 120000,
            },
          ],
        },
      })

      quoteId = Number(createdQuote.id)

      await page.goto('/admin/quotes')
      await waitForAppToSettle(page)
      await page.getByTestId('quotes-search').fill(createdQuote.quote_number)
      await page.getByTestId('quotes-refresh').click()

      const initialCard = page.getByTestId('quote-card').filter({ hasText: createdQuote.quote_number })
      await expect(initialCard).toBeVisible()
      await initialCard.getByTestId('quote-send').click()

      const sentCard = page.getByTestId('quote-card').filter({ hasText: createdQuote.quote_number })
      await expect(sentCard).toBeVisible()
      await sentCard.getByTestId('quote-approve').click()

      const approvedCard = page.getByTestId('quote-card').filter({ hasText: createdQuote.quote_number })
      await expect(approvedCard).toBeVisible()
      await approvedCard.getByTestId('quote-create-repair').click()

      await expect(page).toHaveURL(/\/admin\/repairs\/\d+$/)
      const match = page.url().match(/\/admin\/repairs\/(\d+)$/)
      repairId = match ? Number(match[1]) : null
      expect(repairId).not.toBeNull()
      await expectNoBrowserErrors(tracker)
    } finally {
      if (repairId) {
        await apiAs('admin', `/repairs/${repairId}`, { method: 'DELETE' }).catch(() => null)
      }
      if (quoteId) {
        await apiAs('admin', `/diagnostic/quotes/${quoteId}`, { method: 'DELETE' }).catch(() => null)
      }
    }

  })

  test('appointments CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36).replace(/[0-9]/g, 'a')
    const email = `appointment.${Date.now()}@example.com`
    const name = `Cita Prueba ${slug}`
    const createdAppointment = await publicApi('/appointments/', {
      method: 'POST',
      body: {
        nombre: name,
        email,
        telefono: '+56933333333',
        fecha: new Date(Date.now() + 86_400_000).toISOString(),
        mensaje: `Agenda ${slug}`,
        turnstile_token: 'e2e-bypass',
      },
    })

    page.on('dialog', (dialog) => dialog.accept())

    await page.goto('/admin/appointments')
    await waitForAppToSettle(page)

    const appointmentRow = page.getByTestId('appointment-row').filter({ hasText: email })
    await expect(appointmentRow).toBeVisible()
    await appointmentRow.getByTestId('appointment-confirm').click()
    await expect(page.getByTestId('appointment-row').filter({ hasText: email })).toContainText('Confirmada')

    const confirmedRow = page.getByTestId('appointment-row').filter({ hasText: email })
    await confirmedRow.getByTestId('appointment-cancel').click()
    await expect(page.getByTestId('appointment-row').filter({ hasText: email })).toContainText('Cancelada')

    await page.getByTestId('appointment-row').filter({ hasText: email }).getByTestId('appointment-delete').click()
    await expect(page.getByTestId('appointment-row').filter({ hasText: email })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)

    await apiAs('admin', `/appointments/${createdAppointment.id}`, { method: 'DELETE' }).catch(() => null)
  })

  test('tickets CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const subject = `Ticket E2E ${slug}`

    page.on('dialog', (dialog) => dialog.accept())

    await page.goto('/admin/tickets')
    await waitForAppToSettle(page)

    await page.getByTestId('tickets-new').click()
    await page.getByTestId('wizard-next').click()
    await page.getByTestId('ticket-subject').fill(subject)
    await page.getByTestId('ticket-priority').selectOption('high')
    await page.getByTestId('ticket-message').fill(`Mensaje ${slug}`)
    await page.getByTestId('wizard-next').click()
    await expect(page.getByTestId('ticket-result')).toContainText('Ticket creado')
    await page.getByTestId('wizard-next').click()

    const createdRow = page.getByTestId('ticket-row').filter({ hasText: subject })
    await expect(createdRow).toBeVisible()
    await createdRow.getByTestId('ticket-status-select').selectOption('closed')
    await expect(page.getByTestId('ticket-row').filter({ hasText: subject })).toContainText('closed')

    await page.getByTestId('ticket-row').filter({ hasText: subject }).getByTestId('ticket-delete').click()
    await expect(page.getByTestId('ticket-row').filter({ hasText: subject })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)
  })

  test('purchase requests CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)

    page.on('dialog', (dialog) => dialog.accept())

    await page.goto('/admin/purchase-requests')
    await waitForAppToSettle(page)

    await page.getByTestId('purchase-requests-new').click()
    await page.getByTestId('purchase-request-notes').fill(`Notas ${slug}`)
    await page.getByTestId('wizard-next').click()

    const firstItem = page.getByTestId('purchase-request-item-row').first()
    await firstItem.getByTestId('purchase-request-item-sku').fill(`SKU-${slug}`)
    await firstItem.getByTestId('purchase-request-item-name').fill(`Compra ${slug}`)
    await firstItem.getByTestId('purchase-request-item-quantity').fill('2')
    await firstItem.getByTestId('purchase-request-item-price').fill('15990')

    await page.getByTestId('wizard-next').click()
    const resultText = await page.getByTestId('purchase-request-result').textContent()
    const requestId = Number(resultText?.match(/#(\d+)/)?.[1] || 0)
    expect(requestId).toBeGreaterThan(0)
    await page.getByTestId('wizard-next').click()
    await page.getByTestId('purchase-requests-refresh').click()

    const requestRow = page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })
    await expect(requestRow).toBeVisible()
    await requestRow.getByTestId('purchase-request-request-payment').click()
    await expect(page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })).toContainText('pending_payment')

    const pendingRow = page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })
    await pendingRow.getByTestId('purchase-request-confirm-payment').click()
    await expect(page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })).toContainText('paid_client')

    const paidRow = page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })
    await paidRow.getByTestId('purchase-request-status-select').selectOption('received')
    await expect(page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })).toContainText('received')

    await page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` }).getByTestId('purchase-request-delete').click()
    await expect(page.getByTestId('purchase-request-row').filter({ hasText: `#${requestId}` })).toHaveCount(0)
    await expectNoBrowserErrors(tracker)
  })

  test('manuals CRUD works from admin UI', async ({ page }) => {
    const tracker = trackBrowserErrors(page)
    const slug = Date.now().toString(36)
    const createdTitle = `Manual E2E ${slug}`
    const updatedTitle = `Manual E2E ${slug} Editado`
    let manualId: number | null = null
    let instrumentId: number | null = null

    page.on('dialog', (dialog) => dialog.accept())

    try {
      const instrument = await apiAs('admin', '/instruments/', {
        method: 'POST',
        body: {
          name: `Instrumento ${slug}`,
          model: `E2E-${slug}`,
          type: 'synthesizer',
        },
      })
      instrumentId = Number(instrument.id)

      await page.goto('/admin/manuals')
      await waitForAppToSettle(page)

      await page.getByTestId('manuals-new').click()
      await page.getByTestId('manual-instrument').selectOption(String(instrumentId))
      await page.getByTestId('manual-title').fill(createdTitle)
      await page.getByTestId('wizard-next').click()
      await page.getByTestId('manual-url').fill(`https://example.com/manual-${slug}.pdf`)
      await page.getByTestId('wizard-next').click()
      const resultText = await page.getByTestId('manual-result').textContent()
      manualId = Number(resultText?.match(/#(\d+)/)?.[1] || 0)
      expect(manualId).toBeGreaterThan(0)
      await page.getByTestId('wizard-next').click()
      await page.getByTestId('manuals-refresh').click()

      const manualRow = page.getByTestId('manual-row').filter({ hasText: `#${manualId}` })
      await expect(manualRow).toBeVisible()
      await manualRow.getByTestId('manual-edit').click()
      await page.getByTestId('manual-title-input').fill(updatedTitle)
      await page.getByTestId('manual-url-input').fill(`https://example.com/manual-${slug}-updated.pdf`)
      await page.getByTestId('manual-save').click()

      const updatedRow = page.getByTestId('manual-row').filter({ hasText: updatedTitle })
      await expect(updatedRow).toBeVisible()
      await updatedRow.getByTestId('manual-delete').click()
      manualId = null
      await expect(page.getByTestId('manual-row').filter({ hasText: updatedTitle })).toHaveCount(0)
      await expectNoBrowserErrors(tracker)
    } finally {
      if (manualId) {
        await apiAs('admin', `/manuals/${manualId}`, { method: 'DELETE' }).catch(() => null)
      }
      if (instrumentId) {
        await apiAs('admin', `/instruments/${instrumentId}`, { method: 'DELETE' }).catch(() => null)
      }
    }
  })
})
