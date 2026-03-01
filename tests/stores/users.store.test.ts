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

import { useUsersStore } from '@stores/users'

describe('users store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('starts empty', () => {
    const store = useUsersStore()

    expect(store.users).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })

  it('fetches users successfully', async () => {
    apiMock.get.mockResolvedValueOnce([{ id: 1, email: 'admin@test.com' }])

    const store = useUsersStore()
    await store.fetchUsers()

    expect(apiMock.get).toHaveBeenCalledWith('/users')
    expect(store.users).toEqual([{ id: 1, email: 'admin@test.com' }])
    expect(store.error).toBeNull()
  })

  it('captures fetch errors and clears stale users', async () => {
    const failure = { message: '403' }
    apiMock.get.mockRejectedValueOnce(failure)

    const store = useUsersStore()
    store.users = [{ id: 99 }]

    await store.fetchUsers()

    expect(store.users).toEqual([])
    expect(store.error).toEqual(failure)
  })

  it('adds, updates and deletes users', async () => {
    apiMock.post.mockResolvedValueOnce({ id: 2, email: 'new@test.com' })
    apiMock.put.mockResolvedValueOnce({ id: 2, email: 'updated@test.com' })
    apiMock.delete.mockResolvedValueOnce({ ok: true })

    const store = useUsersStore()
    store.users = [{ id: 1, email: 'old@test.com' }]

    await expect(store.createUser({ email: 'new@test.com' })).resolves.toEqual({ id: 2, email: 'new@test.com' })
    await expect(store.updateUser(2, { email: 'updated@test.com' })).resolves.toEqual({ id: 2, email: 'updated@test.com' })
    await expect(store.deleteUser(1)).resolves.toEqual({ ok: true })

    expect(apiMock.post).toHaveBeenCalledWith('/users/', { email: 'new@test.com' })
    expect(apiMock.put).toHaveBeenCalledWith('/users/2', { email: 'updated@test.com' })
    expect(apiMock.delete).toHaveBeenCalledWith('/users/1')
    expect(store.users).toEqual([{ id: 2, email: 'updated@test.com' }])
  })
})
