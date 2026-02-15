# 🚀 PLAN TOTAL 1000%: DE CERO A ENTERPRISE PRODUCTION
**Objetivo:** Transformar proyecto de "funcional" a "PRODUCTION-GRADE ENTERPRISE"

**NO es 100%, es DESDE 0% HASTA 1000%** - Todo sanitizado, optimizado, seguro, testeable, monitoreable.

---

## 📋 ÍNDICE EJECUTIVO

**10 FASES - 70+ HORAS**

| Fase | Objetivo | Horas | Stack |
|------|----------|-------|-------|
| 1 | SASS ULTRA-COMPLETO | 8h | SCSS 7-1, BEM, CSS vars, animations |
| 2 | FRONT SECURITY TOTAL | 6h | CSP, XSS, CSRF, JWT, MFA |
| 3 | BACK SECURITY TOTAL | 8h | SQL injection, rate limit, audit logs |
| 4 | TYPESCRIPT OBLIGATORIO | 12h | Types, interfaces, generics, strict |
| 5 | TESTING EXHAUSTIVO | 14h | Unit 90%, E2E total, integration, perf |
| 6 | BACKEND SANITIZACIÓN | 8h | Input validation, PII encryption, logs |
| 7 | PERFORMANCE 1000% | 8h | Bundles, images, lazy loading, caching |
| 8 | OBSERVABILIDAD TOTAL | 6h | Logs, metrics, tracing, alerting |
| 9 | CI/CD ENTERPRISE | 6h | Pipelines, automation, deployments |
| 10 | DOCUMENTACIÓN 1000% | 4h | README, APIs, ADRs, guides |
| **TOTAL** | | **70h** | **PRODUCTION-READY** |

---

## ⚠️ CRITERIOS DE COMPLETITUD "1000%"

### Front-end:
- ✅ 0% inline CSS (100% SCSS)
- ✅ 100% BEM nomenclatura
- ✅ 100% type safety (TypeScript strict)
- ✅ 90%+ test coverage
- ✅ WCAG 2.1 AA accessibility
- ✅ Lighthouse >95 todos scoreboards
- ✅ Cero console.logs en producción
- ✅ Cero secrets en código
- ✅ 100% CSP compliance
- ✅ XSS-proof + CSRF tokens

### Back-end:
- ✅ 100% input validation + sanitization
- ✅ 0% SQL injection vulnerability
- ✅ 100% parameterized queries
- ✅ Password hashing (bcrypt salted)
- ✅ Audit trail para operaciones críticas
- ✅ Rate limiting (IP + user-based)
- ✅ Error handling sin stack traces
- ✅ PII encryption at rest
- ✅ Database transactions ACID
- ✅ 100% API documentation

### DevOps:
- ✅ 100% CI/CD pipeline
- ✅ SAST + DAST automatic scanning
- ✅ Dependency vulnerability checks
- ✅ Blue-green deployments
- ✅ Automatic rollback on failure
- ✅ Health checks endpoints
- ✅ Uptime monitoring 99.9%
- ✅ Centralized logging (ELK/DataDog)
- ✅ Distributed tracing
- ✅ Alerting system

---

## FASE 1: SASS ULTRA-COMPLETO 🎨
**8 horas | 🔴 CRÍTICA**

### 1.1 Estructura 7-1 Perfecta

```
src/scss/
├── abstracts/
│   ├── _variables.scss       # Colores, spacing, tipografía, breakpoints
│   ├── _functions.scss       # calc-valued functions, color manipulation
│   ├── _mixins.scss          # Media queries, vendor prefixes, patterns
│   └── _placeholders.scss    # %extends reutilizables
├── base/
│   ├── _normalize.scss       # Reset CSS
│   ├── _typography.scss      # Estilos base h1-h6, p, etc
│   └── _utilities-reset.scss # Box-sizing, etc
├── layout/
│   ├── _header.scss
│   ├── _footer.scss
│   ├── _sections.scss
│   ├── _sidebar.scss
│   └── _grid.scss
├── components/               # ⭐ NUEVA - COMPLETAMENTE POBLADA
│   ├── _buttons.scss
│   ├── _forms.scss
│   ├── _cards.scss
│   ├── _badges.scss
│   ├── _modals.scss
│   ├── _progress.scss
│   ├── _alerts.scss
│   ├── _tabs.scss
│   ├── _dropdowns.scss
│   ├── _pagination.scss
│   ├── _tooltips.scss
│   └── _spinners.scss
├── pages/
│   ├── _admin.scss
│   ├── _repairs.scss
│   └── _diagnostics.scss
├── themes/
│   ├── _light.scss
│   ├── _dark.scss
│   └── _variables-theme.scss
├── utilities/                # ⭐ NUEVA - COMPLETAMENTE POBLADA
│   ├── _spacing.scss
│   ├── _display.scss
│   ├── _visibility.scss
│   ├── _text.scss
│   ├── _flexbox.scss
│   ├── _grid.scss
│   ├── _responsive.scss
│   ├── _colors.scss
│   ├── _sizing.scss
│   ├── _positioning.scss
│   ├── _z-index.scss
│   ├── _overflow.scss
│   ├── _borders.scss
│   ├── _shadows.scss
│   ├── _opacity.scss
│   ├── _transitions.scss
│   ├── _transforms.scss
│   ├── _cursor.scss
│   └── _accessibility.scss
└── main.scss               # Entry point con imports ordenado
```

### 1.2 Variables por FUNCIÓN (no descripción)

```scss
// ✅ CORRECTO - Por función
$color-primary: #007bff;        // Para acciones principales
$color-secondary: #6c757d;      // Para acciones secundarias
$color-success: #28a745;        // Para éxito/positivo
$color-danger: #dc3545;         // Para error/peligro
$color-warning: #ffc107;        // Para advertencias
$color-info: #17a2b8;           // Para información

$spacing-xs: 0.25rem;           // Para micro espacios
$spacing-sm: 0.5rem;            // Para espacios pequeños
$spacing-md: 1rem;              // Espaciado base
$spacing-lg: 1.5rem;            // Espacios grandes
$spacing-xl: 2rem;              // Espacios muy grandes

$breakpoint-sm: 576px;          // Small devices
$breakpoint-md: 768px;          // Medium devices
$breakpoint-lg: 992px;          // Large devices
$breakpoint-xl: 1200px;         // Extra large devices

// ❌ INCORRECTO - Por descripción
$small-padding: 0.5rem;         // Confuso
$blue-color: #007bff;           // Redundante
```

