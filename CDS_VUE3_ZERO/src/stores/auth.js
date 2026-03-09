import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  checkAuth as checkAuthRequest,
  clearStoredSession,
  confirmPasswordReset as confirmPasswordResetRequest,
  extractErrorMessage,
  getStoredToken,
  getStoredUser,
  login as loginRequest,
  logout as logoutRequest,
  pickAccessToken,
  pickUser,
  register as registerRequest,
  requestPasswordReset as requestPasswordResetRequest,
  setStoredToken,
  setStoredUser,
  verifyTwoFactor as verifyTwoFactorRequest
} from '@/services/api'

function normalizeRole(user) {
  if (!user || typeof user !== 'object') return ''
  const role = user.role || user.user_role || user.type || user.user_type || ''
  return String(role).toLowerCase()
}

function normalizeRoles(user) {
  if (!user || typeof user !== 'object') return []
  const source = user.roles || user.permissions || []
  if (!Array.isArray(source)) return []
  return source.map((entry) => String(entry).toLowerCase())
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getStoredToken())
  const user = ref(getStoredUser())
  const isLoading = ref(false)
  const error = ref('')

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => {
    const role = normalizeRole(user.value)
    const roles = normalizeRoles(user.value)
    return role.includes('admin') || roles.includes('admin')
  })

  function resetError() {
    error.value = ''
  }

  function applySession(payload) {
    const nextToken = pickAccessToken(payload)
    const nextUser = pickUser(payload)

    if (nextToken) {
      token.value = nextToken
      setStoredToken(nextToken)
    }

    if (nextUser) {
      user.value = nextUser
      setStoredUser(nextUser)
    }
  }

  function clearSession() {
    token.value = ''
    user.value = null
    clearStoredSession()
  }

  async function login(email, password, turnstileToken) {
    resetError()
    isLoading.value = true

    try {
      const payload = {
        email,
        password,
        turnstile_token: turnstileToken
      }
      const response = await loginRequest(payload)

      if (response?.requires_2fa) {
        return response
      }

      applySession(response)
      return response
    } catch (err) {
      error.value = extractErrorMessage(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function verifyTwoFactor(challengeId, code) {
    resetError()
    isLoading.value = true

    try {
      const response = await verifyTwoFactorRequest({
        challenge_id: challengeId,
        code
      })
      applySession(response)
      return response
    } catch (err) {
      error.value = extractErrorMessage(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function register(payload) {
    resetError()
    isLoading.value = true

    try {
      return await registerRequest(payload)
    } catch (err) {
      error.value = extractErrorMessage(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function checkAuth() {
    resetError()

    if (!token.value) {
      user.value = null
      return null
    }

    isLoading.value = true
    try {
      const response = await checkAuthRequest()
      const nextUser = pickUser(response) || response
      user.value = nextUser
      setStoredUser(nextUser)
      return nextUser
    } catch (err) {
      clearSession()
      error.value = extractErrorMessage(err)
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    resetError()
    isLoading.value = true

    try {
      await logoutRequest()
    } catch (err) {
      error.value = extractErrorMessage(err)
    } finally {
      clearSession()
      isLoading.value = false
    }
  }

  async function requestPasswordReset(email) {
    resetError()
    isLoading.value = true

    try {
      return await requestPasswordResetRequest({ email })
    } catch (err) {
      error.value = extractErrorMessage(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function confirmPasswordReset(tokenValue, newPassword) {
    resetError()
    isLoading.value = true

    try {
      return await confirmPasswordResetRequest({
        token: tokenValue,
        new_password: newPassword
      })
    } catch (err) {
      error.value = extractErrorMessage(err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    token,
    user,
    isLoading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    verifyTwoFactor,
    register,
    checkAuth,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    clearSession
  }
})
