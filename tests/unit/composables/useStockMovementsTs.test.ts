import { beforeEach, describe, expect, it, vi } from 'vitest'

const storeToRefsMock = vi.hoisted(() => vi.fn())
const storeMock = vi.hoisted(() => ({
  fetchMovements: vi.fn(),
  createMovement: vi.fn(),
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: storeToRefsMock,
  }
})

vi.mock('@/stores/stockMovements', () => ({
  useStockMovementsStore: () => storeMock,
}))

import { useStockMovements } from '@/composables/useStockMovements.ts'

describe('useStockMovements.ts compatibility wrapper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('uses loading ref when store exposes it', () => {
    const refs = {
      movements: { value: [{ id: 'm1' }] },
      loading: { value: false },
      isLoading: { value: true },
      error: { value: null },
    }
    storeToRefsMock.mockReturnValue(refs)

    const composable = useStockMovements()

    expect(composable.movements).toBe(refs.movements)
    expect(composable.loading).toBe(refs.loading)
    expect(composable.error).toBe(refs.error)
    expect(composable.fetchMovements).toBe(storeMock.fetchMovements)
    expect(composable.createMovement).toBe(storeMock.createMovement)
  })

  it('falls back to isLoading when loading ref is missing', () => {
    const refs = {
      movements: { value: [] },
      isLoading: { value: true },
      error: { value: 'error' },
    }
    storeToRefsMock.mockReturnValue(refs)

    const composable = useStockMovements()

    expect(composable.loading).toBe(refs.isLoading)
    expect(composable.error).toBe(refs.error)
  })
})
