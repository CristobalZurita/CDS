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

import { useDiagnosticsStore } from '@stores/diagnostics'

describe('diagnostics store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    apiMock.handleApiError.mockImplementation((error) => ({
      message: error?.message ?? 'Unknown error',
    }))
  })

  it('starts with the current diagnostics state shape', () => {
    const store = useDiagnosticsStore()

    expect(store.diagnostics).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('loads diagnostics from the API', async () => {
    apiMock.get.mockResolvedValueOnce({
      data: {
        data: [{ id: 1, findings: 'Noise floor' }],
      },
    })

    const store = useDiagnosticsStore()
    await store.fetchDiagnostics()

    expect(apiMock.get).toHaveBeenCalledWith('/diagnostic')
    expect(store.diagnostics).toEqual([{ id: 1, findings: 'Noise floor' }])
    expect(store.loading).toBe(false)
  })

  it('stores fetch errors', async () => {
    const failure = new Error('down')
    apiMock.get.mockRejectedValueOnce(failure)

    const store = useDiagnosticsStore()
    await store.fetchDiagnostics()

    expect(store.error).toBe('down')
  })

  it('delegates create, update and delete actions to the API', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        data: { id: 2 },
      },
    })
    apiMock.put.mockResolvedValueOnce({
      data: {
        data: { id: 2, findings: 'Updated' },
      },
    })
    apiMock.deleteRequest.mockResolvedValueOnce({
      data: {
        data: { ok: true },
      },
    })

    const store = useDiagnosticsStore()

    await expect(store.createDiagnostic({ repair_id: 4 })).resolves.toEqual({ id: 2 })
    await expect(store.updateDiagnostic(2, { findings: 'Updated' })).resolves.toEqual({ id: 2, findings: 'Updated' })
    await expect(store.deleteDiagnostic(2)).resolves.toBeUndefined()

    expect(apiMock.post).toHaveBeenCalledWith('/diagnostic/calculate', { repair_id: 4 })
    expect(apiMock.put).toHaveBeenCalledWith('/diagnostic/2', { findings: 'Updated' })
    expect(apiMock.deleteRequest).toHaveBeenCalledWith('/diagnostic/2')
  })
})
