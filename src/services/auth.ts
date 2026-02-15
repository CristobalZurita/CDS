/**
 * Auth Service - JWT Management con HttpOnly Cookies
 * ✅ SEGURO: Tokens en HttpOnly cookies (no accesibles via JS)
 * ✅ XSS-proof: Aunque hackeen JS, no pueden acceder al token
 * Uso: useAuthService().login(), useAuthService().logout(), etc
 */

import { ref } from 'vue';
import type { User, AuthToken } from '@/types/common';
import api from './api';
import { getCSRFToken } from './security';

class AuthService {
  private user = ref<User | null>(null);
  private isAuthenticated = ref(false);
  private isLoading = ref(false);

  /**
   * Inicializar autenticación - Restaurar sesión si existe
   */
  async initialize(): Promise<void> {
    try {
      // Backend verifica HttpOnly cookie y retorna usuario
      const response = await api.get('/users/me');
      if (response.data.success) {
        this.user.value = response.data.data;
        this.isAuthenticated.value = true;
      }
    } catch (error) {
      console.debug('No active session');
      this.isAuthenticated.value = false;
    }
  }

  /**
   * Login - Obtener token (guardado en HttpOnly cookie por backend)
   */
  async login(email: string, password: string): Promise<boolean> {
    this.isLoading.value = true;
    try {
      const response = await api.post('/users/login', {
        email,
        password,
      });

      if (response.data.success) {
        this.user.value = response.data.data.user;
        this.isAuthenticated.value = true;
        // Token guardado automáticamente en HttpOnly cookie por backend
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      this.isLoading.value = false;
    }
  }

  /**
   * Register - Crear nueva cuenta
   */
  async register(email: string, password: string, firstName: string, lastName: string): Promise<boolean> {
    this.isLoading.value = true;
    try {
      const response = await api.post('/users/register', {
        email,
        password,
        firstName,
        lastName,
      });

      if (response.data.success) {
        this.user.value = response.data.data.user;
        this.isAuthenticated.value = true;
        return true;
      }
      return false;
    } catch (error) {
      console.error('Register failed:', error);
      return false;
    } finally {
      this.isLoading.value = false;
    }
  }

  /**
   * Logout - Limpiar sesión
   */
  async logout(): Promise<void> {
    try {
      await api.post('/users/logout', {}, {
        headers: { 'X-CSRF-Token': getCSRFToken() || '' },
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.user.value = null;
      this.isAuthenticated.value = false;
      // Backend limpia HttpOnly cookie
    }
  }

  /**
   * Refresh Token - Renovar sesión si está por expirar
   */
  async refreshToken(): Promise<boolean> {
    try {
      const response = await api.post('/users/refresh-token', {});
      if (response.data.success) {
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.isAuthenticated.value = false;
      return false;
    }
  }

  /**
   * Request Password Reset - Solicitar reset
   */
  async requestPasswordReset(email: string): Promise<boolean> {
    try {
      const response = await api.post('/users/password-reset', { email });
      return response.data.success;
    } catch (error) {
      console.error('Password reset request failed:', error);
      return false;
    }
  }

  /**
   * Confirm Password Reset - Confirmar con token
   */
  async confirmPasswordReset(token: string, newPassword: string): Promise<boolean> {
    try {
      const response = await api.post('/users/confirm-reset', {
        token,
        newPassword,
      });
      return response.data.success;
    } catch (error) {
      console.error('Password reset confirmation failed:', error);
      return false;
    }
  }

  /**
   * Delete Account - Eliminar cuenta (requiere confirmación)
   */
  async deleteAccount(password: string): Promise<boolean> {
    try {
      const response = await api.delete('/users/me', {
        data: { password },
        headers: { 'X-CSRF-Token': getCSRFToken() || '' },
      });

      if (response.data.success) {
        await this.logout();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Account deletion failed:', error);
      return false;
    }
  }

  /**
   * Check if user has permission
   */
  hasPermission(permission: string): boolean {
    return this.user.value?.permissions.includes(permission) ?? false;
  }

  /**
   * Check if user has role
   */
  hasRole(role: string): boolean {
    return this.user.value?.role === role;
  }

  /**
   * Getters
   */
  get currentUser() {
    return this.user;
  }

  get isAuth() {
    return this.isAuthenticated;
  }

  get loading() {
    return this.isLoading;
  }
}

// Singleton instance
export const authService = new AuthService();
