import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
  get: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import { useAuthStore } from '@stores/auth'
import { useAuth } from '@composables/useAuth'

describe('auth store', () => {
  const resetState = () => {
    const auth = useAuth()
    auth.user.value = null
    auth.token.value = null
    auth.refreshToken.value = null
    auth.isLoading.value = false
    auth.error.value = null
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    resetState()
  })

  it('starts with the expected default state', () => {
    const store = useAuthStore()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBeNull()
    expect(store.mfaRequired).toBe(false)
    expect(store.sessionExpiry).toBeNull()
    expect(store.isAdmin).toBe(false)
  })

  it('marks the session as authenticated after a successful login', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        access_token: 'access-1',
        refresh_token: 'refresh-1',
      },
    })
    apiMock.get.mockResolvedValueOnce({
      data: {
        id: 1,
        email: 'admin@test.com',
        role: 'admin',
      },
    })

    const store = useAuthStore()
    const user = await store.login('admin@test.com', 'secret')

    expect(user).toEqual({
      id: 1,
      email: 'admin@test.com',
      role: 'admin',
    })
    expect(store.isAuthenticated).toBe(true)
    expect(store.mfaVerified).toBe(true)
    expect(store.sessionStart).not.toBeNull()
    expect(store.sessionExpiry).not.toBeNull()
    expect(store.isAdmin).toBe(true)
  })

  it('keeps the store unauthenticated when the backend requires 2FA', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        requires_2fa: true,
        challenge_id: 'challenge-1',
      },
    })

    const store = useAuthStore()
    const result = await store.login('admin@test.com', 'secret')

    expect(result).toEqual({
      requires_2fa: true,
      challenge_id: 'challenge-1',
    })
    expect(store.isAuthenticated).toBe(false)
    expect(store.requires2FA).toBe(true)
    expect(store.mfaRequired).toBe(true)
    expect(store.twoFAChallengeId).toBe('challenge-1')
  })

  it('verifies 2FA using the stored challenge id', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        access_token: 'access-2',
        refresh_token: 'refresh-2',
      },
    })
    apiMock.get.mockResolvedValueOnce({
      data: {
        id: 2,
        email: 'user@test.com',
        role: 'user',
      },
    })

    const store = useAuthStore()
    store.twoFAChallengeId = 'challenge-2'
    store.mfaRequired = true

    const user = await store.verify2FA('123456')

    expect(user).toEqual({
      id: 2,
      email: 'user@test.com',
      role: 'user',
    })
    expect(store.isAuthenticated).toBe(true)
    expect(store.twoFAChallengeId).toBeNull()
    expect(store.requires2FA).toBe(false)
    expect(store.mfaRequired).toBe(false)
  })

  it('resets auth flags on logout', async () => {
    const store = useAuthStore()
    store.user = { id: 1, role: 'user' }
    store.token = 'access'
    store.refreshToken = 'refresh'
    store.isAuthenticated = true
    store.mfaRequired = true
    store.requires2FA = true
    store.sessionExpiry = Date.now() + 1000

    await store.logout()

    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
    expect(store.refreshToken).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(store.mfaRequired).toBe(false)
    expect(store.requires2FA).toBe(false)
    expect(store.sessionExpiry).toBeNull()
  })

  it('refreshes the token and keeps auth state in sync', async () => {
    const store = useAuthStore()
    store.user = { id: 3, role: 'user' }
    store.token = 'access-old'
    store.refreshToken = 'refresh-old'

    apiMock.post.mockResolvedValueOnce({
      data: {
        access_token: 'access-new',
        refresh_token: 'refresh-new',
      },
    })

    const token = await store.refreshAccessToken()

    expect(token).toBe('access-new')
    expect(store.token).toBe('access-new')
    expect(store.refreshToken).toBe('refresh-new')
    expect(store.isAuthenticated).toBe(true)
  })

  it('evaluates role checks and token expiration', () => {
    const store = useAuthStore()
    store.user = { id: 4, role: 'technician' }
    store.sessionExpiry = Date.now() - 1

    expect(store.hasRole('technician')).toBe(true)
    expect(store.hasRole('admin')).toBe(false)
    expect(store.isTokenExpired()).toBe(true)

    store.sessionExpiry = Date.now() + 60_000
    expect(store.isTokenExpired()).toBe(false)
  })
})
