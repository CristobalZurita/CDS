import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({
  post: vi.fn(),
  get: vi.fn(),
}))

vi.mock('@/services/api', () => ({
  api: apiMock,
}))

import { useAuth } from '@composables/useAuth'

describe('useAuth composable', () => {
  const resetState = () => {
    const auth = useAuth()
    auth.user.value = null
    auth.token.value = null
    auth.refreshToken.value = null
    auth.isLoading.value = false
    auth.error.value = null
    return auth
  }

  beforeEach(() => {
    vi.clearAllMocks()
    resetState()
  })

  it('starts unauthenticated', () => {
    const auth = useAuth()

    expect(auth.user.value).toBeNull()
    expect(auth.token.value).toBeNull()
    expect(auth.isAuthenticated.value).toBe(false)
    expect(auth.isAdmin.value).toBe(false)
    expect(auth.error.value).toBeNull()
  })

  it('registers a user with normalized payload', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: { id: 1, email: 'ana@test.com', full_name: 'Ana Test' },
    })

    const auth = useAuth()
    const result = await auth.register({
      email: 'ana@test.com',
      username: 'ana',
      full_name: 'Ana Test',
      password: 'secret123',
    })

    expect(apiMock.post).toHaveBeenCalledWith('/auth/register', {
      email: 'ana@test.com',
      username: 'ana',
      full_name: 'Ana Test',
      password: 'secret123',
      phone: null,
      turnstile_token: null,
    })
    expect(result).toEqual({ id: 1, email: 'ana@test.com', full_name: 'Ana Test' })
    expect(auth.user.value).toEqual({ id: 1, email: 'ana@test.com', full_name: 'Ana Test' })
    expect(auth.isLoading.value).toBe(false)
  })

  it('logs in, stores tokens and fetches the current user', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        access_token: 'access-1',
        refresh_token: 'refresh-1',
      },
    })
    apiMock.get.mockResolvedValueOnce({
      data: {
        id: 7,
        email: 'user@test.com',
        role: 'admin',
      },
    })

    const auth = useAuth()
    const user = await auth.login('user@test.com', 'secret', 'turnstile-token')

    expect(apiMock.post).toHaveBeenCalledWith('/auth/login', {
      email: 'user@test.com',
      password: 'secret',
      turnstile_token: 'turnstile-token',
    })
    expect(apiMock.get).toHaveBeenCalledWith('/auth/me', {
      headers: {
        Authorization: 'Bearer access-1',
      },
    })
    expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'access-1')
    expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-1')
    expect(user).toEqual({ id: 7, email: 'user@test.com', role: 'admin' })
    expect(auth.user.value).toEqual({ id: 7, email: 'user@test.com', role: 'admin' })
    expect(auth.isAuthenticated.value).toBe(true)
    expect(auth.isAdmin.value).toBe(true)
  })

  it('returns the 2FA challenge without authenticating the session', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        requires_2fa: true,
        challenge_id: 'challenge-1',
      },
    })

    const auth = useAuth()
    const result = await auth.login('user@test.com', 'secret')

    expect(result).toEqual({
      requires_2fa: true,
      challenge_id: 'challenge-1',
    })
    expect(auth.token.value).toBeNull()
    expect(auth.user.value).toBeNull()
    expect(auth.isAuthenticated.value).toBe(false)
  })

  it('verifies two-factor authentication and hydrates the user', async () => {
    apiMock.post.mockResolvedValueOnce({
      data: {
        access_token: 'access-2',
        refresh_token: 'refresh-2',
      },
    })
    apiMock.get.mockResolvedValueOnce({
      data: {
        id: 9,
        email: 'mfa@test.com',
        role: 'user',
      },
    })

    const auth = useAuth()
    const user = await auth.verifyTwoFactor('challenge-2', '123456')

    expect(apiMock.post).toHaveBeenCalledWith('/auth/verify-2fa', {
      challenge_id: 'challenge-2',
      code: '123456',
    })
    expect(user).toEqual({
      id: 9,
      email: 'mfa@test.com',
      role: 'user',
    })
    expect(auth.token.value).toBe('access-2')
    expect(auth.refreshToken.value).toBe('refresh-2')
  })

  it('refreshes the access token and persists the new pair', async () => {
    const auth = useAuth()
    auth.refreshToken.value = 'refresh-old'

    apiMock.post.mockResolvedValueOnce({
      data: {
        access_token: 'access-new',
        refresh_token: 'refresh-new',
      },
    })

    const result = await auth.refreshAccessToken()

    expect(apiMock.post).toHaveBeenCalledWith('/auth/refresh', {
      refresh_token: 'refresh-old',
    })
    expect(result).toBe('access-new')
    expect(auth.token.value).toBe('access-new')
    expect(auth.refreshToken.value).toBe('refresh-new')
    expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'access-new')
    expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-new')
  })

  it('clears the session when trying to refresh without refresh token', async () => {
    const auth = useAuth()
    auth.user.value = { id: 1, role: 'user' }
    auth.token.value = 'access-old'
    auth.refreshToken.value = null

    const result = await auth.refreshAccessToken()

    expect(result).toBeNull()
    expect(auth.user.value).toBeNull()
    expect(auth.token.value).toBeNull()
    expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
    expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token')
  })

  it('logs out locally when fetchUserInfo fails', async () => {
    const auth = useAuth()
    auth.token.value = 'expired-token'
    apiMock.get.mockRejectedValueOnce(new Error('expired'))

    await expect(auth.fetchUserInfo()).rejects.toThrow('expired')

    expect(auth.user.value).toBeNull()
    expect(auth.token.value).toBeNull()
    expect(auth.refreshToken.value).toBeNull()
  })

  it('checks an existing session when a token is already present', async () => {
    const auth = useAuth()
    auth.token.value = 'existing-token'
    apiMock.get.mockResolvedValueOnce({
      data: {
        id: 12,
        email: 'persisted@test.com',
        role: 'user',
      },
    })

    await auth.checkAuth()

    expect(apiMock.get).toHaveBeenCalledWith('/auth/me', {
      headers: {
        Authorization: 'Bearer existing-token',
      },
    })
    expect(auth.user.value?.email).toBe('persisted@test.com')
    expect(auth.isAuthenticated.value).toBe(true)
  })

  it('exposes logout as a synchronous session reset', () => {
    const auth = useAuth()
    auth.user.value = { id: 1, role: 'user' }
    auth.token.value = 'access'
    auth.refreshToken.value = 'refresh'

    auth.logout()

    expect(auth.user.value).toBeNull()
    expect(auth.token.value).toBeNull()
    expect(auth.refreshToken.value).toBeNull()
  })
})
