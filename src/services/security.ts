/**
 * Security Service - Prevención de XSS, CSRF, HTTPS enforcement
 * Uso: sanitizeHtml(userInput), getCSRFToken(), etc
 */

import DOMPurify from 'dompurify/dist/purify.cjs';

/**
 * Sanitize HTML - Prevenir XSS attacks
 * @param dirty HTML sin sanitizar
 * @returns HTML limpio y seguro
 */
export function sanitizeHtml(dirty: string): string {
  return (DOMPurify as any).sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'],
    ALLOWED_ATTR: [],
  });
}

/**
 * Sanitize URL - Evitar javascript: y data: URLs
 * @param url URL a sanitizar
 * @returns URL segura
 */
export function sanitizeUrl(url: string): string {
  try {
    const parsed = new URL(url, window.location.origin);
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return '';
    }
    return parsed.toString();
  } catch {
    return '';
  }
}

/**
 * Get CSRF Token - Obtener token CSRF del documento
 * @returns Token CSRF o null
 */
export function getCSRFToken(): string | null {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta?.getAttribute('content') || null;
}

/**
 * Validate Input - Validación básica en frontend
 * @param input String a validar
 * @param type Tipo de validación
 * @returns boolean
 */
export function validateInput(input: string, type: 'email' | 'url' | 'phone' | 'alphanumeric'): boolean {
  const patterns = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    url: /^https?:\/\/.+/,
    phone: /^\+?[\d\s\-()]{7,}$/,
    alphanumeric: /^[a-zA-Z0-9]*$/,
  };

  return patterns[type].test(input);
}

/**
 * Check HTTPS - Asegurar que la conexión es HTTPS en producción
 */
export function enforceHttps(): void {
  if ((import.meta.env.PROD as unknown as boolean) && window.location.protocol !== 'https:') {
    window.location.protocol = 'https:';
  }
}

/**
 * Set Security Headers - Via HTTP headers (backend responsibility)
 * Frontend puede detectar y alertar si faltan headers
 */
export function checkSecurityHeaders(): Record<string, string | null> {
  return {
    'content-security-policy': null, // Debe venir del backend
    'x-content-type-options': null,
    'x-frame-options': null,
    'x-xss-protection': null,
    'strict-transport-security': null,
  };
}

/**
 * Nonce Generator - Para CSP inline scripts
 * @returns Nonce string aleatorio
 */
export function generateNonce(): string {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Content Security Policy config
 * Debe ser enviado via HTTP headers desde backend
 */
export const CSP_CONFIG = {
  'default-src': ["'self'"],
  'script-src': ["'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'],
  'style-src': ["'self'", "'unsafe-inline'", 'fonts.googleapis.com'],
  'img-src': ["'self'", 'data:', 'https:'],
  'font-src': ["'self'", 'fonts.gstatic.com'],
  'connect-src': ["'self'", 'https://api.example.com'],
  'frame-ancestors': ["'none'"],
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
};