### 1.3 BEM Nomenclatura 100% Consistente

```scss
// Estructura BEM: .block__element--modifier

.repair-card {                   // Block
  &__header {                    // Element
    padding: $spacing-md;
  }

  &__title {                     // Element
    font-size: $font-size-lg;
    font-weight: 600;
  }

  &__body {                      // Element
    padding: $spacing-md;
  }

  &__status {                    // Element
    display: inline-block;
    padding: $spacing-xs $spacing-sm;
    border-radius: $border-radius-sm;
  }

  // Modifiers - Variantes del bloque
  &--completed {                 // Modifier
    .repair-card__status {
      background-color: $color-success;
      color: white;
    }
  }

  &--urgent {                    // Modifier
    border-left: 4px solid $color-danger;
    background-color: rgba($color-danger, 0.05);
  }

  &--compact {                   // Modifier
    .repair-card__header,
    .repair-card__body {
      padding: $spacing-sm;
    }
  }

  // Estados
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  &:focus {
    outline: 2px solid $color-primary;
    outline-offset: 2px;
  }
}

// PSEUDO-ELEMENTOS - Evitar anidación profunda
.repair-card__badge {
  &::before {
    content: '●';
    margin-right: $spacing-xs;
  }
}
```

### 1.4 CSS Custom Properties para Dinámicos

```scss
// Variables CSS para valores que cambian en runtime

:root {
  --color-primary: #{$color-primary};
  --color-secondary: #{$color-secondary};
  --spacing-base: #{$spacing-md};
  --transition-speed: #{$transition-speed};
}

// Tema oscuro
@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: #4a9eff;
    --color-secondary: #9ca3af;
    --bg-primary: #1f2937;
    --text-primary: #f3f4f6;
  }
}

// Uso en componentes
.dynamic-component {
  background-color: var(--color-primary);
  padding: var(--spacing-base);
  transition-duration: var(--transition-speed);
}
```

### 1.5 Mixins Profesionales

```scss
// Mixins - DRY + reutilizable

// Media queries
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (min-width: $breakpoint-sm) { @content; }
  }
  @else if $breakpoint == 'md' {
    @media (min-width: $breakpoint-md) { @content; }
  }
  @else if $breakpoint == 'lg' {
    @media (min-width: $breakpoint-lg) { @content; }
  }
}

// Flexbox centering
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

// Truncate text
@mixin truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// Accessibility focus
@mixin focus-visible {
  &:focus-visible {
    outline: 2px solid $color-focus;
    outline-offset: 2px;
  }
}

// Gradientes
@mixin gradient($from, $to, $direction: 135deg) {
  background: linear-gradient($direction, $from, $to);
}

// Box shadow con escala
@mixin elevation($level: 1) {
  @if $level == 1 {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
  }
  @else if $level == 2 {
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
  }
  @else if $level == 3 {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23);
  }
}

// Animations
@mixin animate($name, $duration: 0.3s, $timing: ease-in-out) {
  animation: $name $duration $timing;
}

// Uso:
.button {
  @include flex-center;
  @include focus-visible;
  @include elevation(1);

  &:hover {
    @include elevation(2);
  }

  @include respond-to('md') {
    padding: $spacing-lg $spacing-xl;
  }
}
```

### 1.6 Animations & Transitions

```scss
// Animations profesionales - Performance optimizado

// Smooth fade-in
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

// Slide from left
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

// Scale up with bounce
@keyframes scaleInUp {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

// Loading spinner
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// Pulse effect
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

// Shimmer (skeleton loading)
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

// Variables de transición reutilizables
$transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
$transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
$transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);

// Uso
.button {
  transition: all $transition-normal;

  &:hover {
    @include animate(scaleInUp, 300ms);
  }
}

.loading-skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}
```

### 1.7 Accessibility WCAG 2.1 AA

```scss
// Accesibilidad integrada en SCSS

// Focus states visibles para teclado
input:focus-visible,
button:focus-visible,
a:focus-visible {
  outline: 2px solid $color-focus;
  outline-offset: 2px;
}

// High contrast mode
@media (prefers-contrast: more) {
  $color-primary: darken($color-primary, 20%);
  $color-text: #000;
  $color-border: #000;
}

// Respect motion preferences
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

// Screen reader only text
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

// High enough contrast for text
.text-primary {
  color: #0052cc;        // 7.5:1 contrast ratio con white bg
  font-weight: 500;      // Aumenta legibilidad
}

// Visible skip links
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: $color-primary;
  color: white;
  padding: $spacing-md;
  text-decoration: none;
  z-index: 100;

  &:focus {
    top: 0;
  }
}

// Focus indicators para iconos
.icon-button {
  &:focus-within {
    background-color: rgba($color-primary, 0.1);
  }
}
```

### 1.8 NO CSS INLINE - Todo en SCSS

**ANTES (❌ PROHIBIDO):**
```html
<div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px;">
  Content
</div>
```

**DESPUÉS (✅ CORRECTO):**
```html
<div class="u-bg-light u-p-lg u-rounded-md">
  Content
</div>
```

```scss
.u-bg-light { background-color: $color-light; }
.u-p-lg { padding: $spacing-lg; }
.u-rounded-md { border-radius: $border-radius-md; }
```

---

## FASE 2: FRONT SECURITY TOTAL 🔐
**6 horas | 🔴 CRÍTICA**

### 2.1 Content Security Policy (CSP)

```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'nonce-{RANDOM_NONCE}' https://cdn.jsdelivr.net;
  style-src 'self' 'nonce-{RANDOM_NONCE}' https://fonts.googleapis.com;
  img-src 'self' data: https:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.cirujano.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self'
">
```

### 2.2 XSS Prevention - Sanitize Input

