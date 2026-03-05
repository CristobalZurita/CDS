import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'
import { useApi } from '@composables/useApi'

const httpClient = (axios.create as ReturnType<typeof vi.fn>).mock.results[0].value

describe('useApi composable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exposes CRUD helpers', () => {
    const api = useApi()

    expect(typeof api.get).toBe('function')
    expect(typeof api.post).toBe('function')
    expect(typeof api.put).toBe('function')
    expect(typeof api.patch).toBe('function')
    expect(typeof api.delete).toBe('function')
  })

  it('returns response payloads for successful requests', async () => {
    httpClient.get.mockResolvedValueOnce({ data: { items: [1, 2] } })
    httpClient.post.mockResolvedValueOnce({ data: { id: 10 } })
    httpClient.put.mockResolvedValueOnce({ data: { id: 10, status: 'ok' } })
    httpClient.patch.mockResolvedValueOnce({ data: { updated: true } })
    httpClient.delete.mockResolvedValueOnce({ data: { deleted: true } })

    const api = useApi()

    await expect(api.get('/items')).resolves.toEqual({ items: [1, 2] })
    await expect(api.post('/items', { name: 'Test' })).resolves.toEqual({ id: 10 })
    await expect(api.put('/items/10', { status: 'ok' })).resolves.toEqual({ id: 10, status: 'ok' })
    await expect(api.patch('/items/10', { status: 'ok' })).resolves.toEqual({ updated: true })
    await expect(api.delete('/items/10')).resolves.toEqual({ deleted: true })

    expect(httpClient.get).toHaveBeenCalledWith('/items', {})
    expect(httpClient.post).toHaveBeenCalledWith('/items', { name: 'Test' }, {})
    expect(httpClient.put).toHaveBeenCalledWith('/items/10', { status: 'ok' }, {})
    expect(httpClient.patch).toHaveBeenCalledWith('/items/10', { status: 'ok' }, {})
    expect(httpClient.delete).toHaveBeenCalledWith('/items/10', {})
  })

  it('normalizes API errors with backend detail', async () => {
    httpClient.post.mockRejectedValueOnce({
      response: {
        status: 422,
        data: {
          detail: 'Datos inválidos',
          field: 'email',
        },
      },
      message: 'Request failed',
    })

    await expect(useApi().post('/users', { email: 'bad' })).rejects.toEqual({
      message: 'Datos inválidos',
      status: 422,
      data: {
        detail: 'Datos inválidos',
        field: 'email',
      },
    })
  })

  it('falls back to the transport message when the backend has no detail', async () => {
    httpClient.get.mockRejectedValueOnce(new Error('Network down'))

    await expect(useApi().get('/health')).rejects.toEqual({
      message: 'Network down',
      status: undefined,
      data: undefined,
    })
  })
})
