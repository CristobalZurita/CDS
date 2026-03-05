import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
}))

const catalogState = vi.hoisted(() => ({
  brands: {
    value: [{ id: 'korg', name: 'Korg' }, { id: 'roland', name: 'Roland' }],
    __v_isRef: true,
  },
  getInstrumentsByBrand: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/composables/useInstrumentsCatalog', () => ({
  useInstrumentsCatalog: () => ({
    brands: catalogState.brands,
    getInstrumentsByBrand: catalogState.getInstrumentsByBrand,
  }),
}))

import AIAnalysisResult from '@/vue/components/ai/AIAnalysisResult.vue'
import FaultDetector from '@/vue/components/ai/FaultDetector.vue'
import FaultMarker from '@/vue/components/ai/FaultMarker.vue'
import ImageUploader from '@/vue/components/ai/ImageUploader.vue'
import QuoteGenerator from '@/vue/components/ai/QuoteGenerator.vue'

describe('ai components', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    catalogState.getInstrumentsByBrand.mockImplementation((brandId: string) => {
      if (brandId === 'korg') {
        return [
          { id: 'ms20', model: 'MS-20' },
          { id: 'minilogue', model: 'Minilogue' },
        ]
      }
      return []
    })
  })

  it('formats AI analysis payload as pretty JSON', () => {
    const wrapper = mount(AIAnalysisResult, {
      props: {
        result: { score: 0.92, faults: ['noise'] },
      },
    })

    expect(wrapper.text()).toContain('Resultado IA')
    expect(wrapper.text()).toContain('"score": 0.92')
    expect(wrapper.text()).toContain('"noise"')
  })

  it('toggles faults and emits updated model value', async () => {
    const wrapper = mount(FaultDetector, {
      props: {
        faults: [
          { code: 'f1', label: 'Ruido' },
          { code: 'f2', label: 'No enciende' },
        ],
        modelValue: ['f1'],
      },
    })

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes[0].trigger('change')
    expect(wrapper.emitted('update:modelValue')?.[0]?.[0]).toEqual([])

    await checkboxes[1].trigger('change')
    expect(wrapper.emitted('update:modelValue')?.[1]?.[0]).toEqual(['f1', 'f2'])
  })

  it('renders fault marker fallback and custom label', () => {
    const fallback = mount(FaultMarker, {
      props: { code: 'F-01' },
    })
    expect(fallback.text()).toContain('F-01')

    const custom = mount(FaultMarker, {
      props: { code: 'F-02', label: 'Falla crítica' },
    })
    expect(custom.text()).toContain('Falla crítica')
  })

  it('previews selected image and emits selected file', async () => {
    const createObjectURLSpy = vi.fn(() => 'blob:preview-url')
    Object.defineProperty(URL, 'createObjectURL', {
      value: createObjectURLSpy,
      configurable: true,
    })

    const wrapper = mount(ImageUploader)
    const fileInput = wrapper.get('input[type="file"]')
    const file = new File(['img-bytes'], 'board.png', { type: 'image/png' })
    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true,
    })

    await fileInput.trigger('change')
    expect(createObjectURLSpy).toHaveBeenCalledWith(file)
    expect(wrapper.emitted('select')?.[0]?.[0]).toBe(file)
    expect(wrapper.get('img').attributes('src')).toBe('blob:preview-url')
  })

  it('generates quote result and handles API errors', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: { min_price: 500000, max_price: 800000 },
    })
    apiMock.post.mockRejectedValueOnce({
      response: { data: { detail: 'Servicio no disponible' } },
    })

    const wrapper = mount(QuoteGenerator)

    const brandSelect = wrapper.findAll('select')[0]
    const modelSelect = wrapper.findAll('select')[1]

    await brandSelect.setValue('korg')
    await flushPromises()
    expect(modelSelect.findAll('option').length).toBeGreaterThan(1)

    await modelSelect.setValue('ms20')
    await flushPromises()
    await wrapper.get('button.btn.btn-primary').trigger('click')
    await flushPromises()

    expect(apiMock.post).toHaveBeenCalledWith('/quotations/estimate', {
      instrument_id: 'ms20',
      faults: [],
    })
    expect(wrapper.text()).toContain('Resultado de ejemplo')
    expect(wrapper.text()).toContain('"min_price": 500000')

    await modelSelect.setValue('minilogue')
    await wrapper.get('button.btn.btn-primary').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Error al generar estimación: Servicio no disponible')
  })
})
