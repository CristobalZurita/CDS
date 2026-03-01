import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
}))

const quotationStoreMock = vi.hoisted(() => ({
  selectedInstrument: { name: 'Prophet-5' },
}))

const authStoreMock = vi.hoisted(() => ({
  user: {
    full_name: 'Cliente Demo',
    email: 'cliente@example.com',
    phone: '+56911111111',
  },
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/stores/quotation', () => ({
  useQuotationStore: () => quotationStoreMock,
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => authStoreMock,
}))

import SchedulePage from '@/vue/content/pages/SchedulePage.vue'

const turnstileStub = {
  template: '<button data-testid="turnstile-stub" @click="$emit(\'verify\', \'turnstile-token\')">captcha</button>',
}

describe('SchedulePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.post.mockResolvedValue({ data: { ok: true } })
  })

  it('walks through the booking wizard and posts the appointment to the backend', async () => {
    const consoleLog = vi.spyOn(console, 'log').mockImplementation(() => undefined)
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => undefined)

    const wrapper = mount(SchedulePage, {
      global: {
        stubs: {
          TurnstileWidget: turnstileStub,
        },
      },
    })

    await wrapper.get('[data-testid="schedule-next-month"]').trigger('click')
    const selectableDay = wrapper
      .findAll('[data-testid="schedule-day"]')
      .find((node) => node.attributes('data-disabled') === 'false')

    expect(selectableDay).toBeTruthy()
    await selectableDay!.trigger('click')
    await wrapper.get('[data-testid="schedule-date-next"]').trigger('click')

    await wrapper.get('[data-testid="schedule-time-slot"]').trigger('click')
    await wrapper.get('[data-testid="schedule-time-next"]').trigger('click')

    await wrapper.get('input[type="checkbox"]').setValue(true)
    await wrapper.get('[data-testid="turnstile-stub"]').trigger('click')
    await wrapper.get('[data-testid="schedule-confirm"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="schedule-success"]').text()).toContain('¡Cita Confirmada!')
    expect(wrapper.get('[data-testid="schedule-appointment-number"]').text()).toMatch(/^CIT-\d{8}$/)
    expect(apiMock.post).toHaveBeenCalledWith(
      '/appointments/',
      expect.objectContaining({
        nombre: 'Cliente Demo',
        email: 'cliente@example.com',
        telefono: '+56911111111',
        mensaje: 'Instrumento: Prophet-5',
        turnstile_token: 'turnstile-token',
      })
    )
    expect(consoleLog).toHaveBeenCalled()
    expect(consoleWarn).not.toHaveBeenCalled()
  })
})
