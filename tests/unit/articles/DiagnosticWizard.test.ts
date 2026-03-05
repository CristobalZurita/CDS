import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const diagnosticMock = vi.hoisted(() => ({
  selectedBrand: { value: 'korg' as string | null },
  selectedModel: { value: 'ms20' as string | null },
  selectedFaults: { value: ['POWER'] as string[] },
  clientName: { value: 'Juan Perez' },
  clientEmail: { value: 'juan@test.cl' },
  clientPhone: { value: '+56912345678' },
  faults: {
    value: {
      POWER: { id: 'POWER', name: 'No enciende', basePrice: 120000 },
    } as Record<string, { id: string; name: string; basePrice: number }>,
  },
  getAvailableFaults: vi.fn(() => [{ id: 'POWER', name: 'No enciende', basePrice: 120000 }]),
  addFault: vi.fn(),
  removeFault: vi.fn(),
  clearFaults: vi.fn(),
  getEffectiveFaults: vi.fn(() => ['POWER']),
  calculateQuote: vi.fn(() => ({
    baseCost: 120000,
    complexityFactor: 1.5,
    valueFactor: 1.2,
    finalCost: 216000,
    instrument: { model: 'MS-20' },
    brand: { name: 'Korg', tier: 'professional' },
    faults: [{ id: 'POWER', name: 'No enciende', basePrice: 120000 }],
  })),
  validateName: vi.fn(() => true),
  validateEmail: vi.fn(() => true),
  validatePhone: vi.fn(() => true),
  reset: vi.fn(),
  getQuoteData: vi.fn(),
}))

const catalogMock = vi.hoisted(() => ({
  getAllBrands: vi.fn(() => [{ id: 'korg', name: 'Korg' }]),
  getInstrumentsByBrand: vi.fn(() => [{ id: 'ms20', model: 'MS-20', imagePath: '/img/ms20.webp' }]),
  getBrandById: vi.fn((id: string) => (id === 'korg' ? { id: 'korg', name: 'Korg' } : undefined)),
  getInstrumentById: vi.fn((id: string) =>
    id === 'ms20' ? { id: 'ms20', model: 'MS-20', imagePath: '/img/ms20.webp' } : null
  ),
}))

vi.mock('@/composables/useDiagnostic', () => ({
  useDiagnostic: () => diagnosticMock,
}))

vi.mock('@/composables/useInstrumentsCatalog', () => ({
  useInstrumentsCatalog: () => catalogMock,
}))

import DiagnosticWizard from '@/vue/components/articles/DiagnosticWizard.vue'

describe('DiagnosticWizard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    diagnosticMock.getQuoteData.mockReturnValue({
      client: {
        name: 'Juan Perez',
        email: 'juan@test.cl',
        phone: '+56912345678',
      },
      equipment: {
        brand: 'korg',
        model: 'ms20',
        estimatedValue: null,
      },
      diagnostics: {
        faults: ['POWER'],
        quote: {
          baseCost: 120000,
          complexityFactor: 1.5,
          valueFactor: 1.2,
          finalCost: 216000,
          instrument: { model: 'MS-20' },
          brand: { name: 'Korg', tier: 'professional' },
          faults: [{ id: 'POWER', name: 'No enciende', basePrice: 120000 }],
        },
      },
      timestamp: '2026-03-05T12:00:00Z',
    })
    vi.spyOn(window, 'alert').mockImplementation(() => {})
  })

  it('downloads quote file using current getQuoteData shape', async () => {
    const createObjectURLSpy = vi.fn(() => 'blob:diagnostic-quote')
    const revokeObjectURLSpy = vi.fn()
    Object.defineProperty(window.URL, 'createObjectURL', {
      value: createObjectURLSpy,
      configurable: true,
    })
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      value: revokeObjectURLSpy,
      configurable: true,
    })

    const originalCreateElement = document.createElement.bind(document)
    let createdAnchor: HTMLAnchorElement | null = null
    const clickSpy = vi.fn()
    vi.spyOn(document, 'createElement').mockImplementation(((tagName: string) => {
      const element = originalCreateElement(tagName)
      if (tagName.toLowerCase() === 'a') {
        createdAnchor = element as HTMLAnchorElement
        ;(createdAnchor as any).click = clickSpy
      }
      return element
    }) as any)

    const wrapper = mount(DiagnosticWizard, {
      global: {
        stubs: {
          ImageView: {
            template: '<img data-testid="image-view-stub" />',
          },
        },
      },
    })

    ;(wrapper.vm as any).currentStep = 5
    await flushPromises()

    const downloadButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Descargar PDF'))
    expect(downloadButton).toBeTruthy()
    await downloadButton!.trigger('click')

    expect(createObjectURLSpy).toHaveBeenCalled()
    expect(clickSpy).toHaveBeenCalled()
    expect(createdAnchor?.download).toBe('cotizacion-Juan-Perez.txt')
    expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:diagnostic-quote')
  })

  it('alerts when quote data is incomplete for download', async () => {
    diagnosticMock.getQuoteData.mockReturnValue({
      client: {
        name: 'Juan Perez',
        email: 'juan@test.cl',
        phone: '',
      },
      diagnostics: {
        faults: [],
        quote: null,
      },
    })

    const createObjectURLSpy = vi.fn(() => 'blob:should-not-happen')
    Object.defineProperty(window.URL, 'createObjectURL', {
      value: createObjectURLSpy,
      configurable: true,
    })

    const wrapper = mount(DiagnosticWizard, {
      global: {
        stubs: {
          ImageView: {
            template: '<img data-testid="image-view-stub" />',
          },
        },
      },
    })

    ;(wrapper.vm as any).currentStep = 5
    await flushPromises()

    const downloadButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('Descargar PDF'))
    expect(downloadButton).toBeTruthy()
    await downloadButton!.trigger('click')

    expect(window.alert).toHaveBeenCalledWith('Error: No hay datos de cotización para descargar')
    expect(createObjectURLSpy).not.toHaveBeenCalled()
  })
})
