import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiMock = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  handleApiError: vi.fn(),
}))

vi.mock('@/services/api', () => apiMock)

import { useStockMovementsStore } from '@stores/stockMovements'

describe('stock movements store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    apiMock.handleApiError.mockImplementation((error) => ({
      message: error?.message ?? 'Unknown error',
    }))
  })

  it('starts empty', () => {
    const store = useStockMovementsStore()

    expect(store.movements).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches movement history', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: {
        data: [{ id: 1, type: 'in' }],
      },
    })

    const store = useStockMovementsStore()
    await store.fetchMovements()

    expect(apiMock.get).toHaveBeenCalledWith('/stock-movements')
    expect(store.movements).toEqual([{ id: 1, type: 'in' }])
    expect(store.loading).toBe(false)
  })

  it('stores fetch errors', async () => {
    const failure = new Error('timeout')
    apiMock.get.mockRejectedValueOnce(failure)

    const store = useStockMovementsStore()
    await store.fetchMovements()

    expect(store.error).toBe('timeout')
  })

  it('creates a stock movement via the API', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        data: { id: 3, type: 'out' },
      },
    })

    const store = useStockMovementsStore()
    await expect(store.createMovement({ item_id: 1, quantity: 2 })).resolves.toEqual({ id: 3, type: 'out' })

    expect(apiMock.post).toHaveBeenCalledWith('/stock-movements', {
      item_id: 1,
      quantity: 2,
    })
  })
})
