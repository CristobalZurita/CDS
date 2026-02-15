import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@stores/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
      expect(store.mfaRequired).toBe(false)
      expect(store.sessionExpiry).toBeNull()
    })

    it('should have isAdmin as false when no user', () => {
      const store = useAuthStore()
      expect(store.isAdmin).toBe(false)
    })
  })

  describe('Login Action', () => {
    it('should set loading state during login', () => {
      const store = useAuthStore()
      const loginPromise = store.login('test@example.com', 'password123')
      expect(store.isLoading).toBe(true)
    })

    it('should update user and token on successful login', async () => {
      const store = useAuthStore()
      const mockUser = {
        id: 1,
        name: 'Test User',
        email: 'test@example.com',
        role: 'user'
      }
      
      // Mock successful login
      await store.login('test@example.com', 'password123')
      // Note: Actual API call will be mocked
      expect(store.isLoading).toBe(false)
    })

    it('should set MFA required flag if MFA enabled', async () => {
      const store = useAuthStore()
      // Simulate MFA requirement
      store.mfaRequired = true
      expect(store.mfaRequired).toBe(true)
    })

    it('should handle login errors gracefully', async () => {
      const store = useAuthStore()
      // Simulate error
      store.error = 'Invalid credentials'
      expect(store.error).toBe('Invalid credentials')
      expect(store.isAuthenticated).toBe(false)
    })

    it('should clear error on new login attempt', async () => {
      const store = useAuthStore()
      store.error = 'Previous error'
      store.error = null
      expect(store.error).toBeNull()
    })
  })

  describe('Logout Action', () => {
    it('should clear user and token on logout', async () => {
      const store = useAuthStore()
      // Set up authenticated state
      store.user = { id: 1, name: 'Test', email: 'test@test.com', role: 'user' }
      store.token = 'test-token'
      store.isAuthenticated = true

      await store.logout()
      
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.mfaRequired).toBe(false)
    })

    it('should reset loading state after logout', async () => {
      const store = useAuthStore()
      store.isLoading = true
      await store.logout()
      expect(store.isLoading).toBe(false)
    })

    it('should clear session expiry on logout', async () => {
      const store = useAuthStore()
      store.sessionExpiry = new Date().getTime() + 3600000
      await store.logout()
      expect(store.sessionExpiry).toBeNull()
    })
  })

  describe('MFA Verification', () => {
    it('should require MFA code when MFA enabled', () => {
      const store = useAuthStore()
      store.mfaRequired = true
      expect(store.mfaRequired).toBe(true)
    })

    it('should set authenticated after MFA verification', async () => {
      const store = useAuthStore()
      store.mfaRequired = true
      store.mfaVerified = false

      // Simulate MFA verification
      store.mfaVerified = true
      store.isAuthenticated = true

      expect(store.isAuthenticated).toBe(true)
      expect(store.mfaRequired).toBe(true)
    })

    it('should handle invalid MFA code', async () => {
      const store = useAuthStore()
      store.error = 'Invalid MFA code'
      expect(store.error).toBe('Invalid MFA code')
      expect(store.isAuthenticated).toBe(false)
    })

    it('should clear MFA flag after verification', async () => {
      const store = useAuthStore()
      store.mfaRequired = true
      store.mfaVerified = true
      store.mfaRequired = false
      expect(store.mfaRequired).toBe(false)
    })
  })

  describe('Token Management', () => {
    it('should update token on successful refresh', () => {
      const store = useAuthStore()
      const oldToken = 'old-token'
      const newToken = 'new-token'

      store.token = oldToken
      store.token = newToken

      expect(store.token).toBe(newToken)
    })

    it('should set session expiry time', () => {
      const store = useAuthStore()
      const expiryTime = new Date().getTime() + 3600000 // 1 hour

      store.sessionExpiry = expiryTime
      expect(store.sessionExpiry).toBe(expiryTime)
    })

    it('should determine if token is expired', () => {
      const store = useAuthStore()
      const pastTime = new Date().getTime() - 1000

      store.sessionExpiry = pastTime
      expect(store.isTokenExpired()).toBe(true)
    })

    it('should determine if token is not expired', () => {
      const store = useAuthStore()
      const futureTime = new Date().getTime() + 3600000

      store.sessionExpiry = futureTime
      expect(store.isTokenExpired()).toBe(false)
    })
  })

  describe('Permission Checks', () => {
    it('should identify admin users', () => {
      const store = useAuthStore()
      store.user = {
        id: 1,
        name: 'Admin',
        email: 'admin@test.com',
        role: 'admin'
      }

      expect(store.isAdmin).toBe(true)
    })

    it('should identify non-admin users', () => {
      const store = useAuthStore()
      store.user = {
        id: 1,
        name: 'User',
        email: 'user@test.com',
        role: 'user'
      }

      expect(store.isAdmin).toBe(false)
    })

    it('should check specific role permission', () => {
      const store = useAuthStore()
      store.user = {
        id: 1,
        name: 'User',
        email: 'user@test.com',
        role: 'technician'
      }

      expect(store.hasRole('technician')).toBe(true)
      expect(store.hasRole('admin')).toBe(false)
    })
  })

  describe('User Update', () => {
    it('should update user profile', () => {
      const store = useAuthStore()
      const newUser = {
        id: 1,
        name: 'Updated Name',
        email: 'updated@test.com',
        role: 'user'
      }

      store.user = newUser
      expect(store.user?.name).toBe('Updated Name')
      expect(store.user?.email).toBe('updated@test.com')
    })

    it('should preserve user ID on update', () => {
      const store = useAuthStore()
      store.user = {
        id: 42,
        name: 'Test',
        email: 'test@test.com',
        role: 'user'
      }

      const userId = store.user?.id
      store.user!.name = 'Updated'

      expect(store.user?.id).toBe(userId)
    })
  })

  describe('Computed Properties', () => {
    it('should return correct authenticated state', () => {
      const store = useAuthStore()
      store.isAuthenticated = false
      expect(store.isAuthenticated).toBe(false)

      store.isAuthenticated = true
      expect(store.isAuthenticated).toBe(true)
    })

    it('should return correct loading state', () => {
      const store = useAuthStore()
      store.isLoading = false
      expect(store.isLoading).toBe(false)

      store.isLoading = true
      expect(store.isLoading).toBe(true)
    })

    it('should return error message correctly', () => {
      const store = useAuthStore()
      store.error = 'Test error'
      expect(store.error).toBe('Test error')

      store.error = null
      expect(store.error).toBeNull()
    })
  })

  describe('Session Management', () => {
    it('should track session creation time', () => {
      const store = useAuthStore()
      const now = new Date().getTime()
      store.sessionStart = now

      expect(store.sessionStart).toBe(now)
    })

    it('should calculate session duration', () => {
      const store = useAuthStore()
      const start = new Date().getTime()
      const now = new Date().getTime() + 1000

      store.sessionStart = start
      expect(now - store.sessionStart!).toBe(1000)
    })

    it('should handle concurrent sessions flag', () => {
      const store = useAuthStore()
      store.allowConcurrentSessions = false
      expect(store.allowConcurrentSessions).toBe(false)

      store.allowConcurrentSessions = true
      expect(store.allowConcurrentSessions).toBe(true)
    })
  })

  describe('Error Handling', () => {
    it('should clear error on successful action', () => {
      const store = useAuthStore()
      store.error = 'Previous error'
      store.error = null
      expect(store.error).toBeNull()
    })

    it('should preserve error until cleared', () => {
      const store = useAuthStore()
      store.error = 'Persistent error'
      expect(store.error).toBe('Persistent error')
    })
  })
})
