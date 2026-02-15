/**
 * Composable useAuth.ts - Gestión de autenticación con TypeScript
 * MEJORADO: Usa authService con HttpOnly cookies en lugar de localStorage
 *
 * Proporciona:
 * - login() / register() / logout()
 * - 2FA verification
 * - Token refresh
 * - User info fetch
 */

import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { User } from '@/types/common';
import api from '@/services/api';

// Global auth state
const user = ref<User | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const requires2FA = ref(false);
const twoFAChallengeId = ref<string | null>(null);

// Computed properties
const isAuthenticated = computed(() => !!user.value);
const isAdmin = computed(() => user.value?.role === 'admin');
const isTechnician = computed(() => user.value?.role === 'technician');

export function useAuth() {
  const router = useRouter();

  /**
   * Registrar nuevo usuario
   */
  async function register(data: {
    email: string;
    firstName: string;
    lastName: string;
    password: string;
    phone?: string;
  }): Promise<User | null> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/register', {
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        password: data.password,
        phone: data.phone || null,
      });

      if (response.data.success) {
        user.value = response.data.data.user;
        return user.value;
      }
      throw new Error(response.data.error?.message || 'Registration failed');
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Error en el registro';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Login con email y password
   * Si requiere 2FA, retorna challenge_id
   */
  async function login(
    email: string,
    password: string,
    turnstileToken?: string
  ): Promise<{ user?: User; requires2FA?: boolean; challengeId?: string }> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/login', {
        email,
        password,
        turnstile_token: turnstileToken || null,
      });

      if (!response.data.success) {
        throw new Error(response.data.error?.message || 'Login failed');
      }

      // Check if 2FA required
      if (response.data.data?.requires_2fa) {
        requires2FA.value = true;
        twoFAChallengeId.value = response.data.data.challenge_id;
        return {
          requires2FA: true,
          challengeId: response.data.data.challenge_id,
        };
      }

      // Login exitoso - obtener info del usuario
      user.value = response.data.data.user;
      // Token se guarda automáticamente en HttpOnly cookie por backend

      return { user: user.value };
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Email o contraseña incorrectos';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Verificar 2FA code
   */
  async function verifyTwoFactor(code: string): Promise<User | null> {
    if (!twoFAChallengeId.value) {
      error.value = 'No 2FA challenge in progress';
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/verify-2fa', {
        challenge_id: twoFAChallengeId.value,
        code,
      });

      if (response.data.success) {
        user.value = response.data.data.user;
        requires2FA.value = false;
        twoFAChallengeId.value = null;
        return user.value;
      }

      throw new Error(response.data.error?.message || '2FA verification failed');
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Código inválido';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Obtener información del usuario actual
   * Endpoint verifica HttpOnly cookie automáticamente
   */
  async function fetchUserInfo(): Promise<User | null> {
    try {
      const response = await api.get('/users/me');

      if (response.data.success) {
        user.value = response.data.data;
        return user.value;
      }

      logout();
      return null;
    } catch (err) {
      // Token expirado o inválido
      logout();
      throw err;
    }
  }

  /**
   * Refrescar access token
   * Backend valida refresh_token en HttpOnly cookie
   */
  async function refreshAccessToken(): Promise<boolean> {
    try {
      const response = await api.post('/users/refresh-token', {});

      if (response.data.success) {
        // Token se actualiza automáticamente en HttpOnly cookie
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
   * Logout - Limpiar sesión
   */
  async function logout(): Promise<void> {
    try {
      await api.post('/users/logout', {});
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      user.value = null;
      error.value = null;
      requires2FA.value = false;
      twoFAChallengeId.value = null;
      // Cookies se limpian automáticamente por backend
    }
  }

  /**
   * Solicitar password reset
   */
  async function requestPasswordReset(email: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/password-reset', { email });

      if (response.data.success) {
        return true;
      }

      throw new Error(response.data.error?.message || 'Password reset request failed');
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Error enviando reset';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Confirmar password reset con token
   */
  async function confirmPasswordReset(token: string, newPassword: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/users/confirm-reset', {
        token,
        newPassword,
      });

      if (response.data.success) {
        return true;
      }

      throw new Error(response.data.error?.message || 'Password reset confirmation failed');
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Error confirmando reset';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Eliminar cuenta
   */
  async function deleteAccount(password: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.delete('/users/me', {
        data: { password },
      });

      if (response.data.success) {
        await logout();
        return true;
      }

      throw new Error(response.data.error?.message || 'Account deletion failed');
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || 'Error eliminando cuenta';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Verificar si usuario tiene permiso
   */
  function hasPermission(permission: string): boolean {
    return user.value?.permissions.includes(permission) ?? false;
  }

  /**
   * Inicializar autenticación desde sesión actual
   */
  async function initialize(): Promise<void> {
    try {
      await fetchUserInfo();
    } catch (err) {
      console.debug('No active session');
    }
  }

  return {
    // State
    user,
    isLoading,
    error,
    requires2FA,
    twoFAChallengeId,

    // Computed
    isAuthenticated,
    isAdmin,
    isTechnician,

    // Methods
    register,
    login,
    verifyTwoFactor,
    fetchUserInfo,
    refreshAccessToken,
    logout,
    requestPasswordReset,
    confirmPasswordReset,
    deleteAccount,
    hasPermission,
    initialize,
  };
}
