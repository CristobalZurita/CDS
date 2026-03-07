import { computed } from 'vue'
import { useAuthStore } from '@new/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()

  const user = computed(() => authStore.user)
  const token = computed(() => authStore.token)
  const error = computed(() => authStore.error)
  const isLoading = computed(() => authStore.isLoading)
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const isAdmin = computed(() => authStore.isAdmin)

  return {
    user,
    token,
    error,
    isLoading,
    isAuthenticated,
    isAdmin,
    login: authStore.login,
    verifyTwoFactor: authStore.verifyTwoFactor,
    register: authStore.register,
    checkAuth: authStore.checkAuth,
    logout: authStore.logout,
    requestPasswordReset: authStore.requestPasswordReset,
    confirmPasswordReset: authStore.confirmPasswordReset,
    clearSession: authStore.clearSession
  }
}