```typescript
// src/utils/security.ts

import DOMPurify from 'dompurify';

export class XSSProtection {
  /**
   * Sanitiza contenido HTML para prevenir XSS
   * @param dirty - HTML potencialmente peligroso
   * @returns HTML seguro
   */
  static sanitizeHTML(dirty: string): string {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
      ALLOWED_ATTR: ['href', 'title', 'target'],
      ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
    });
  }

  /**
   * Escapa caracteres especiales para HTML
   * @param text - Texto a escapar
   * @returns Texto escapado
   */
  static escapeHTML(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Valida URLs antes de usar en href
   * @param url - URL a validar
   * @returns true si es segura
   */
  static isSafeURL(url: string): boolean {
    try {
      const u = new URL(url);
      return ['http:', 'https:'].includes(u.protocol);
    } catch {
      return false;
    }
  }

  /**
   * Previene ataques de inyección en atributos
   * @param attr - Valor de atributo
   * @returns Valor seguro
   */
  static sanitizeAttribute(attr: string): string {
    return attr
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
}

// Uso en Vue
<template>
  <div v-html="XSSProtection.sanitizeHTML(userContent)"></div>
  <a :href="XSSProtection.isSafeURL(link) ? link : '#'">Link</a>
</template>
```

### 2.3 CSRF Token Protection

```typescript
// src/services/csrf.ts

export class CSRFProtection {
  private static readonly TOKEN_KEY = 'csrf-token';
  private static readonly HEADER_NAME = 'X-CSRF-Token';

  /**
   * Obtiene o genera un CSRF token
   */
  static getToken(): string {
    let token = sessionStorage.getItem(this.TOKEN_KEY);
    
    if (!token) {
      token = this.generateToken();
      sessionStorage.setItem(this.TOKEN_KEY, token);
    }
    
    return token;
  }

  /**
   * Genera un token criptográficamente seguro
   */
  private static generateToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Añade CSRF token a headers de peticiones
   */
  static getHeaders(): Record<string, string> {
    return {
      [this.HEADER_NAME]: this.getToken(),
    };
  }
}

// Uso en Axios
import axios from 'axios';
import { CSRFProtection } from '@/services/csrf';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Añadir CSRF token a todas las peticiones (excepto GET)
api.interceptors.request.use(config => {
  if (['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase() || '')) {
    config.headers = {
      ...config.headers,
      ...CSRFProtection.getHeaders(),
    };
  }
  return config;
});
```

### 2.4 JWT Token Management Seguro

```typescript
// src/services/auth.ts

interface TokenResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export class AuthService {
  private static readonly ACCESS_TOKEN_KEY = 'access_token_encrypted';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token_encrypted';
  private static readonly TOKEN_EXPIRY_KEY = 'token_expiry';

  /**
   * Almacena tokens de forma segura (en memory + sessionStorage)
   */
  static async storeTokens(response: TokenResponse): Promise<void> {
    // NO usar localStorage para tokens (XSS vulnerability)
    // Usar sessionStorage + in-memory para mayor seguridad
    
    // Validar tokens antes de almacenar
    if (!this.isValidJWT(response.accessToken)) {
      throw new Error('Invalid JWT token');
    }

    // Almacenar encriptado en sessionStorage (si es obligatorio)
    const encrypted = await this.encryptToken(response.accessToken);
    sessionStorage.setItem(this.ACCESS_TOKEN_KEY, encrypted);

    // Almacenar refresh token en sessionStorage (con expiración)
    const refreshEncrypted = await this.encryptToken(response.refreshToken);
    sessionStorage.setItem(this.REFRESH_TOKEN_KEY, refreshEncrypted);

    // Guardar expiry time
    const expiryTime = Date.now() + response.expiresIn * 1000;
    sessionStorage.setItem(this.TOKEN_EXPIRY_KEY, expiryTime.toString());
  }

  /**
   * Obtiene access token actual
   */
  static async getAccessToken(): Promise<string | null> {
    const encrypted = sessionStorage.getItem(this.ACCESS_TOKEN_KEY);
    if (!encrypted) return null;

    try {
      const token = await this.decryptToken(encrypted);
      
      // Verificar si token expiró
      if (this.isTokenExpired()) {
        await this.refreshAccessToken();
        return this.getAccessToken();
      }

      return token;
    } catch (error) {
      console.error('Error retrieving token:', error);
      this.clearTokens();
      return null;
    }
  }

  /**
   * Valida estructura JWT
   */
  private static isValidJWT(token: string): boolean {
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      const payload = JSON.parse(atob(parts[1]));
      return payload.exp && payload.sub;
    } catch {
      return false;
    }
  }

  /**
   * Verifica si token expiró
   */
  private static isTokenExpired(): boolean {
    const expiry = sessionStorage.getItem(this.TOKEN_EXPIRY_KEY);
    if (!expiry) return true;
    return Date.now() > parseInt(expiry);
  }

  /**
   * Encripta token (opcional, para extra security)
   */
  private static async encryptToken(token: string): Promise<string> {
    // Implementar con TweetNaCl o libsodium
    // Por ahora, retornar base64
    return btoa(token);
  }

  /**
   * Desencripta token
   */
  private static async decryptToken(encrypted: string): Promise<string> {
    return atob(encrypted);
  }

  /**
   * Refresca access token
   */
  private static async refreshAccessToken(): Promise<void> {
    const refreshToken = sessionStorage.getItem(this.REFRESH_TOKEN_KEY);
    if (!refreshToken) throw new Error('No refresh token');

    try {
      const response = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refreshToken: await this.decryptToken(refreshToken) }),
      });

      if (!response.ok) throw new Error('Refresh failed');

      const data = await response.json();
      await this.storeTokens(data);
    } catch (error) {
      this.clearTokens();
      throw error;
    }
  }

  /**
   * Limpia tokens
   */
  static clearTokens(): void {
    sessionStorage.removeItem(this.ACCESS_TOKEN_KEY);
    sessionStorage.removeItem(this.REFRESH_TOKEN_KEY);
    sessionStorage.removeItem(this.TOKEN_EXPIRY_KEY);
  }
}
```

### 2.5 Secure Form Handling

