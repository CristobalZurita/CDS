/**
 * Store Pinia - auth.ts (TypeScript)
 * Gestiona el estado global de autenticación
 *
 * Uso en componentes:
 * import { useAuthStore } from '@/stores/auth'
 * const auth = useAuthStore()
 * auth.login(email, password)
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/common';
import type { AuthStoreState, AuthStoreActions, RegisterFormData } from '@/types/stores';
import api from '@/services/api';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const isAuthenticated = ref(false);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const requires2FA = ref(false);
  const twoFAChallengeId = ref<string | null>(null);

  // Computed
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isTechnician = computed(() => user.value?.role === 'technician');

  /**
   * Inicializar auth desde sesión existente
   */
  async function checkAuth(): Promise<void> {
    try {
      const response = await api.get('/users/me');
      if (response.data.success) {
        user.value = response.data.data;
        isAuthenticated.value = true;
        error.value = null;
      }
    } catch (err: any) {
      isAuthenticated.value = false;
      user.value = null;
    }
  }

  /**
   * Login
   */
  async function login(email: string, password: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/login', { email, password });

      if (!response.data.success) {
        throw new Error(response.data.error?.message || 'Login failed');
      }

      // Check 2FA
      if (response.data.data?.requires_2fa) {
        requires2FA.value = true;
        twoFAChallengeId.value = response.data.data.challenge_id;
        return;
      }

      user.value = response.data.data.user;
      isAuthenticated.value = true;
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Registrar
   */
  async function register(data: RegisterFormData): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/register', data);

      if (!response.data.success) {
        throw new Error(response.data.error?.message || 'Registration failed');
      }

      user.value = response.data.data.user;
      isAuthenticated.value = true;
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Registration failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Verify 2FA
   */
  async function verify2FA(code: string): Promise<void> {
    if (!twoFAChallengeId.value) {
      throw new Error('No 2FA challenge in progress');
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/verify-2fa', {
        challenge_id: twoFAChallengeId.value,
        code,
      });

      if (!response.data.success) {
        throw new Error(response.data.error?.message || '2FA verification failed');
      }

      user.value = response.data.data.user;
      isAuthenticated.value = true;
      requires2FA.value = false;
      twoFAChallengeId.value = null;
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Invalid code';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch user info
   */
  async function fetchUserInfo(): Promise<void> {
    try {
      const response = await api.get('/users/me');

      if (response.data.success) {
        user.value = response.data.data;
        isAuthenticated.value = true;
      } else {
        logout();
      }
    } catch (err) {
      logout();
      throw err;
    }
  }

  /**
   * Refresh access token
   */
  async function refreshAccessToken(): Promise<boolean> {
    try {
      const response = await api.post('/users/refresh-token', {});

      if (response.data.success) {
        return true;
      }

      logout();
      return false;
    } catch (err) {
      logout();
      return false;
    }
  }

  /**
   * Logout
   */
  async function logout(): Promise<void> {
    try {
      await api.post('/users/logout', {});
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      user.value = null;
      isAuthenticated.value = false;
      error.value = null;
      requires2FA.value = false;
      twoFAChallengeId.value = null;
    }
  }

  /**
   * Request password reset
   */
  async function requestPasswordReset(email: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/password-reset', { email });

      if (!response.data.success) {
        throw new Error(response.data.error?.message || 'Request failed');
      }
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Password reset request failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Confirm password reset
   */
  async function confirmPasswordReset(token: string, newPassword: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/confirm-reset', {
        token,
        newPassword,
      });

      if (!response.data.success) {
        throw new Error(response.data.error?.message || 'Confirmation failed');
      }
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Password reset confirmation failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete account
   */
  async function deleteAccount(password: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.delete('/users/me', {
        data: { password },
      });

      if (!response.data.success) {
        throw new Error(response.data.error?.message || 'Deletion failed');
      }

      await logout();
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Account deletion failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Check if user has permission
   */
  function hasPermission(permission: string): boolean {
    return user.value?.permissions.includes(permission) ?? false;
  }

  /**
   * Check if user has role
   */
  function hasRole(role: string): boolean {
    return user.value?.role === role;
  }

  /**
   * Set error message
   */
  function setError(msg: string): void {
    error.value = msg;
  }

  return {
    // State
    user,
    isAuthenticated,
    isLoading,
    error,
    requires2FA,
    twoFAChallengeId,

    // Computed
    isAdmin,
    isTechnician,

    // Actions
    checkAuth,
    login,
    register,
    verify2FA,
    fetchUserInfo,
    refreshAccessToken,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    deleteAccount,
    hasPermission,
    hasRole,
    setError,
  };
});
