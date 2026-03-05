import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiService = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  deleteRequest: vi.fn(),
  handleApiError: vi.fn(),
}))

vi.mock('@/services/api', () => apiService)

import { useApi } from '@/composables/useApi.ts'

describe('useApi.ts compatibility wrapper', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('delegates CRUD calls to the service layer', async () => {
    apiService.get.mockResolvedValueOnce({ data: { ok: true } })
    apiService.post.mockResolvedValueOnce({ data: { id: 1 } })
    apiService.put.mockResolvedValueOnce({ data: { updated: true } })
    apiService.patch.mockResolvedValueOnce({ data: { patched: true } })
    apiService.deleteRequest.mockResolvedValueOnce({ data: { deleted: true } })

    const api = useApi()

    await api.get('/items', { params: { page: 1 } })
    await api.post('/items', { name: 'Synth' }, { headers: { 'X-Request': '1' } })
    await api.put('/items/1', { name: 'Updated' }, {})
    await api.patch('/items/1', { active: false }, {})
    await api.delete('/items/1', { params: { hard: false } })

    expect(apiService.get).toHaveBeenCalledWith('/items', { params: { page: 1 } })
    expect(apiService.post).toHaveBeenCalledWith(
      '/items',
      { name: 'Synth' },
      { headers: { 'X-Request': '1' } }
    )
    expect(apiService.put).toHaveBeenCalledWith('/items/1', { name: 'Updated' }, {})
    expect(apiService.patch).toHaveBeenCalledWith('/items/1', { active: false }, {})
    expect(apiService.deleteRequest).toHaveBeenCalledWith('/items/1', { params: { hard: false } })
  })

  it('exposes handleApiError passthrough', () => {
    const api = useApi()
    const err = new Error('boom')

    api.handleApiError(err)

    expect(apiService.handleApiError).toHaveBeenCalledWith(err)
  })
})
