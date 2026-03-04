import { ref } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

type AuthMock = ReturnType<typeof createAuthMock>

function createAuthMock(overrides: Partial<Record<string, any>> = {}) {
  return {
    initialize: vi.fn().mockResolvedValue(undefined),
    login: vi.fn().mockResolvedValue({ id: '1' }),
    verifyTwoFactor: vi.fn().mockResolvedValue({ id: '1' }),
    register: vi.fn().mockResolvedValue({ id: '1' }),
    logout: vi.fn(),
    refreshAccessToken: vi.fn().mockResolvedValue('new-access-token'),
    requestPasswordReset: vi.fn().mockResolvedValue(true),
    confirmPasswordReset: vi.fn().mockResolvedValue(true),
    deleteAccount: vi.fn().mockResolvedValue(false),
    hasPermission: vi.fn().mockReturnValue(true),
    user: ref({ role: 'admin', email: 'admin@example.com' }),
    isAuthenticated: ref(true),
    isLoading: ref(false),
    requires2FA: ref(false),
    twoFAChallengeId: ref('challenge-1'),
    error: ref('prev-error'),
    ...overrides,
  }
}

async function loadAuthService(authMock: AuthMock) {
  vi.resetModules()
  vi.doMock('@/composables/useAuth', () => ({
    useAuth: () => authMock,
  }))
  return import('@/services/auth')
}

describe('authService compatibility wrapper', () => {
  afterEach(() => {
    vi.resetModules()
    vi.restoreAllMocks()
  })

  it('logs in successfully and clears stale auth errors before delegating', async () => {
    const authMock = createAuthMock()
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    const { authService } = await loadAuthService(authMock)

    const ok = await authService.login('admin@example.com', 'secret12', 'turnstile-token')

    expect(ok).toBe(true)
    expect(authMock.error.value).toBeNull()
    expect(authMock.login).toHaveBeenCalledWith('admin@example.com', 'secret12', 'turnstile-token')
    expect(consoleError).not.toHaveBeenCalled()
  })

  it('returns false for 2FA challenges and failed logins', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => undefined)

    const authWith2fa = createAuthMock({
      login: vi.fn().mockResolvedValue({ requires_2fa: true, challenge_id: 'challenge-2' }),
    })
    const first = await loadAuthService(authWith2fa)
    expect(await first.authService.login('admin@example.com', 'secret12')).toBe(false)

    const authWithError = createAuthMock({
      login: vi.fn().mockRejectedValue(new Error('boom')),
    })
    const second = await loadAuthService(authWithError)
    expect(await second.authService.login('admin@example.com', 'secret12')).toBe(false)
    expect(consoleError).toHaveBeenCalled()
  })

  it('delegates register, initialize, logout and exposes the current auth getters', async () => {
    const authMock = createAuthMock({
      user: ref({ role: 'admin', email: 'owner@example.com' }),
      isAuthenticated: ref(true),
      isLoading: ref(true),
      requires2FA: ref(true),
      twoFAChallengeId: ref('challenge-9'),
    })
    const { authService } = await loadAuthService(authMock)

    await authService.initialize()
    expect(authMock.initialize).toHaveBeenCalledTimes(1)

    expect(await authService.register('owner@example.com', 'secret12', 'Owner', 'Admin')).toBe(true)
    expect(authMock.register).toHaveBeenCalledWith({
      email: 'owner@example.com',
      password: 'secret12',
      firstName: 'Owner',
      lastName: 'Admin',
      phone: null,
      turnstile_token: null,
    })

    await authService.logout()
    expect(authMock.logout).toHaveBeenCalledTimes(1)
    expect(authService.hasPermission('users.read')).toBe(true)
    expect(authService.hasRole('admin')).toBe(true)
    expect(authService.currentUser.value?.email).toBe('owner@example.com')
    expect(authService.isAuth.value).toBe(true)
    expect(authService.loading.value).toBe(true)
    expect(authService.requiresTwoFactor.value).toBe(true)
    expect(authService.twoFactorChallengeId.value).toBe('challenge-9')
  })

  it('delegates two-factor verification and account deletion', async () => {
    const authMock = createAuthMock({
      deleteAccount: vi.fn().mockResolvedValue(true),
    })
    const { authService } = await loadAuthService(authMock)

    expect(await authService.verifyTwoFactor('challenge-1', '123456')).toBe(true)
    expect(authMock.verifyTwoFactor).toHaveBeenCalledWith('challenge-1', '123456')
    expect(await authService.deleteAccount('secret12')).toBe(true)
    expect(authMock.deleteAccount).toHaveBeenCalledWith('secret12')
  })

  it('returns false when refresh and password reset helpers fail', async () => {
    const authMock = createAuthMock({
      refreshAccessToken: vi.fn().mockRejectedValue(new Error('refresh failed')),
      requestPasswordReset: vi.fn().mockRejectedValue(new Error('request failed')),
      confirmPasswordReset: vi.fn().mockRejectedValue(new Error('confirm failed')),
    })
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => undefined)
    const { authService } = await loadAuthService(authMock)

    expect(await authService.refreshToken()).toBe(false)
    expect(await authService.requestPasswordReset('user@example.com')).toBe(false)
    expect(await authService.confirmPasswordReset('token-1', 'new-secret')).toBe(false)
    expect(consoleError).toHaveBeenCalled()
  })
})