```typescript
// src/composables/useSecureForm.ts

import { ref, reactive, computed } from 'vue';
import { XSSProtection } from '@/utils/security';
import { CSRFProtection } from '@/services/csrf';

export function useSecureForm<T extends Record<string, any>>(initialState: T) {
  const formData = reactive<T>({ ...initialState });
  const errors = ref<Record<string, string>>({});
  const isSubmitting = ref(false);

  /**
   * Valida y sanitiza un campo
   */
  const sanitizeField = (key: keyof T, value: any): any => {
    if (typeof value === 'string') {
      // XSS prevention
      return XSSProtection.sanitizeHTML(value);
    }
    if (Array.isArray(value)) {
      return value.map(v => sanitizeField(key, v));
    }
    return value;
  };

  /**
   * Maneja cambios de campo
   */
  const updateField = (key: keyof T, value: any) => {
    const sanitized = sanitizeField(key, value);
    formData[key] = sanitized;
    errors.value[key as string] = '';
  };

  /**
   * Valida formulario antes de enviar
   */
  const validate = (rules: Record<string, (value: any) => boolean | string>): boolean => {
    const newErrors: Record<string, string> = {};

    Object.entries(rules).forEach(([field, rule]) => {
      const result = rule(formData[field as keyof T]);
      if (typeof result === 'string') {
        newErrors[field] = result;
      }
    });

    errors.value = newErrors;
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Envía formulario de forma segura
   */
  const submit = async (
    onSubmit: (data: T) => Promise<void>,
    rules?: Record<string, (value: any) => boolean | string>
  ): Promise<void> => {
    if (!validate(rules || {})) return;

    isSubmitting.value = true;
    try {
      // Añadir CSRF token
      const dataWithCSRF = {
        ...formData,
        _csrf: CSRFProtection.getToken(),
      };

      await onSubmit(dataWithCSRF);
    } finally {
      isSubmitting.value = false;
    }
  };

  return {
    formData,
    errors,
    isSubmitting,
    updateField,
    submit,
    validate,
  };
}
```

---

## FASE 3: BACKEND SECURITY TOTAL 🔐
**8 horas | 🔴 CRÍTICA**

### 3.1 Input Validation + Sanitization

```python
# backend/app/schemas.py
from pydantic import BaseModel, validator, EmailStr, Field
import re

class RepairCreate(BaseModel):
    """Schema para crear reparación con validación stricta"""
    
    patient_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    diagnosis: str = Field(..., min_length=5, max_length=1000)
    symptoms: list[str] = Field(..., min_items=1, max_items=10)
    notes: str | None = Field(None, max_length=5000)

    @validator('patient_name')
    def sanitize_patient_name(cls, v):
        """Sanitiza nombre del paciente"""
        # Remover caracteres especiales
        sanitized = re.sub(r'[<>\"\'();]', '', v)
        # Validar que sea solo letras y espacios
        if not re.match(r'^[a-záéíóúñA-ZÁÉÍÓÚÑ\s]+$', sanitized):
            raise ValueError('Invalid patient name')
        return sanitized.strip()

    @validator('diagnosis')
    def sanitize_diagnosis(cls, v):
        """Previene inyección SQL en diagnosis"""
        # Validar contra patrones SQL
        sql_patterns = [
            r'(\bDROP\b|\bDELETE\b|\bINSERT\b)',
            r'(--|#|/\*)',
            r"(\bOR\b.*=.*|\bAND\b.*=.*)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Suspicious input detected')
        
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        """Valida email"""
        # Verificar que no sea honeypot (campo oculto)
        if 'mailto:' in v.lower():
            raise ValueError('Invalid email format')
        return v.lower()

    class Config:
        extra = 'forbid'  # Rechazar campos no declarados

class Config:
    schema_extra = {
        "example": {
            "patient_name": "Juan Pérez",
            "email": "juan@example.com",
            "diagnosis": "Fractura de tibia",
            "symptoms": ["dolor", "inflamación"],
            "notes": "Paciente muy estable"
        }
    }
```

### 3.2 Password Hashing + Auth

```python
# backend/app/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os

# Configuración de hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Factor de trabajo alto para seguridad
)

class SecurityConfig:
    # JWT
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Passwordos
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True

def hash_password(password: str) -> str:
    """Hashea password con bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Valida fortaleza del password"""
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        return False, f"Password debe tener mínimo {SecurityConfig.MIN_PASSWORD_LENGTH} caracteres"
    
    if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password debe incluir mayúsculas"
    
    if SecurityConfig.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
        return False, "Password debe incluir números"
    
    if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*" for c in password):
        return False, "Password debe incluir caracteres especiales (!@#$%^&*)"
    
    # Verificar que no sea común
    common_passwords = ['password123', 'admin123', '123456', 'qwerty']
    if password.lower() in common_passwords:
        return False, "Password demasiado común, elige otro"
    
    return True, ""

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Crea JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SecurityConfig.SECRET_KEY,
        algorithm=SecurityConfig.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verifica JWT token"""
    try:
        payload = jwt.decode(
            token,
            SecurityConfig.SECRET_KEY,
            algorithms=[SecurityConfig.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido")
```

### 3.3 Rate Limiting

```python
# backend/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.rules = {
            "/api/auth/login": (5, 60),          # 5 intentos por minuto
            "/api/auth/register": (3, 3600),     # 3 registros por hora
            "/api/repairs": (100, 60),           # 100 requests por minuto
            "/api/search": (30, 60),             # 30 búsquedas por minuto
        }

    async def check_rate_limit(self, request: Request) -> bool:
        """Verifica si cliente excedió rate limit"""
        # Obtener identificador (IP o user ID)
        client_id = request.client.host
        if hasattr(request.state, 'user_id'):
            client_id = f"user_{request.state.user_id}"

        # Obtener regla
        path = request.url.path
        if path not in self.rules:
            return True  # Sin límite

        max_requests, window_seconds = self.rules[path]
        
        # Limpiar requests antiguos
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]

        # Verificar si excedió límite
        if len(self.requests[client_id]) >= max_requests:
            return False

        # Registrar nuevo request
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter()

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if not await rate_limiter.check_rate_limit(request):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Try again later.",
            headers={"Retry-After": "60"}
        )
    return await call_next(request)
```

### 3.4 Audit Logging

