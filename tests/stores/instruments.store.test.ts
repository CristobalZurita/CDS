import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  deleteRequest: vi.fn(),
  handleApiError: vi.fn(),
}))

vi.mock('@/services/api', () => apiMock)

import { useInstrumentsStore } from '@stores/instruments'

describe('instruments store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    apiMock.handleApiError.mockImplementation((error) => ({
      message: error?.message ?? 'Unknown error',
    }))
  })

  it('starts empty', () => {
    const store = useInstrumentsStore()

    expect(store.instruments).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches instruments', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: {
        data: [{ id: 1, name: 'Juno-106' }],
      },
    })

    const store = useInstrumentsStore()
    await store.fetchInstruments()

    expect(apiMock.get).toHaveBeenCalledWith('/instruments')
    expect(store.instruments).toEqual([{ id: 1, name: 'Juno-106' }])
    expect(store.loading).toBe(false)
  })

  it('captures fetch errors', async () => {
    const failure = new Error('backend down')
    apiMock.get.mockRejectedValueOnce(failure)

    const store = useInstrumentsStore()
    await store.fetchInstruments()

    expect(store.error).toBe('backend down')
  })

  it('delegates create, update and delete to the API', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        data: { id: 2 },
      },
    })
    apiMock.put.mockResolvedValueOnce({
      data: {
        data: { id: 2, name: 'DX7' },
      },
    })
    apiMock.deleteRequest.mockResolvedValueOnce({
      data: {
        data: { ok: true },
      },
    })

    const store = useInstrumentsStore()

    await expect(store.createInstrument({ name: 'DX7' })).resolves.toEqual({ id: 2 })
    await expect(store.updateInstrument(2, { name: 'DX7' })).resolves.toEqual({ id: 2, name: 'DX7' })
    await expect(store.deleteInstrument(2)).resolves.toBeUndefined()

    expect(apiMock.post).toHaveBeenCalledWith('/instruments', { name: 'DX7' })
    expect(apiMock.put).toHaveBeenCalledWith('/instruments/2', { name: 'DX7' })
    expect(apiMock.deleteRequest).toHaveBeenCalledWith('/instruments/2')
  })
})
