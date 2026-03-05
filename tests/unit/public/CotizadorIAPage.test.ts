import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerPush = vi.hoisted(() => vi.fn())
const quotationStoreMock = vi.hoisted(() => ({
  setFaults: vi.fn(),
}))
const quotationComposableMock = vi.hoisted(() => ({
  quotation: { total: 0 },
  loading: false,
  error: '',
  estimate: vi.fn(),
  reset: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: routerPush,
  }),
}))

vi.mock('@/stores/quotation', () => ({
  useQuotationStore: () => quotationStoreMock,
}))

vi.mock('@/composables/useQuotation', () => ({
  useQuotation: () => quotationComposableMock,
}))

import CotizadorIAPage from '@/vue/content/pages/CotizadorIAPage.vue'

const stubs = {
  InstrumentSelector: {
    template: '<button data-testid="instrument-select" @click="$emit(\'selected\', { id: 77, model: \'MS-20\' })">instrument</button>',
  },
  InteractiveInstrumentDiagnostic: {
    props: ['initialInstrument'],
    template: `
      <div>
        <span data-testid="diag-instrument">{{ initialInstrument?.id }}</span>
        <button
          data-testid="diagnostic-complete"
          @click="$emit('complete', { selected_symptoms: ['noise', 'hum'] })"
        >
          diagnostic
        </button>
      </div>
    `,
  },
  DisclaimerModal: {
    props: ['show'],
    template: `
      <div data-testid="disclaimer-stub">
        <span data-testid="disclaimer-show">{{ show ? 'yes' : 'no' }}</span>
        <button data-testid="disclaimer-accept" @click="$emit('accept')">accept</button>
        <button data-testid="disclaimer-cancel" @click="$emit('cancel')">cancel</button>
      </div>
    `,
  },
  TurnstileWidget: {
    template: '<button data-testid="turnstile-verify" @click="$emit(\'verify\', \'turnstile-ok\')">captcha</button>',
  },
  QuotationResult: {
    props: ['quotation', 'loading', 'error'],
    template: `
      <div data-testid="quotation-result-stub">
        <span data-testid="quotation-props">{{ JSON.stringify({ quotation, loading, error }) }}</span>
        <button data-testid="quotation-new" @click="$emit('new-quote')">new</button>
        <button data-testid="quotation-schedule" @click="$emit('schedule')">schedule</button>
      </div>
    `,
  },
}

describe('CotizadorIAPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    quotationComposableMock.estimate.mockResolvedValue({ total: 123000 })
  })

  it('runs full step flow, validates captcha, estimates and supports reset/schedule', async () => {
    const wrapper = mount(CotizadorIAPage, {
      global: { stubs },
    })

    expect(wrapper.text()).toContain('Seleccionar Instrumento')

    await wrapper.get('[data-testid="instrument-select"]').trigger('click')
    expect(wrapper.text()).toContain('Diagnóstico Visual')
    expect(wrapper.get('[data-testid="diag-instrument"]').text()).toBe('77')

    await wrapper.get('[data-testid="diagnostic-complete"]').trigger('click')
    expect(quotationStoreMock.setFaults).toHaveBeenCalledWith(['noise', 'hum'])
    expect(wrapper.find('[data-testid="disclaimer-stub"]').exists()).toBe(true)

    await wrapper.get('[data-testid="disclaimer-accept"]').trigger('click')
    await flushPromises()
    expect(quotationComposableMock.estimate).not.toHaveBeenCalled()
    expect(wrapper.find('[data-testid="disclaimer-stub"]').exists()).toBe(true)

    await wrapper.get('[data-testid="turnstile-verify"]').trigger('click')
    await wrapper.get('[data-testid="disclaimer-accept"]').trigger('click')
    await flushPromises()

    expect(quotationComposableMock.estimate).toHaveBeenCalledWith(
      77,
      { selected_symptoms: ['noise', 'hum'] },
      'turnstile-ok'
    )
    expect(wrapper.find('[data-testid="quotation-result-stub"]').exists()).toBe(true)

    await wrapper.get('[data-testid="quotation-schedule"]').trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/agendar')

    await wrapper.get('[data-testid="quotation-new"]').trigger('click')
    expect(quotationComposableMock.reset).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Seleccionar Instrumento')
  })

  it('returns to step 2 on disclaimer cancel and logs estimate errors', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    quotationComposableMock.estimate.mockRejectedValue(new Error('estimate error'))

    const wrapper = mount(CotizadorIAPage, {
      global: { stubs },
    })

    await wrapper.get('[data-testid="instrument-select"]').trigger('click')
    await wrapper.get('[data-testid="diagnostic-complete"]').trigger('click')

    await wrapper.get('[data-testid="disclaimer-cancel"]').trigger('click')
    expect(wrapper.text()).toContain('Diagnóstico Visual')

    await wrapper.get('[data-testid="diagnostic-complete"]').trigger('click')
    await wrapper.get('[data-testid="turnstile-verify"]').trigger('click')
    await wrapper.get('[data-testid="disclaimer-accept"]').trigger('click')
    await flushPromises()

    expect(quotationComposableMock.estimate).toHaveBeenCalled()
    expect(consoleErrorSpy).toHaveBeenCalled()
    expect(wrapper.find('[data-testid="quotation-result-stub"]').exists()).toBe(true)
  })
})
