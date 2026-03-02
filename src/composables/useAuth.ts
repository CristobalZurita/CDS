/**
 * Composable TypeScript alineado con el backend real `/auth/*`.
 * Mantiene el mismo contrato operativo que la versión JavaScript.
 */

import { ref, computed, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import type { User } from '@/types/common';
import api from '@/services/api';

type AuthUser = User & {
  username?: string;
  fullName?: string;
  full_name?: string;
  phone?: string | null;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
};

type RegisterPayload = {
  email: string;
  username?: string;
  full_name?: string;
  firstName?: string;
  lastName?: string;
  password: string;
  phone?: string | null;
  turnstile_token?: string | null;
};

const user = ref<AuthUser | null>(null);
const token = ref<string | null>(localStorage.getItem('access_token'));
const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'));
const isLoading = ref(false);
const error = ref<string | null>(null);
const requires2FA = ref(false);
const twoFAChallengeId = ref<string | null>(null);

const isAuthenticated = computed(() => !!token.value && !!user.value);
const isAdmin = computed(() => user.value?.role === 'admin');
const isTechnician = computed(() => user.value?.role === 'technician');

function splitFullName(raw: string): { firstName: string; lastName: string } {
  const parts = String(raw || '').trim().split(/\s+/).filter(Boolean);
  return {
    firstName: parts[0] || '',
    lastName: parts.slice(1).join(' '),
  };
}

function normalizeUser(raw: any): AuthUser | null {
  if (!raw) {
    return null;
  }

  const fullName = String(
    raw.full_name ||
    raw.fullName ||
    `${raw.first_name || raw.firstName || ''} ${raw.last_name || raw.lastName || ''}`
  ).trim();
  const { firstName, lastName } = splitFullName(fullName);

  return {
    ...raw,
    id: String(raw.id ?? ''),
    email: String(raw.email || ''),
    firstName,
    lastName,
    fullName,
    full_name: fullName,
    role: String(raw.role || 'client') as AuthUser['role'],
    permissions: Array.isArray(raw.permissions) ? raw.permissions : [],
    createdAt: raw.createdAt || raw.created_at || '',
    updatedAt: raw.updatedAt || raw.updated_at || '',
    phone: raw.phone || null,
  };
}

function setTokens(accessValue: string | null, refreshValue: string | null): void {
  token.value = accessValue;
  refreshToken.value = refreshValue;

  if (accessValue) {
    localStorage.setItem('access_token', accessValue);
  } else {
    localStorage.removeItem('access_token');
  }

  if (refreshValue) {
    localStorage.setItem('refresh_token', refreshValue);
  } else {
    localStorage.removeItem('refresh_token');
  }
}

function clearSession(): void {
  user.value = null;
  error.value = null;
  requires2FA.value = false;
  twoFAChallengeId.value = null;
  setTokens(null, null);
}

function buildRegisterPayload(data: RegisterPayload) {
  const email = String(data?.email || '').trim();
  const username = String(data?.username || '').trim() || (email.split('@')[0] || 'usuario');
  const providedFullName = String(data?.full_name || '').trim();
  const composedFullName = `${String(data?.firstName || '').trim()} ${String(data?.lastName || '').trim()}`.trim();

  return {
    email,
    username,
    full_name: providedFullName || composedFullName || username,
    password: String(data?.password || ''),
    phone: data?.phone || null,
    turnstile_token: data?.turnstile_token || null,
  };
}

function buildAuthHeaders() {
  if (!token.value) {
    return {};
  }
  return {
    Authorization: `Bearer ${token.value}`,
  };
}

export function useAuth() {
  const router = getCurrentInstance() ? useRouter() : null;

  async function register(data: RegisterPayload): Promise<AuthUser | null> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/register', buildRegisterPayload(data));
      user.value = normalizeUser(response.data);
      return user.value;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error en el registro';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function login(
    email: string,
    password: string,
    turnstileToken: string | null = null
  ): Promise<AuthUser | { requires_2fa: true; challenge_id: string }> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/login', {
        email,
        password,
        turnstile_token: turnstileToken,
      });

      if (response.data?.requires_2fa) {
        requires2FA.value = true;
        twoFAChallengeId.value = String(response.data.challenge_id || '');
        return {
          requires_2fa: true,
          challenge_id: twoFAChallengeId.value,
        };
      }

      const { access_token, refresh_token } = response.data || {};
      setTokens(access_token || null, refresh_token || null);
      await fetchUserInfo();

      if (!user.value) {
        throw new Error('No se pudo cargar el usuario autenticado');
      }

      return user.value;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Email o contraseña incorrectos';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function verifyTwoFactor(challengeId: string, code: string): Promise<AuthUser | null> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/auth/verify-2fa', {
        challenge_id: challengeId,
        code,
      });
      const { access_token, refresh_token } = response.data || {};
      setTokens(access_token || null, refresh_token || null);
      requires2FA.value = false;
      twoFAChallengeId.value = null;
      await fetchUserInfo();
      return user.value;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Código inválido';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchUserInfo(): Promise<AuthUser | null> {
    if (!token.value) {
      clearSession();
      return null;
    }

    try {
      const response = await api.get('/auth/me', {
        headers: buildAuthHeaders(),
      });
      user.value = normalizeUser(response.data);
      return user.value;
    } catch (err) {
      clearSession();
      throw err;
    }
  }

  async function refreshAccessToken(): Promise<string | null> {
    if (!refreshToken.value) {
      clearSession();
      return null;
    }

    try {
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value,
      });
      const { access_token, refresh_token } = response.data || {};
      setTokens(access_token || null, refresh_token || null);
      return access_token || null;
    } catch (err) {
      clearSession();
      throw err;
    }
  }

  function logout(): void {
    clearSession();
    if (router) {
      router.push('/login');
    }
  }

  async function requestPasswordReset(email: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      await api.post('/auth/forgot-password', { email });
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error enviando reset';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function confirmPasswordReset(tokenValue: string, newPassword: string): Promise<boolean> {
    isLoading.value = true;
    error.value = null;

    try {
      await api.post('/auth/reset-password', {
        token: tokenValue,
        new_password: newPassword,
      });
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error confirmando reset';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteAccount(password: string): Promise<boolean> {
    void password;
    error.value = 'deleteAccount endpoint not implemented in backend';
    return false;
  }

  function hasPermission(permission: string): boolean {
    return user.value?.permissions?.includes(permission) ?? false;
  }

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

  async function initialize(): Promise<void> {
    try {
      await checkAuth();
    } catch {
      console.debug('No active session');
    }
  }

  return {
    user,
    token,
    refreshToken,
    isLoading,
    error,
    requires2FA,
    twoFAChallengeId,
    isAuthenticated,
    isAdmin,
    isTechnician,
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
    checkAuth,
    initialize,
  };
}