```python
# backend/app/models/audit_log.py
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
import json

class AuditLog(Base):
    """Registro de auditoría para operaciones críticas"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE'
    entity_type = Column(String(100), nullable=False)  # 'repair', 'user', etc
    entity_id = Column(Integer, nullable=False)
    old_values = Column(JSON, nullable=True)  # Antes de cambio
    new_values = Column(JSON, nullable=True)  # Después de cambio
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='success')  # 'success', 'failure'

    class Config:
        tablename = 'audit_logs'

# Servicio de auditoría
class AuditService:
    @staticmethod
    async def log_action(
        db: Session,
        user_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: dict | None,
        new_values: dict | None,
        request: Request,
        status: str = 'success'
    ):
        """Registra acción en audit log"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.client.host,
            user_agent=request.headers.get('user-agent'),
            status=status
        )
        db.add(audit_log)
        await db.commit()

# Uso en endpoints
@router.post("/repairs")
async def create_repair(
    repair_data: RepairCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request
):
    try:
        repair = Repair(**repair_data.dict())
        db.add(repair)
        db.commit()

        # Log auditoría
        await AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action='CREATE',
            entity_type='repair',
            entity_id=repair.id,
            old_values=None,
            new_values=repair_data.dict(),
            request=request
        )

        return repair
    except Exception as e:
        await AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action='CREATE',
            entity_type='repair',
            entity_id=0,
            old_values=None,
            new_values=repair_data.dict(),
            request=request,
            status='failure'
        )
        raise
```

### 3.5 PII Encryption at Rest

```python
# backend/app/utils/encryption.py
from cryptography.fernet import Fernet
import os

class PIIEncryption:
    """Encripta datos personales (PII) en base de datos"""
    
    @staticmethod
    def get_cipher():
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")
        return Fernet(key.encode())

    @staticmethod
    def encrypt(value: str) -> str:
        """Encripta valor"""
        if not value:
            return value
        cipher = PIIEncryption.get_cipher()
        return cipher.encrypt(value.encode()).decode()

    @staticmethod
    def decrypt(encrypted_value: str) -> str:
        """Desencripta valor"""
        if not encrypted_value:
            return encrypted_value
        cipher = PIIEncryption.get_cipher()
        return cipher.decrypt(encrypted_value.encode()).decode()

# Uso en modelo SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    _phone = Column("phone", String(500))  # Encriptado en DB
    _ssn = Column("ssn", String(500))      # Encriptado en DB

    @property
    def phone(self):
        """Desencripta al acceder"""
        if self._phone:
            return PIIEncryption.decrypt(self._phone)
        return None

    @phone.setter
    def phone(self, value):
        """Encripta al asignar"""
        self._phone = PIIEncryption.encrypt(value) if value else None

    @property
    def ssn(self):
        return PIIEncryption.decrypt(self._ssn) if self._ssn else None

    @ssn.setter
    def ssn(self, value):
        self._ssn = PIIEncryption.encrypt(value) if value else None

# Evento para encriptar al guardar
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def encrypt_pii(mapper, connection, target):
    """Asegura que PII esté encriptado antes de guardar"""
    if target.phone and not target._phone.startswith('gAAAAAA'):
        target._phone = PIIEncryption.encrypt(target.phone)
```

---

## FASE 4: TYPESCRIPT TOTAL 🔤
**12 horas | 🟡 ALTA**

### 4.1 Configuración Strict

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "jsxImportSource": "vue",

    // Strict type checking
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,

    // Additional checks
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    // Module resolution
    "moduleResolution": "node",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,

    // Declaration files
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    // Output
    "outDir": "./dist",
    "rootDir": "./src",

    // Path mapping
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/vue/components/*"],
      "@stores/*": ["src/stores/*"],
      "@composables/*": ["src/composables/*"],
      "@services/*": ["src/services/*"],
      "@utils/*": ["src/utils/*"],
      "@types/*": ["src/types/*"],
      "@scss/*": ["src/scss/*"]
    }
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 4.2 Type Definitions para APIs

```typescript
// src/types/api.ts

/**
 * Respuesta genérica de API
 */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string>;
  timestamp: string;
  requestId: string;
}

/**
 * Entidad Reparación
 */
export interface Repair {
  id: number;
  patientName: string;
  email: string;
  diagnosis: string;
  symptoms: string[];
  notes: string | null;
  status: RepairStatus;
  createdAt: Date;
  updatedAt: Date;
  createdBy: number;
}

export enum RepairStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

/**
 * Request para crear reparación
 */
export interface CreateRepairRequest {
  patientName: string;
  email: string;
  diagnosis: string;
  symptoms: string[];
  notes?: string;
}

/**
 * Respuesta de autenticación
 */
export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
  expiresIn: number;
}

/**
 * Entidad Usuario
 */
export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  createdAt: Date;
}

export enum UserRole {
  ADMIN = 'admin',
  TECHNICIAN = 'technician',
  USER = 'user',
}

/**
 * Paginación
 */
export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  pageSize: number;
  total: number;
  hasMore: boolean;
}

/**
 * Filtros de búsqueda
 */
export interface RepairFilters {
  status?: RepairStatus;
  patientName?: string;
  startDate?: Date;
  endDate?: Date;
  page?: number;
  pageSize?: number;
  sortBy?: 'createdAt' | 'updatedAt' | 'patientName';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Errores de API
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  statusCode: number;
}
```

### 4.3 Type-Safe Composables

```typescript
// src/composables/useApi.ts
import { ref, readonly } from 'vue';
import axios, { AxiosError } from 'axios';
import type { ApiResponse, ApiError } from '@/types/api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

