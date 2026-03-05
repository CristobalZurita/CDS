/**
 * Servicio de compatibilidad sobre el composable alineado al backend real.
 * Mantiene la API de clase sin sostener una segunda fuente de verdad.
 */

import { useAuth } from '@/composables/useAuth';

class AuthService {
  private auth = useAuth();

  async initialize(): Promise<void> {
    await this.auth.initialize();
  }

  async login(email: string, password: string, turnstileToken?: string): Promise<boolean> {
    this.auth.error.value = null;
    try {
      const result = await this.auth.login(email, password, turnstileToken || null);
      return !('requires_2fa' in result);
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  }

  async verifyTwoFactor(challengeId: string, code: string): Promise<boolean> {
    try {
      await this.auth.verifyTwoFactor(challengeId, code);
      return true;
    } catch (error) {
      console.error('2FA verification failed:', error);
      return false;
    }
  }

  async register(
    email: string,
    password: string,
    firstName: string,
    lastName: string,
    phone?: string,
    turnstileToken?: string
  ): Promise<boolean> {
    try {
      await this.auth.register({
        email,
        password,
        firstName,
        lastName,
        phone: phone || null,
        turnstile_token: turnstileToken || null,
      });
      return true;
    } catch (error) {
      console.error('Register failed:', error);
      return false;
    }
  }

  async logout(): Promise<void> {
    this.auth.logout();
  }

  async refreshToken(): Promise<boolean> {
    try {
      return Boolean(await this.auth.refreshAccessToken());
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }

  async requestPasswordReset(email: string): Promise<boolean> {
    try {
      return await this.auth.requestPasswordReset(email);
    } catch (error) {
      console.error('Password reset request failed:', error);
      return false;
    }
  }

  async confirmPasswordReset(token: string, newPassword: string): Promise<boolean> {
    try {
      return await this.auth.confirmPasswordReset(token, newPassword);
    } catch (error) {
      console.error('Password reset confirmation failed:', error);
      return false;
    }
  }

  async deleteAccount(password: string): Promise<boolean> {
    return this.auth.deleteAccount(password);
  }

  hasPermission(permission: string): boolean {
    return this.auth.hasPermission(permission);
  }

  hasRole(role: string): boolean {
    return this.auth.user.value?.role === role;
  }

  get currentUser() {
    return this.auth.user;
  }

  get isAuth() {
    return this.auth.isAuthenticated;
  }

  get loading() {
    return this.auth.isLoading;
  }

  get requiresTwoFactor() {
    return this.auth.requires2FA;
  }

  get twoFactorChallengeId() {
    return this.auth.twoFAChallengeId;
  }
}

export const authService = new AuthService();
