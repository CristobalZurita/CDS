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
import { useAuth } from '@/composables/useAuth'

export const useAuthStore = defineStore('auth', () => {
  const authComposable = useAuth()

  // State properties
  const user = authComposable.user
  const token = authComposable.token
  const refreshToken = authComposable.refreshToken
  const isLoading = authComposable.isLoading
  const error = authComposable.error

  // Computed properties
  const isAuthenticated = authComposable.isAuthenticated
  const isAdmin = authComposable.isAdmin

  // Actions
  const register = authComposable.register
  const login = authComposable.login
  const logout = authComposable.logout
  const checkAuth = authComposable.checkAuth
  const fetchUserInfo = authComposable.fetchUserInfo
  const refreshAccessToken = authComposable.refreshAccessToken

  return {
    // State
    user,
    token,
    refreshToken,
    isLoading,
    error,

    // Computed
    isAuthenticated,
    isAdmin,

    // Actions
    register,
    login,
    logout,
    checkAuth,
    fetchUserInfo,
    refreshAccessToken
  }
})
