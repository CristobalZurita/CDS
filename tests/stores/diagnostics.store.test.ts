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

import { useDiagnosticsStore } from '@stores/diagnostics'

describe('diagnostics store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('starts with the current diagnostics state shape', () => {
    const store = useDiagnosticsStore()

    expect(store.diagnostics).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('loads diagnostics from the API', async () => {
    apiMock.get.mockResolvedValueOnce([{ id: 1, findings: 'Noise floor' }])

    const store = useDiagnosticsStore()
    await store.fetchDiagnostics()

    expect(apiMock.get).toHaveBeenCalledWith('/diagnostic')
    expect(store.diagnostics).toEqual([{ id: 1, findings: 'Noise floor' }])
    expect(store.loading).toBe(false)
  })

  it('stores fetch errors', async () => {
    const failure = { message: 'down' }
    apiMock.get.mockRejectedValueOnce(failure)

    const store = useDiagnosticsStore()
    await store.fetchDiagnostics()

    expect(store.error).toEqual(failure)
  })

  it('delegates create, update and delete actions to the API', async () => {
    apiMock.post.mockResolvedValueOnce({ id: 2 })
    apiMock.put.mockResolvedValueOnce({ id: 2, findings: 'Updated' })
    apiMock.delete.mockResolvedValueOnce({ ok: true })

    const store = useDiagnosticsStore()

    await expect(store.createDiagnostic({ repair_id: 4 })).resolves.toEqual({ id: 2 })
    await expect(store.updateDiagnostic(2, { findings: 'Updated' })).resolves.toEqual({ id: 2, findings: 'Updated' })
    await expect(store.deleteDiagnostic(2)).resolves.toEqual({ ok: true })

    expect(apiMock.post).toHaveBeenCalledWith('/diagnostic/calculate', { repair_id: 4 })
    expect(apiMock.put).toHaveBeenCalledWith('/diagnostic/2', { findings: 'Updated' })
    expect(apiMock.delete).toHaveBeenCalledWith('/diagnostic/2')
  })
})
