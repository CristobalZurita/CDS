import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const repairsState = vi.hoisted(() => ({
  currentRepair: { value: null },
  currentRepairTimeline: { value: [] },
  currentRepairPhotos: { value: [] },
  currentRepairNotes: { value: [] },
  fetchClientRepairDetail: vi.fn(),
  downloadClientClosurePdf: vi.fn(),
  clearCurrentRepairDetail: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { id: '123' },
  }),
}))

vi.mock('@/composables/useRepairs', () => ({
  useRepairs: () => repairsState,
}))

import RepairDetailPage from '@/vue/content/pages/RepairDetailPage.vue'

describe('RepairDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    repairsState.currentRepair.value = {
      instrument: 'Prophet-5',
      repair_code: 'OT-123',
      status: 'Diagnóstico',
      problem_reported: 'No enciende',
      diagnosis: 'Fuente dañada',
      work_performed: 'Cambio de condensadores',
      total_cost: 150000,
    }
    repairsState.currentRepairTimeline.value = [{ label: 'Ingreso', date: '2026-02-01T00:00:00Z' }]
    repairsState.currentRepairPhotos.value = [{ id: 1, caption: 'Antes', resolved_photo_url: 'blob:photo-1' }]
    repairsState.currentRepairNotes.value = [{ id: 2, note: 'Revisar voltajes', created_at: '2026-02-02T00:00:00Z' }]
    repairsState.fetchClientRepairDetail.mockImplementation(async () => {
      return {
        repair: repairsState.currentRepair.value,
        timeline: repairsState.currentRepairTimeline.value,
        photos: repairsState.currentRepairPhotos.value,
        notes: repairsState.currentRepairNotes.value,
      }
    })
    repairsState.downloadClientClosurePdf.mockResolvedValue(new Uint8Array([1, 2, 3]))
    repairsState.clearCurrentRepairDetail.mockImplementation(() => undefined)
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

    expect(repairsState.fetchClientRepairDetail).toHaveBeenCalledWith('123')
    expect(wrapper.text()).toContain('Prophet-5')
    expect(wrapper.text()).toContain('Fuente dañada')

    await wrapper.get('[data-testid="repair-download"]').trigger('click')
    await flushPromises()

    expect(repairsState.downloadClientClosurePdf).toHaveBeenCalledWith('123')
    expect(window.URL.createObjectURL).toHaveBeenCalled()
    expect(HTMLAnchorElement.prototype.click).toHaveBeenCalled()

    wrapper.unmount()
    expect(repairsState.clearCurrentRepairDetail).toHaveBeenCalled()
  })

  it('alerts when the closure pdf download fails', async () => {
    repairsState.fetchClientRepairDetail.mockImplementation(async () => {
      repairsState.currentRepair.value = { instrument: 'Prophet-5' }
      repairsState.currentRepairTimeline.value = []
      repairsState.currentRepairPhotos.value = []
      repairsState.currentRepairNotes.value = []
      return {
        repair: repairsState.currentRepair.value,
        timeline: [],
        photos: [],
        notes: [],
      }
    })
    repairsState.downloadClientClosurePdf.mockRejectedValueOnce({
      response: {
        data: {
          detail: 'PDF no disponible',
        },
      },
    })

    const wrapper = mount(RepairDetailPage)
    await flushPromises()

    await wrapper.get('[data-testid="repair-download"]').trigger('click')
    await flushPromises()

    expect(window.alert).toHaveBeenCalledWith('PDF no disponible')
  })
})
