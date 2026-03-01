import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))
const toastMock = vi.hoisted(() => ({
  showError: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: routerPush }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/toastService', () => toastMock)

import RepairsPage from '@/vue/content/pages/RepairsPage.vue'

const repairsPayload = [
  {
    id: 12,
    instrument: 'Prophet-5',
    repair_code: 'CDS-010-OT-012',
    status: 'en_trabajo',
    fault: 'Sin audio',
    date_in: '2026-02-01T00:00:00Z',
    progress: 60,
  },
  {
    id: 14,
    instrument: 'Juno-106',
    repair_code: 'CDS-010-OT-014',
    status: 'entregado',
    fault: 'Afinación inestable',
    date_in: '2026-01-10T00:00:00Z',
    date_out: '2026-01-25T00:00:00Z',
    cost: 85000,
  },
]

describe('RepairsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue({ data: repairsPayload })
  })

  it('loads repairs, filters by status bucket and navigates to the detail view', async () => {
    const wrapper = mount(RepairsPage)
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/client/repairs')
    expect(wrapper.findAll('[data-testid="repairs-card"]')).toHaveLength(2)
    expect(wrapper.text()).toContain('Prophet-5')
    expect(wrapper.text()).toContain('Juno-106')

    await wrapper.get('[data-testid="repairs-status-filter"]').setValue('completed')

    const cards = wrapper.findAll('[data-testid="repairs-card"]')
    expect(cards).toHaveLength(1)
    expect(cards[0].text()).toContain('Juno-106')

    await wrapper.get('[data-testid="repair-view"]').trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/repairs/14')
  })

  it('shows the empty state when no repairs match the selected filter', async () => {
    const wrapper = mount(RepairsPage)
    await flushPromises()

    await wrapper.get('[data-testid="repairs-status-filter"]').setValue('cancelled')
    expect(wrapper.get('[data-testid="repairs-empty"]').text()).toContain('No hay reparaciones')
  })

  it('surfaces API failures through the toast service', async () => {
    apiMock.get.mockRejectedValueOnce({
      response: { data: { detail: 'No se pudo consultar reparaciones' } },
    })

    mount(RepairsPage)
    await flushPromises()

    expect(toastMock.showError).toHaveBeenCalledWith('No se pudo consultar reparaciones')
  })
})
