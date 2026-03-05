import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import OtPaymentsPage from '@/vue/content/pages/OtPaymentsPage.vue'

const pendingRequest = {
  id: 11,
  status: 'pending_payment',
  repair_code: 'CDS-001-OT-011',
  requested_amount: 24990,
  payment_due_date: '2026-03-10T00:00:00Z',
  items_count: 1,
  notes: 'Pago pendiente',
  latest_payment: {
    admin_notes: 'Deposita el monto y sube comprobante.',
    proof_path: null,
  },
}

const submittedRequest = {
  ...pendingRequest,
  status: 'proof_submitted',
  latest_payment: {
    ...pendingRequest.latest_payment,
    proof_path: '/uploads/images/proof.png',
    deposit_reference: 'DEP-OT-001',
  },
}

describe('OtPaymentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockReset()
    apiMock.post.mockReset()
  })

  it('renders the empty state when the client has no OT payment requests', async () => {
    apiMock.get.mockResolvedValueOnce({ data: [] })

    const wrapper = mount(OtPaymentsPage)
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/client/purchase-requests')
    expect(wrapper.get('[data-testid="ot-payments-empty"]').text()).toContain('No tienes solicitudes de pago OT pendientes')
  })

  it('uploads a proof image and persists the deposit proof payload', async () => {
    apiMock.get
      .mockResolvedValueOnce({ data: [pendingRequest] })
      .mockResolvedValueOnce({ data: [submittedRequest] })
    apiMock.post
      .mockResolvedValueOnce({ data: { path: '/uploads/images/proof.png' } })
      .mockResolvedValueOnce({ data: { ok: true } })

    const wrapper = mount(OtPaymentsPage)
    await flushPromises()

    await wrapper.get('[data-testid="ot-payment-amount"]').setValue('25990')
    await wrapper.get('[data-testid="ot-payment-reference"]').setValue('DEP-OT-001')
    await wrapper.get('[data-testid="ot-payment-notes"]').setValue('Comprobante enviado desde unit test')
    const fileInput = wrapper.get('[data-testid="ot-payment-file"]')
    Object.defineProperty(fileInput.element, 'files', {
      value: [new File(['proof'], 'proof.png', { type: 'image/png' })],
      configurable: true,
    })
    await fileInput.trigger('change')
    await wrapper.get('[data-testid="ot-payment-submit"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledTimes(2)
    expect(apiMock.post.mock.calls[0][0]).toBe('/uploads/images')
    expect(apiMock.post.mock.calls[0][1]).toBeInstanceOf(FormData)
    expect(apiMock.post.mock.calls[1][0]).toBe('/client/purchase-requests/11/deposit-proof')
    expect(apiMock.post.mock.calls[1][1]).toEqual(
      expect.objectContaining({
        amount: 25990,
        deposit_reference: 'DEP-OT-001',
        client_notes: 'Comprobante enviado desde unit test',
        proof_path: '/uploads/images/proof.png',
      })
    )
    expect(apiMock.get).toHaveBeenCalledTimes(2)
    expect(wrapper.get('[data-testid="ot-payment-row"]').text()).toContain('proof_submitted')
    expect(wrapper.get('[data-testid="ot-payment-proof-link"]').attributes('href')).toContain('/uploads/images/proof.png')
  })

  it('surfaces backend failures when loading or submitting a proof fails', async () => {
    apiMock.get.mockRejectedValueOnce({
      response: { data: { detail: 'Backend temporalmente no disponible' } },
    })

    const wrapper = mount(OtPaymentsPage)
    await flushPromises()

    expect(wrapper.get('[data-testid="ot-payments-error"]').text()).toContain('Backend temporalmente no disponible')

    apiMock.get.mockResolvedValueOnce({ data: [pendingRequest] })
    apiMock.post.mockRejectedValueOnce({
      response: { data: { detail: 'Archivo inválido' } },
    })

    await wrapper.get('[data-testid="ot-payments-refresh"]').trigger('click')
    await flushPromises()

    await wrapper.get('[data-testid="ot-payment-submit"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="ot-payments-error"]').text()).toContain('Archivo inválido')
  })
})
