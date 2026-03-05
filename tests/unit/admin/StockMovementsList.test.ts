import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiComposableMock = vi.hoisted(() => ({
  get: vi.fn(),
}))

vi.mock('@/composables/useApi', () => ({
  useApi: () => apiComposableMock,
}))

import StockMovementsList from '@/vue/components/admin/StockMovementsList.vue'

describe('StockMovementsList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiComposableMock.get.mockResolvedValue([
      {
        id: 1,
        product_id: 100,
        movement_type: 'out',
        quantity: 2,
        created_at: '2026-03-05',
      },
      {
        id: 2,
        product_id: 200,
        movement_type: 'in',
        quantity: 5,
        created_at: '2026-03-06',
      },
    ])
  })

  it('loads movements on mount and refresh button', async () => {
    const wrapper = mount(StockMovementsList)
    await flushPromises()

    expect(apiComposableMock.get).toHaveBeenCalledWith('/stock-movements')
    expect(wrapper.text()).toContain('Movimientos de Stock')
    expect(wrapper.findAll('tbody tr')).toHaveLength(2)
    expect(wrapper.text()).toContain('100')
    expect(wrapper.text()).toContain('out')

    await wrapper.get('button').trigger('click')
    await flushPromises()
    expect(apiComposableMock.get).toHaveBeenCalledTimes(2)
  })
})
