import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import WizardPurchaseRequest from '@/vue/components/admin/wizard/WizardPurchaseRequest.vue'

describe('WizardPurchaseRequest', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue({ data: [] })
    apiMock.post.mockResolvedValue({ data: { id: 22 } })
  })

  it('creates a purchase request from the wizard flow', async () => {
    const wrapper = mount(WizardPurchaseRequest)
    await flushPromises()

    await wrapper.get('[data-testid="purchase-request-notes"]').setValue('Notas de compra')
    await wrapper.get('[data-testid="wizard-next"]').trigger('click')
    const firstRow = wrapper.findAll('[data-testid="purchase-request-item-row"]')[0]
    await firstRow.get('[data-testid="purchase-request-item-sku"]').setValue('SKU-1')
    await firstRow.get('[data-testid="purchase-request-item-name"]').setValue('Transformador')
    await firstRow.get('[data-testid="purchase-request-item-quantity"]').setValue('2')
    await firstRow.get('[data-testid="purchase-request-item-price"]').setValue('15990')
    await wrapper.get('[data-testid="wizard-next"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/purchase-requests/', expect.objectContaining({
      notes: 'Notas de compra',
      items: [
        expect.objectContaining({
          sku: 'SKU-1',
          name: 'Transformador',
          quantity: 2,
          unit_price: 15990,
        }),
      ],
    }))
    expect(wrapper.get('[data-testid="purchase-request-result"]').text()).toContain('#22')

    await wrapper.get('[data-testid="wizard-next"]').trigger('click')
    expect(wrapper.emitted('completed')).toBeTruthy()
  })
})
