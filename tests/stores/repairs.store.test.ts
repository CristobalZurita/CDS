import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))

vi.mock('@/composables/useApi', () => ({
  useApi: () => apiMock,
}))

import { useRepairsStore } from '@stores/repairs'

describe('repairs store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
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
})
