import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))

const mediaMock = vi.hoisted(() => ({
  hydrateRepairPhotos: vi.fn(),
  revokeHydratedRepairPhotos: vi.fn(),
}))

vi.mock('@/composables/useApi', () => ({
  useApi: () => apiMock,
}))

vi.mock('@/services/secureMedia', () => mediaMock)

import { useRepairsStore } from '@stores/repairs'

describe('repairs store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mediaMock.hydrateRepairPhotos.mockImplementation(async (photos) =>
      photos.map((photo) => ({
        ...photo,
        resolved_photo_url: `blob:${photo.id}`,
      }))
    )
    mediaMock.revokeHydratedRepairPhotos.mockImplementation(() => undefined)
  })

  it('starts empty', () => {
    const store = useRepairsStore()

    expect(store.repairs).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches repairs successfully', async () => {
    apiMock.get.mockResolvedValueOnce([{ id: 1 }, { id: 2 }])

    const store = useRepairsStore()
    const result = await store.fetchRepairs()

    expect(apiMock.get).toHaveBeenCalledWith('/repairs/')
    expect(result).toEqual([{ id: 1 }, { id: 2 }])
    expect(store.repairs).toEqual([{ id: 1 }, { id: 2 }])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('captures fetch failures and clears stale repairs', async () => {
    const failure = { message: 'backend down' }
    apiMock.get.mockRejectedValueOnce(failure)

    const store = useRepairsStore()
    store.repairs = [{ id: 99 }]

    await expect(store.fetchRepairs()).resolves.toEqual([])
    expect(store.repairs).toEqual([])
    expect(store.error).toEqual(failure)
  })

  it('prepends new repairs after create', async () => {
    apiMock.post.mockResolvedValueOnce({ id: 3, status: 'pending' })

    const store = useRepairsStore()
    store.repairs = [{ id: 1 }, { id: 2 }]

    const created = await store.createRepair({ status: 'pending' })

    expect(apiMock.post).toHaveBeenCalledWith('/repairs/', { status: 'pending' })
    expect(created).toEqual({ id: 3, status: 'pending' })
    expect(store.repairs.map((repair) => repair.id)).toEqual([3, 1, 2])
  })

  it('replaces an existing repair on update', async () => {
    apiMock.put.mockResolvedValueOnce({ id: 2, status: 'done' })

    const store = useRepairsStore()
    store.repairs = [{ id: 1, status: 'pending' }, { id: 2, status: 'pending' }]

    const updated = await store.updateRepair(2, { status: 'done' })

    expect(apiMock.put).toHaveBeenCalledWith('/repairs/2', { status: 'done' })
    expect(updated).toEqual({ id: 2, status: 'done' })
    expect(store.repairs).toEqual([{ id: 1, status: 'pending' }, { id: 2, status: 'done' }])
  })

  it('filters out the deleted repair', async () => {
    apiMock.delete.mockResolvedValueOnce({ ok: true })

    const store = useRepairsStore()
    store.repairs = [{ id: 1 }, { id: 2 }]

    const result = await store.deleteRepair(1)

    expect(apiMock.delete).toHaveBeenCalledWith('/repairs/1')
    expect(result).toEqual({ ok: true })
    expect(store.repairs).toEqual([{ id: 2 }])
  })

  it('loads client repairs into the shared repairs collection', async () => {
    apiMock.get.mockResolvedValueOnce([{ id: 12 }, { id: 14 }])

    const store = useRepairsStore()
    const result = await store.fetchClientRepairs()

    expect(apiMock.get).toHaveBeenCalledWith('/client/repairs')
    expect(result).toEqual([{ id: 12 }, { id: 14 }])
    expect(store.repairs).toEqual([{ id: 12 }, { id: 14 }])
  })

  it('loads and hydrates client repair detail', async () => {
    apiMock.get.mockResolvedValueOnce({
      repair: { id: 99, instrument: 'Juno-106' },
      timeline: [{ label: 'Ingreso' }],
      photos: [{ id: 7, caption: 'Antes' }],
      notes: [{ id: 3, note: 'Nota visible' }],
    })

    const store = useRepairsStore()
    const detail = await store.fetchClientRepairDetail(99)

    expect(apiMock.get).toHaveBeenCalledWith('/client/repairs/99/details')
    expect(mediaMock.hydrateRepairPhotos).toHaveBeenCalledWith([{ id: 7, caption: 'Antes' }])
    expect(detail.repair).toEqual({ id: 99, instrument: 'Juno-106' })
    expect(store.currentRepair).toEqual({ id: 99, instrument: 'Juno-106' })
    expect(store.currentRepairPhotos).toEqual([{ id: 7, caption: 'Antes', resolved_photo_url: 'blob:7' }])
  })

  it('returns pdf bytes for client closure downloads', async () => {
    const pdfBytes = new Uint8Array([1, 2, 3])
    apiMock.get.mockResolvedValueOnce(pdfBytes)

    const store = useRepairsStore()
    const result = await store.downloadClientClosurePdf(55)

    expect(apiMock.get).toHaveBeenCalledWith('/client/repairs/55/closure-pdf', {
      responseType: 'blob',
    })
    expect(result).toBe(pdfBytes)
  })

  it('clears hydrated client repair detail state', () => {
    const store = useRepairsStore()
    store.currentRepair = { id: 1 }
    store.currentRepairTimeline = [{ label: 'Ingreso' }]
    store.currentRepairPhotos = [{ id: 2, resolved_photo_url: 'blob:2' }]
    store.currentRepairNotes = [{ id: 3 }]

    store.clearCurrentRepairDetail()

    expect(mediaMock.revokeHydratedRepairPhotos).toHaveBeenCalledWith([{ id: 2, resolved_photo_url: 'blob:2' }])
    expect(store.currentRepair).toBeNull()
    expect(store.currentRepairTimeline).toEqual([])
    expect(store.currentRepairPhotos).toEqual([])
    expect(store.currentRepairNotes).toEqual([])
  })
})
