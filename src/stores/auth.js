/**
 * Store Pinia - auth.js
 * Gestiona el estado global de autenticación
 * 
 * Uso en componentes:
 * import { useAuthStore } from '@/stores/auth'
 * const auth = useAuthStore()
 * auth.login(email, password)
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const DEFAULT_SESSION_MS = 60 * 60 * 1000

export const useAuthStore = defineStore('auth', () => {
  const authComposable = useAuth()

  // State base (composable)
  const user = authComposable.user
  const token = authComposable.token
  const refreshToken = authComposable.refreshToken
  const isLoading = authComposable.isLoading
  const error = authComposable.error

  // Compatibilidad aditiva para flujo legacy y tests
  const isAuthenticated = ref(Boolean(token.value && user.value))
  const mfaRequired = ref(false)
  const mfaVerified = ref(false)
  const sessionStart = ref(null)
  const sessionExpiry = ref(null)
  const allowConcurrentSessions = ref(true)
  const requires2FA = ref(false)
  const twoFAChallengeId = ref(null)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const syncAuthState = () => {
    isAuthenticated.value = Boolean(token.value && user.value)
  }

  const setAuthenticatedSession = () => {
    isAuthenticated.value = true
    mfaRequired.value = false
    mfaVerified.value = true
    requires2FA.value = false
    sessionStart.value = Date.now()
    sessionExpiry.value = sessionStart.value + DEFAULT_SESSION_MS
  }

  // Actions (wrappers no destructivos)
  const register = async (...args) => {
    const result = await authComposable.register(...args)
    syncAuthState()
    return result
  }

  const login = async (...args) => {
    const result = await authComposable.login(...args)
    if (result?.requires_2fa) {
      requires2FA.value = true
      twoFAChallengeId.value = result.challenge_id || null
      mfaRequired.value = true
      mfaVerified.value = false
      isAuthenticated.value = false
      return result
    }

    syncAuthState()
    if (isAuthenticated.value) {
      setAuthenticatedSession()
    }
    return result
  }

  const logout = async (...args) => {
    await authComposable.logout(...args)
    isAuthenticated.value = false
    mfaRequired.value = false
    mfaVerified.value = false
    requires2FA.value = false
    twoFAChallengeId.value = null
    sessionStart.value = null
    sessionExpiry.value = null
  }

  const checkAuth = async (...args) => {
    await authComposable.checkAuth(...args)
    syncAuthState()
    if (isAuthenticated.value && !sessionStart.value) {
      sessionStart.value = Date.now()
      sessionExpiry.value = sessionStart.value + DEFAULT_SESSION_MS
    }
  }

  const fetchUserInfo = async (...args) => {
    const result = await authComposable.fetchUserInfo(...args)
    syncAuthState()
    return result
  }

  const refreshAccessToken = async (...args) => {
    const result = await authComposable.refreshAccessToken(...args)
    syncAuthState()
    if (isAuthenticated.value && !sessionExpiry.value) {
      sessionExpiry.value = Date.now() + DEFAULT_SESSION_MS
    }
    return result
  }

  const verifyTwoFactor = async (challengeId, code) => {
    const result = await authComposable.verifyTwoFactor(challengeId, code)
    twoFAChallengeId.value = null
    setAuthenticatedSession()
    return result
  }

  const verify2FA = async (code) => verifyTwoFactor(twoFAChallengeId.value, code)

  const isTokenExpired = () => {
    if (!sessionExpiry.value) {
      return true
    }
    return Date.now() >= Number(sessionExpiry.value)
  }

  const hasRole = (role) => {
    const current = String(user.value?.role || '').trim().toLowerCase()
    return current === String(role || '').trim().toLowerCase()
  }

  return {
    // State
    user,
    token,
    refreshToken,
    loading: isLoading,
    isLoading,
    error,

    // Computed
    isAuthenticated,
    isAdmin,
    mfaRequired,
    mfaVerified,
    sessionStart,
    sessionExpiry,
    allowConcurrentSessions,
    requires2FA,
    twoFAChallengeId,

    // Actions
    register,
    login,
    logout,
    checkAuth,
    fetchUserInfo,
    refreshAccessToken,
    verifyTwoFactor,
    verify2FA,
    isTokenExpired,
    hasRole
  }
})
