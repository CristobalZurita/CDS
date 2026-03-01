import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
}))

const mediaMock = vi.hoisted(() => ({
  hydrateRepairPhotos: vi.fn(),
  revokeHydratedRepairPhotos: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { id: '123' },
  }),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

vi.mock('@/services/secureMedia', () => mediaMock)

import RepairDetailPage from '@/vue/content/pages/RepairDetailPage.vue'

describe('RepairDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.get.mockImplementation((url: string) => {
      if (url.includes('/closure-pdf')) {
        return Promise.resolve({ data: new Uint8Array([1, 2, 3]) })
      }

      return Promise.resolve({
        data: {
          repair: {
            instrument: 'Prophet-5',
            repair_code: 'OT-123',
            status: 'Diagnóstico',
            problem_reported: 'No enciende',
            diagnosis: 'Fuente dañada',
            work_performed: 'Cambio de condensadores',
            total_cost: 150000,
          },
          timeline: [{ label: 'Ingreso', date: '2026-02-01T00:00:00Z' }],
          photos: [{ id: 1, caption: 'Antes' }],
          notes: [{ id: 2, note: 'Revisar voltajes', created_at: '2026-02-02T00:00:00Z' }],
        },
      })
    })
    mediaMock.hydrateRepairPhotos.mockResolvedValue([
      { id: 1, caption: 'Antes', resolved_photo_url: 'blob:photo-1' },
    ])
    mediaMock.revokeHydratedRepairPhotos.mockImplementation(() => undefined)
    Object.defineProperty(window.URL, 'createObjectURL', {
      writable: true,
      value: vi.fn(() => 'blob:pdf-download'),
    })
    Object.defineProperty(window.URL, 'revokeObjectURL', {
      writable: true,
      value: vi.fn(() => undefined),
    })
    vi.spyOn(window, 'alert').mockImplementation(() => undefined)
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
  })

  it('loads detail data, downloads the closure pdf and revokes photo URLs on unmount', async () => {
    const wrapper = mount(RepairDetailPage)
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/client/repairs/123/details')
    expect(mediaMock.hydrateRepairPhotos).toHaveBeenCalledWith([{ id: 1, caption: 'Antes' }])
    expect(wrapper.text()).toContain('Prophet-5')
    expect(wrapper.text()).toContain('Fuente dañada')

    await wrapper.get('[data-testid="repair-download"]').trigger('click')
    await flushPromises()

    expect(apiMock.get).toHaveBeenCalledWith('/client/repairs/123/closure-pdf', {
      responseType: 'blob',
    })
    expect(window.URL.createObjectURL).toHaveBeenCalled()
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled()

    wrapper.unmount()
    expect(mediaMock.revokeHydratedRepairPhotos).toHaveBeenCalledWith([
      { id: 1, caption: 'Antes', resolved_photo_url: 'blob:photo-1' },
    ])
  })

  it('alerts when the closure pdf download fails', async () => {
    apiMock.get.mockImplementation((url: string) => {
      if (url.includes('/closure-pdf')) {
        return Promise.reject({
          response: {
            data: {
              detail: 'PDF no disponible',
            },
          },
        })
      }

      return Promise.resolve({
        data: {
          repair: { instrument: 'Prophet-5' },
          timeline: [],
          photos: [],
          notes: [],
        },
      })
    })
    mediaMock.hydrateRepairPhotos.mockResolvedValue([])

    const wrapper = mount(RepairDetailPage)
    await flushPromises()

    await wrapper.get('[data-testid="repair-download"]').trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('PDF no disponible')
  })
})