export function useApi<T>(baseURL: string = import.meta.env.VITE_API_URL) {
  const state = ref<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  /**
   * Realiza petición GET type-safe
   */
  async function get<R = T>(endpoint: string, config?: any): Promise<R> {
    state.value.loading = true;
    state.value.error = null;

    try {
      const response = await axios.get<ApiResponse<R>>(
        `${baseURL}${endpoint}`,
        config
      );

      if (response.data.success) {
        state.value.data = response.data.data as any;
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Request failed');
      }
    } catch (error) {
      const apiError = handleApiError(error);
      state.value.error = apiError;
      throw apiError;
    } finally {
      state.value.loading = false;
    }
  }

  /**
   * Realiza petición POST type-safe
   */
  async function post<R = T>(endpoint: string, data: any, config?: any): Promise<R> {
    state.value.loading = true;
    state.value.error = null;

    try {
      const response = await axios.post<ApiResponse<R>>(
        `${baseURL}${endpoint}`,
        data,
        config
      );

      if (response.data.success) {
        state.value.data = response.data.data as any;
        return response.data.data;
      } else {
        throw new Error(response.data.message || 'Request failed');
      }
    } catch (error) {
      const apiError = handleApiError(error);
      state.value.error = apiError;
      throw apiError;
    } finally {
      state.value.loading = false;
    }
  }

  /**
   * Maneja errores de API
   */
  function handleApiError(error: unknown): ApiError {
    if (axios.isAxiosError(error)) {
      const response = error.response;
      return {
        code: response?.data?.code || 'UNKNOWN_ERROR',
        message: response?.data?.message || error.message,
        details: response?.data?.errors,
        statusCode: response?.status || 0,
      };
    }

    return {
      code: 'UNKNOWN_ERROR',
      message: error instanceof Error ? error.message : 'Unknown error',
      statusCode: 0,
    };
  }

  return {
    state: readonly(state),
    get,
    post,
  };
}

// Uso
const { state, get } = useApi<Repair>('/api');
const repairs = await get('/repairs');
```

---

## FASE 5: TESTING EXHAUSTIVO 🧪
**14 horas | 🟡 ALTA**

### 5.1 Unit Tests - 90%+ Coverage

```typescript
// src/stores/__tests__/repairs.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useRepairsStore } from '../repairs';
import * as api from '@/services/api';

vi.mock('@/services/api');

describe('Repairs Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  describe('Fetching repairs', () => {
    it('should fetch repairs successfully', async () => {
      const mockRepairs = [
        {
          id: 1,
          patientName: 'Juan',
          diagnosis: 'Fractura',
          status: 'completed',
        },
      ];

      vi.mocked(api.getRepairs).mockResolvedValue(mockRepairs);

      const store = useRepairsStore();
      await store.fetchRepairs();

      expect(store.repairs).toEqual(mockRepairs);
      expect(store.loading).toBe(false);
    });

    it('should handle fetch error gracefully', async () => {
      const error = new Error('API Error');
      vi.mocked(api.getRepairs).mockRejectedValue(error);

      const store = useRepairsStore();
      await store.fetchRepairs();

      expect(store.error).toBe('Failed to fetch repairs');
      expect(store.repairs).toEqual([]);
    });
  });

  describe('Creating repair', () => {
    it('should create repair with validation', async () => {
      const newRepair = {
        patientName: 'María',
        email: 'maria@example.com',
        diagnosis: 'Esguince',
        symptoms: ['dolor', 'inflamación'],
      };

      vi.mocked(api.createRepair).mockResolvedValue({
        id: 2,
        ...newRepair,
        status: 'pending',
      });

      const store = useRepairsStore();
      const created = await store.createRepair(newRepair);

      expect(created).toBeDefined();
      expect(created.id).toBe(2);
    });

    it('should reject invalid input', async () => {
      const store = useRepairsStore();
      
      const invalid = {
        patientName: '',  // Empty
        email: 'invalid',
        diagnosis: 'short',
      };

      await expect(store.createRepair(invalid)).rejects.toThrow();
    });
  });
});
```

### 5.2 E2E Tests - Cypress

```typescript
// cypress/e2e/repair-workflow.cy.ts
describe('Complete Repair Workflow', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.login('admin@test.com', 'Admin123!@#')
  })

  it('should complete full repair lifecycle', () => {
    // 1. Crear reparación
    cy.visit('/admin/repairs')
    cy.get('[data-testid="btn-new-repair"]').click()
    
    cy.get('[data-testid="form-patient"]').type('Test Patient')
    cy.get('[data-testid="form-email"]').type('patient@test.com')
    cy.get('[data-testid="form-diagnosis"]').select('Fractura')
    cy.get('[data-testid="form-symptoms"]').should('have.length.gte', 1)
    cy.get('[data-testid="form-submit"]').click()

    cy.get('.alert--success').should('contain', 'Reparación creada')

    // 2. Editar reparación
    cy.get('[data-testid="repair-row"]').first().click()
    cy.get('[data-testid="form-status"]').select('in_progress')
    cy.get('[data-testid="form-notes"]').type('Started treatment')
    cy.get('[data-testid="form-submit"]').click()

    cy.get('.alert--success').should('be.visible')

    // 3. Completar reparación
    cy.get('[data-testid="repair-row"]').first().click()
    cy.get('[data-testid="form-status"]').select('completed')
    cy.get('[data-testid="form-submit"]').click()

    cy.get('.alert--success').should('be.visible')

    // 4. Verificar auditoría
    cy.get('[data-testid="audit-trail"]').should('contain', 'created')
    cy.get('[data-testid="audit-trail"]').should('contain', 'updated')
  })

  it('should validate required fields', () => {
    cy.visit('/admin/repairs')
    cy.get('[data-testid="btn-new-repair"]').click()
    
    // Intentar enviar sin datos
    cy.get('[data-testid="form-submit"]').click()

    cy.get('[data-testid="error-patient"]').should('be.visible')
    cy.get('[data-testid="error-email"]').should('be.visible')
  })
})
```

### 5.3 Performance Tests

```typescript
// tests/performance/lighthouse.spec.ts
import lighthouse from 'lighthouse';

describe('Performance - Lighthouse', () => {
  it('should pass Lighthouse audits', async () => {
    const options = {
      logLevel: 'info' as const,
      output: 'json',
      port: 9222,
    };

    const runnerResult = await lighthouse(
      'http://localhost:5173',
      options
    );

    const { lhr } = runnerResult;
    
    expect(lhr.categories.performance.score).toBeGreaterThanOrEqual(0.90);
    expect(lhr.categories.accessibility.score).toBeGreaterThanOrEqual(0.90);
    expect(lhr.categories['best-practices'].score).toBeGreaterThanOrEqual(0.90);
    expect(lhr.categories.seo.score).toBeGreaterThanOrEqual(0.90);
  }, 60000); // 60s timeout
});
```

---

## FASE 6: BACKEND SANITIZACIÓN 🧹
**8 horas | 🔴 CRÍTICA**

### 6.1 Validación completa de inputs

```python
# backend/app/validators.py
from typing import Any
import re

