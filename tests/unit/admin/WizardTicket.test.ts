import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import WizardTicket from '@/vue/components/admin/wizard/WizardTicket.vue'

describe('WizardTicket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockResolvedValue({ data: [] })
    apiMock.post.mockResolvedValue({ data: { id: 14 } })
  })

  it('creates a ticket and emits completed at the end', async () => {
    const wrapper = mount(WizardTicket)
    await flushPromises()

    await wrapper.get('[data-testid="wizard-next"]').trigger('click')
    await wrapper.get('[data-testid="ticket-subject"]').setValue('Ticket de prueba')
    await wrapper.get('[data-testid="ticket-priority"]').setValue('high')
    await wrapper.get('[data-testid="ticket-message"]').setValue('Mensaje detallado')
    await wrapper.get('[data-testid="wizard-next"]').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/tickets/', expect.objectContaining({
      subject: 'Ticket de prueba',
      priority: 'high',
      message: 'Mensaje detallado',
    }))
    expect(wrapper.get('[data-testid="ticket-result"]').text()).toContain('#14')

    await wrapper.get('[data-testid="wizard-next"]').trigger('click')
    expect(wrapper.emitted('completed')).toBeTruthy()
  })
})
