/**
 * Store Pinia - auth.ts
 * Capa TypeScript alineada con endpoints reales backend (/auth/*)
 * sin romper el flujo legacy existente en JS.
 */

import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import type { User } from '@/types/common';
import api from '@/services/api';

type RegisterPayload = {
  email: string;
  username: string;
  full_name: string;
  password: string;
  phone?: string | null;
  turnstile_token?: string | null;
};

function buildAuthHeaders(token: string | null): Record<string, string> {
  if (!token) {
    return {};
  }
  return { Authorization: `Bearer ${token}` };
}

function toRegisterPayload(data: Record<string, any>): RegisterPayload {
  const email = String(data?.email || '').trim();
  const username = String(data?.username || '').trim() || (email.split('@')[0] || 'usuario');
  const fullNameFromForm = String(data?.full_name || '').trim();
  const composedFullName = `${String(data?.firstName || '').trim()} ${String(data?.lastName || '').trim()}`.trim();
  const full_name = fullNameFromForm || composedFullName || username;

  return {
    email,
    username,
    full_name,
    password: String(data?.password || ''),
    phone: data?.phone || null,
    turnstile_token: data?.turnstile_token || null,
  };
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'));
  const isAuthenticated = ref<boolean>(!!token.value);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const requires2FA = ref(false);
  const twoFAChallengeId = ref<string | null>(null);

  // Computed
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isTechnician = computed(() => user.value?.role === 'technician');

  function setTokens(access: string | null, refresh: string | null): void {
    token.value = access;
    refreshToken.value = refresh;
    if (access) {
      localStorage.setItem('access_token', access);
    } else {
      localStorage.removeItem('access_token');
    }
    if (refresh) {
      localStorage.setItem('refresh_token', refresh);
    } else {
      localStorage.removeItem('refresh_token');
    }
  }

  function clearSession(): void {
    setTokens(null, null);
    user.value = null;
    isAuthenticated.value = false;
    error.value = null;
    requires2FA.value = false;
    twoFAChallengeId.value = null;
  }

  /**
   * Inicializar auth desde sesión existente
   */
  async function checkAuth(): Promise<void> {
    if (!token.value) {
      clearSession();
      return;
    }
    try {
      await fetchUserInfo();
    } catch {
      clearSession();
    }
  }

  /**
   * Login
   */
  async function login(email: string, password: string, turnstileToken?: string): Promise<{ requires_2fa?: boolean; challenge_id?: string | null }> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        turnstile_token: turnstileToken || null,
      });
      const payload = response.data || {};

      if (payload?.requires_2fa) {
        requires2FA.value = true;
        twoFAChallengeId.value = String(payload.challenge_id || '');
        isAuthenticated.value = false;
        return { requires_2fa: true, challenge_id: twoFAChallengeId.value };
      }

      if (!payload?.access_token || !payload?.refresh_token) {
        throw new Error('Login failed');
      }

      setTokens(String(payload.access_token), String(payload.refresh_token));
      requires2FA.value = false;
      twoFAChallengeId.value = null;
      await fetchUserInfo();
      return {};
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'Login failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Registrar
   */
  async function register(data: Record<string, any>): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      const payload = toRegisterPayload(data);
      await api.post('/auth/register', payload);
      // Register no inicia sesión en backend actual.
      isAuthenticated.value = false;
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'Registration failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Verify 2FA
   */
  async function verifyTwoFactor(challengeId: string | null, code: string): Promise<void> {
    const resolvedChallengeId = challengeId || twoFAChallengeId.value;
    if (!resolvedChallengeId) {
      throw new Error('No 2FA challenge in progress');
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/verify-2fa', {
        challenge_id: resolvedChallengeId,
        code,
      });
      const payload = response.data || {};

      if (!payload?.access_token || !payload?.refresh_token) {
        throw new Error('2FA verification failed');
      }

      setTokens(String(payload.access_token), String(payload.refresh_token));
      requires2FA.value = false;
      twoFAChallengeId.value = null;
      await fetchUserInfo();
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'Invalid code';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // Alias aditivo para compatibilidad con nombre anterior.
  async function verify2FA(code: string): Promise<void> {
    await verifyTwoFactor(twoFAChallengeId.value, code);
  }

  /**
   * Fetch user info
   */
  async function fetchUserInfo(): Promise<void> {
    if (!token.value) {
      clearSession();
      return;
    }
    try {
      const response = await api.get('/auth/me', {
        headers: buildAuthHeaders(token.value),
      });
      user.value = response.data as User;
      isAuthenticated.value = true;
    } catch (err) {
      clearSession();
      throw err;
    }
  }

  /**
   * Refresh access token
   */
  async function refreshAccessToken(): Promise<boolean> {
    if (!refreshToken.value) {
      clearSession();
      return false;
    }
    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value,
      });
      const payload = response.data || {};
      if (!payload?.access_token || !payload?.refresh_token) {
        clearSession();
        return false;
      }
      setTokens(String(payload.access_token), String(payload.refresh_token));
      return true;
    } catch {
      clearSession();
      return false;
    }
  }

  /**
   * Logout
   */
  async function logout(): Promise<void> {
    try {
      await api.post('/auth/logout', {}, {
        headers: buildAuthHeaders(token.value),
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      clearSession();
    }
  }

  /**
   * Request password reset
   */
  async function requestPasswordReset(email: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await api.post('/auth/forgot-password', { email });
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'Password reset request failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Confirm password reset
   */
  async function confirmPasswordReset(tokenValue: string, newPassword: string): Promise<void> {
    isLoading.value = true;
    error.value = null;
    try {
      await api.post('/auth/reset-password', {
        token: tokenValue,
        new_password: newPassword,
      });
    } catch (err: any) {
      error.value = err?.response?.data?.detail || 'Password reset confirmation failed';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete account (placeholder de compatibilidad)
   */
  async function deleteAccount(password: string): Promise<void> {
    void password;
    throw new Error('deleteAccount endpoint not implemented in backend');
  }

  /**
   * Check if user has permission
   */
  function hasPermission(permission: string): boolean {
    return user.value?.permissions?.includes(permission) ?? false;
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
    token,
    refreshToken,
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
    verifyTwoFactor,
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
