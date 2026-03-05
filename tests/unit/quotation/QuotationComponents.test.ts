import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const quotationStoreMock = vi.hoisted(() => ({
  setInstrument: vi.fn(),
}))

const catalogState = vi.hoisted(() => ({
  brands: [
    { id: 'korg', name: 'Korg', tier: 'professional', founded: 1963, country: 'Japan' },
    { id: 'roland', name: 'Roland', tier: 'legendary', founded: 1972, country: 'Japan' },
  ],
  getInstrumentsByBrand: vi.fn(),
}))

vi.mock('@/stores/quotation', () => ({
  useQuotationStore: () => quotationStoreMock,
}))

vi.mock('@/composables/useInstrumentsCatalog', () => ({
  useInstrumentsCatalog: () => ({
    brands: { value: catalogState.brands },
    getInstrumentsByBrand: catalogState.getInstrumentsByBrand,
  }),
}))

import DisclaimerModal from '@/vue/components/quotation/DisclaimerModal.vue'
import InstrumentSelector from '@/vue/components/quotation/InstrumentSelector.vue'
import QuotationResult from '@/vue/components/quotation/QuotationResult.vue'

describe('quotation components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    catalogState.getInstrumentsByBrand.mockImplementation((brandId: string) => {
      if (brandId === 'korg') {
        return [
          {
            id: 'korg-ms20',
            model: 'MS-20',
            year: 1978,
            imagen_url: '/images/ms20.webp',
            valor_min: 500000,
            valor_max: 900000,
          },
        ]
      }
      return []
    })
  })

  it('controls disclaimer acceptance and emits cancel/accept actions', async () => {
    const hidden = mount(DisclaimerModal, {
      props: { show: false },
    })
    expect(hidden.find('.disclaimer-overlay').exists()).toBe(false)

    const visible = mount(DisclaimerModal, {
      props: { show: true },
    })
    expect(visible.find('.disclaimer-overlay').exists()).toBe(true)
    expect(visible.get('.btn-accept').attributes('disabled')).toBeDefined()

    await visible.find('input[type="checkbox"]').setValue(true)
    expect(visible.get('.btn-accept').attributes('disabled')).toBeUndefined()

    await visible.get('.btn-cancel').trigger('click')
    expect(visible.emitted('cancel')).toBeTruthy()

    await visible.get('.btn-accept').trigger('click')
    expect(visible.emitted('accept')).toBeTruthy()
  })

  it('filters brands and instruments, handles image error and emits selected instrument', async () => {
    const wrapper = mount(InstrumentSelector)

    expect(wrapper.findAll('[data-testid="quotation-brand-card"]')).toHaveLength(2)
    await wrapper.find('input[placeholder*="Busca marca"]').setValue('roland')
    expect(wrapper.findAll('[data-testid="quotation-brand-card"]')).toHaveLength(1)

    await wrapper.find('input[placeholder*="Busca marca"]').setValue('korg')
    await wrapper.get('[data-testid="quotation-brand-card"]').trigger('click')
    await flushPromises()

    expect(catalogState.getInstrumentsByBrand).toHaveBeenCalledWith('korg')
    expect(wrapper.findAll('[data-testid="quotation-instrument-card"]')).toHaveLength(1)

    const image = wrapper.get('.instrument-image img')
    await image.trigger('error')
    expect(image.classes()).toContain('img-broken')

    await wrapper.get('[data-testid="quotation-instrument-card"]').trigger('click')
    await wrapper.get('[data-testid="quotation-proceed"]').trigger('click')

    expect(quotationStoreMock.setInstrument).toHaveBeenCalledWith(
      expect.objectContaining({
        id: 'korg-ms20',
        model: 'MS-20',
      })
    )
    expect(wrapper.emitted('selected')?.[0]?.[0]).toEqual(
      expect.objectContaining({
        id: 'korg-ms20',
      })
    )
  })

  it('renders loading/error/success states in QuotationResult and emits actions', async () => {
    const loading = mount(QuotationResult, {
      props: {
        loading: true,
        error: null,
        quotation: null,
      },
    })
    expect(loading.text()).toContain('Generando cotización')

    const error = mount(QuotationResult, {
      props: {
        loading: false,
        error: 'Servicio no disponible',
        quotation: null,
      },
    })
    expect(error.text()).toContain('Error al generar cotización')
    await error.get('.btn-btn').trigger('click')
    expect(error.emitted('new-quote')).toBeTruthy()

    const success = mount(QuotationResult, {
      props: {
        loading: false,
        error: null,
        quotation: {
          instrument_name: 'Korg MS-20',
          min_price: 500000,
          max_price: 900000,
          disclaimer: 'Estimación de referencia',
          created_at: '2026-03-05T12:30:00Z',
          summary: {
            range_label: 'Rango medio',
            size_label: 'Sintetizador compacto',
            selected_symptom_count: 3,
            visual_issue_count: 1,
            notes_present: true,
          },
        },
      },
    })

    expect(success.text()).toContain('Estimación Referencial Generada')
    expect(success.text()).toContain('Korg MS-20')
    expect(success.text()).toContain('500.000')
    expect(success.text()).toContain('900.000')
    expect(success.text()).toContain('Estimación generada:')
    expect(success.text()).toContain('Sí')

    await success.get('.btn-secondary').trigger('click')
    await success.get('.btn-primary').trigger('click')
    expect(success.emitted('new-quote')).toBeTruthy()
    expect(success.emitted('schedule')).toBeTruthy()
  })
})