class InputValidator:
    """Validación exhaustiva de inputs"""
    
    # Patrones de inyección SQL
    SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT',
        'UNION', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE'
    ]
    
    @staticmethod
    def validate_string(value: str, field_name: str, min_len: int = 1, max_len: int = 255) -> str:
        """Valida string sin inyección"""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be string")
        
        value = value.strip()
        
        if len(value) < min_len:
            raise ValueError(f"{field_name} too short")
        
        if len(value) > max_len:
            raise ValueError(f"{field_name} too long")
        
        # Buscar patrones SQL
        for keyword in InputValidator.SQL_KEYWORDS:
            if keyword in value.upper() and '--' in value:
                raise ValueError(f"{field_name} contains suspicious patterns")
        
        # Remover caracteres problemáticos
        dangerous_chars = r'[<>"\'\;\\`*?]'
        if re.search(dangerous_chars, value):
            raise ValueError(f"{field_name} contains invalid characters")
        
        return value

    @staticmethod
    def validate_email(email: str) -> str:
        """Valida email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email.lower()

    @staticmethod
    def validate_integer(value: Any, field_name: str, min_val: int = None, max_val: int = None) -> int:
        """Valida integer"""
        try:
            num = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be integer")
        
        if min_val is not None and num < min_val:
            raise ValueError(f"{field_name} below minimum")
        
        if max_val is not None and num > max_val:
            raise ValueError(f"{field_name} above maximum")
        
        return num

    @staticmethod
    def validate_enum(value: str, field_name: str, allowed_values: list) -> str:
        """Valida enum"""
        if value not in allowed_values:
            raise ValueError(f"{field_name} invalid value")
        return value

    @staticmethod
    def sanitize_html(html: str) -> str:
        """Remueve HTML peligroso"""
        dangerous_tags = ['<script', '<iframe', '<embed', '<object']
        for tag in dangerous_tags:
            if tag in html.lower():
                raise ValueError("Contains dangerous HTML tags")
        
        # Remover atributos on*
        html = re.sub(r'\bon\w+\s*=', '', html, flags=re.IGNORECASE)
        return html

# Uso en endpoints
from fastapi import Request

@router.post("/repairs")
async def create_repair(
    repair_data: RepairCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    # Validar inputs
    try:
        patient_name = InputValidator.validate_string(
            repair_data.patientName,
            "patientName",
            min_len=2,
            max_len=255
        )
        
        email = InputValidator.validate_email(repair_data.email)
        
        diagnosis = InputValidator.validate_string(
            repair_data.diagnosis,
            "diagnosis",
            min_len=10,
            max_len=1000
        )
        
        status = InputValidator.validate_enum(
            repair_data.status,
            "status",
            ['pending', 'in_progress', 'completed']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Crear reparación
    repair = Repair(
        patient_name=patient_name,
        email=email,
        diagnosis=diagnosis,
        status=status
    )
    db.add(repair)
    db.commit()
    
    return repair
```

---

## FASE 7: PERFORMANCE AL 1000% 🚀
**8 horas | 🟡 ALTA**

### 7.1 Bundle Analysis & Optimization

```bash
# package.json scripts
{
  "scripts": {
    "build": "vite build",
    "analyze": "vite build --analyze",
    "preview": "vite preview",
    "lighthouse": "lighthouse http://localhost:5173"
  }
}
```

### 7.2 Vite Config Optimized

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import compression from 'vite-plugin-compression'
import legacy from '@vitejs/plugin-legacy'
import visualizer from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    vue(),
    
    // Compresión Brotli
    compression({
      algorithm: 'brotli',
      threshold: 10240,
      deleteOriginFile: false,
    }),

    // Visualizador de bundle
    visualizer({
      filename: 'dist/bundle-stats.html',
    }),

    // Legacy support
    legacy({
      targets: ['defaults', 'not IE 11']
    })
  ],

  build: {
    target: 'ES2020',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        // Code splitting strategy
        manualChunks: {
          'vue': ['vue', 'vue-router', 'pinia'],
          'utils': ['axios', 'lodash-es'],
          'ui': ['bootstrap'],
        },
        // Filename patterns
        entryFileNames: 'js/[name]-[hash].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: ({ name }) => {
          if (/\.(gif|jpe?g|png|gif|webp|avif)$/.test(name ?? '')) {
            return 'images/[name]-[hash][extname]';
          } else if (/\.css$/.test(name ?? '')) {
            return 'css/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
    // Optimizaciones
    commonjsOptions: {
      include: /node_modules/,
      sourceMap: false,
    },
  },

  // Optimizaciones de servidor
  server: {
    middlewareMode: false,
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
    },
  },

  // Optimizaciones de dependencias
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
    exclude: ['@vite/client'],
  },
})
```

### 7.3 Image Optimization

```html
<!-- Imágenes optimizadas con múltiples formatos -->
<picture>
  <!-- AVIF - Mejor compresión -->
  <source srcset="/images/repair-[name].avif" type="image/avif">
  
  <!-- WebP - Compatible navegadores modernos -->
  <source srcset="/images/repair-[name].webp" type="image/webp">
  
  <!-- Fallback PNG -->
  <img 
    src="/images/repair-[name].png" 
    alt="Repair image"
    loading="lazy"
    width="800"
    height="600"
  >
</picture>
```

### 7.4 Caching Strategy

```javascript
// public/sw.js - Service Worker
const CACHE_NAME = 'cirujano-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/css/main.css',
  '/js/main.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) return response;

      return fetch(event.request).then((response) => {
        // Cachear respuestas de API (estrategia network-first)
        if (event.request.url.includes('/api/')) {
          const cache = caches.open(CACHE_NAME);
          cache.then((c) => c.put(event.request, response.clone()));
        }
        return response;
      });
    })
  );
});
```

---

## FASE 8: OBSERVABILIDAD TOTAL 🔍
**6 horas | 🟡 ALTA**

### 8.1 Logging Centralizado

```python
# backend/app/logging_config.py
import logging
import json
from pythonjsonlogger import jsonlogger
from datetime import datetime

class JSONFormatter(jsonlogger.JsonFormatter):
    """Formato JSON para logs"""
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

def setup_logging():
    """Configura logging con ELK/DataDog"""
    logger = logging.getLogger('cirujano')
    logger.setLevel(logging.DEBUG)

    # Console handler (JSON)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # File handler (para persistencia local)
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()

# Uso
logger.info('Repair created', extra={
    'user_id': user.id,
    'repair_id': repair.id,
    'patient_name': repair.patient_name,
})
```

### 8.2 Sentry Error Tracking

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=1.0,
    attach_stacktrace=True,
)
```

---

## FASE 9: CI/CD ENTERPRISE 🔄
**6 horas | 🟡 ALTA**

### 9.1 GitHub Actions Completo

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - uses: actions/setup-node@v3
      with:
        node-version: '18'

    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    # Frontend tests
    - name: Install dependencies
      run: npm ci

    - name: Lint
      run: npm run lint

    - name: Format check
      run: npm run format:check

    - name: Unit tests
      run: npm run test:unit

    - name: E2E tests
      run: npm run test:e2e

    - name: Build
      run: npm run build

    # Backend tests
    - name: Setup Python
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Backend tests
      run: |
        cd backend
        pytest tests/

    - name: Security scan
      run: npm run security:scan

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Deploy to production
      run: |
        # Blue-green deployment
        kubectl set image deployment/cirujano \
          cirujano=${{ env.DOCKER_IMAGE }}:${{ github.sha }}
        kubectl rollout status deployment/cirujano

    - name: Health check
      run: |
        curl -f https://cirujano.com/health || exit 1

    - name: Notify Slack
      uses: slackapi/slack-github-action@v1
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK }}
        payload: |
          {
            "text": "Deployment successful",
            "blocks": [
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "✅ Cirujano deployed to production"
                }
              }
            ]
          }
```

---

## FASE 10: DOCUMENTACIÓN 1000% 📚
**4 horas | 🟡 MEDIA**

### 10.1 README Exhaustivo

```markdown
# Cirujano - Sistema de Gestión de Reparaciones Quirúrgicas

## 📋 Tabla de Contenidos
- [Instalación](#instalación)
- [Arquitectura](#arquitectura)
- [Desarrollo](#desarrollo)
- [Despliegue](#despliegue)
- [Seguridad](#seguridad)
- [Testing](#testing)
- [Monitoreo](#monitoreo)

## 🚀 Instalación

### Prerequisitos
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Docker + Docker Compose

### Setup Local

#### Frontend
```bash
cd cirujano-front
npm install
npm run dev
```

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

## 🏗️ Arquitectura

### Frontend (Vue 3 + TypeScript)
```
src/
├── components/       # Componentes Vue
├── composables/     # Lógica reutilizable
├── stores/          # Pinia state management
├── services/        # API clients
├── types/           # TypeScript definitions
├── scss/            # Estilos (7-1 pattern)
└── utils/           # Funciones utilitarias
```

### Backend (FastAPI + SQLAlchemy)
```
backend/
├── app/
│   ├── models/     # ORM models
│   ├── schemas/    # Pydantic schemas
│   ├── routes/     # API endpoints
│   ├── services/   # Business logic
│   ├── security/   # Auth + validation
│   └── middleware/ # Middleware custom
├── tests/          # Tests
└── alembic/        # Database migrations
```

## 🛡️ Seguridad

### Frontend
- ✅ CSP headers
- ✅ XSS prevention (DOMPurify)
- ✅ CSRF token protection
- ✅ Secure JWT storage
- ✅ Input validation

### Backend
- ✅ SQL injection prevention
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting
- ✅ Input sanitization
- ✅ Audit logging

## ✅ Testing

```bash
# Frontend
npm run test:unit           # Unit tests
npm run test:e2e           # E2E tests
npm run test:coverage      # Coverage report

# Backend
pytest                      # All tests
pytest --cov               # With coverage
```

## 📊 Monitoreo

- **Logs:** ELK Stack / DataDog
- **Errores:** Sentry
- **Performance:** Lighthouse / Web Vitals
- **Uptime:** Pingdom / Datadog
- **Métricas:** Prometheus + Grafana

---
```

### 10.2 API Documentation (OpenAPI)

```python
# backend/app/main.py
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Cirujano API",
        version="1.0.0",
        description="API de gestión de reparaciones quirúrgicas",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://cirujano.com/logo.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Acceder en: http://localhost:8000/docs
```

---

## 📊 RESUMEN COMPLETO 1000%

| Fase | Objetivo | Status | Horas |
|------|----------|--------|-------|
| 1 | SASS ULTRA 7-1 | ⏳ TODO | 8h |
| 2 | FRONT SECURITY | ⏳ TODO | 6h |
| 3 | BACK SECURITY | ⏳ TODO | 8h |
| 4 | TYPESCRIPT TOTAL | ⏳ TODO | 12h |
| 5 | TESTING 90%+ | ⏳ TODO | 14h |
| 6 | SANITIZACIÓN | ⏳ TODO | 8h |
| 7 | PERFORMANCE | ⏳ TODO | 8h |
| 8 | OBSERVABILIDAD | ⏳ TODO | 6h |
| 9 | CI/CD ENTERPRISE | ⏳ TODO | 6h |
| 10 | DOCUMENTACIÓN | ⏳ TODO | 4h |
| **TOTAL** | | | **70 HORAS** |

---

## 🎯 ¿COMENZAMOS?

**Recomendación: Empezar en paralelo**

1. **Developer A:** FASE 1 (SASS) + FASE 2 (Front Security)
2. **Developer B:** FASE 3 (Back Security) + FASE 6 (Sanitización)
3. **DevOps:** FASE 9 (CI/CD)

**Simultaneamente:** FASE 4 (TypeScript) - critical path

---

## ✨ RESULTADO FINAL: 100% → 1000%

**Antes:**
```
✅ Funciona
❌ Desorganizado
❌ Sin seguridad
❌ Sin tests
❌ Sin monitoreo
```

**Después:**
```
✅ Funciona perfectamente
✅ Organizado al máximo
✅ Seguro al 1000%
✅ 90%+ test coverage
✅ Monitoreo en tiempo real
✅ PRODUCTION-READY
✅ ENTERPRISE-GRADE
✅ LISTO PARA EQUIPO REAL
```

---

**¿Confirmamos y empezamos con FASE 1?**
