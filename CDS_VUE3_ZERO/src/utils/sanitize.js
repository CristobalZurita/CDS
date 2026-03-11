/**
 * Sanitización de inputs - Protección contra XSS
 * 
 * Reglas:
 * - Nunca confiar en input de usuario
 * - Sanitizar antes de enviar al backend
 * - Sanitizar antes de mostrar en DOM (si es necesario)
 */

import DOMPurify from 'dompurify'

// Configuración base de DOMPurify
const PURIFY_CONFIG = {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li'],
  ALLOWED_ATTR: [],
  KEEP_CONTENT: true
}

/**
 * Sanitiza HTML permitiendo solo etiquetas básicas de formato
 * Útil para descripciones, comentarios, etc.
 * @param {string} dirty - HTML potencialmente malicioso
 * @returns {string} HTML limpio
 */
export function sanitizeHTML(dirty) {
  if (typeof dirty !== 'string') return ''
  return DOMPurify.sanitize(dirty, PURIFY_CONFIG)
}

/**
 * Sanitiza texto plano - elimina TODO HTML
 * Útil para nombres, emails, campos de una línea
 * @param {string} value - Texto a limpiar
 * @returns {string} Texto sin HTML
 */
export function sanitizeText(value) {
  if (typeof value !== 'string') return ''
  return DOMPurify.sanitize(value, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] })
}

/**
 * Sanitiza input de usuario eliminando patrones peligrosos
 * Útil antes de enviar al backend
 * @param {string} value - Input del usuario
 * @returns {string} Input limpio
 */
export function sanitizeInput(value) {
  if (typeof value !== 'string') return value
  
  return value
    // Eliminar script tags y contenido
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    // Eliminar event handlers onclick, onerror, etc
    .replace(/\s*on\w+\s*=/gi, '')
    // Eliminar javascript: protocol
    .replace(/javascript:/gi, '')
    // Eliminar data: URIs potencialmente peligrosos
    .replace(/data:text\/html/gi, '')
    // Eliminar expresiones CSS peligrosas
    .replace(/expression\s*\(/gi, '')
    // Trim
    .trim()
}

/**
 * Sanitiza un objeto completo (recursivo)
 * Útil para formularios completos
 * @param {Object} obj - Objeto a sanitizar
 * @param {Function} sanitizer - Función de sanitización a usar
 * @returns {Object} Objeto limpio
 */
export function sanitizeObject(obj, sanitizer = sanitizeInput) {
  if (typeof obj !== 'object' || obj === null) {
    return typeof obj === 'string' ? sanitizer(obj) : obj
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item, sanitizer))
  }
  
  const clean = {}
  for (const [key, value] of Object.entries(obj)) {
    // La key no se sanitiza (debe ser código, no input de usuario)
    clean[key] = sanitizeObject(value, sanitizer)
  }
  return clean
}

/**
 * Valida y sanitiza email
 * @param {string} email - Email a validar
 * @returns {string|null} Email limpio o null si es inválido
 */
export function sanitizeEmail(email) {
  if (typeof email !== 'string') return null
  
  const clean = sanitizeText(email).toLowerCase().trim()
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  
  return emailRegex.test(clean) ? clean : null
}

/**
 * Valida y sanitiza teléfono
 * @param {string} phone - Teléfono a validar
 * @returns {string|null} Teléfono limpio o null
 */
export function sanitizePhone(phone) {
  if (typeof phone !== 'string') return null
  
  // Mantener solo dígitos, + y -
  const clean = phone.replace(/[^\d+\-\s]/g, '').trim()
  const digits = clean.replace(/\D/g, '')
  
  // Entre 7 y 15 dígitos
  return digits.length >= 7 && digits.length <= 15 ? clean : null
}

/**
 * Escapa HTML para mostrar como texto (no interpretar)
 * Útil para mostrar código o logs
 * @param {string} text - Texto a escapar
 * @returns {string} Texto con HTML escapado
 */
export function escapeHTML(text) {
  if (typeof text !== 'string') return ''
  
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

/**
 * Composable-ready: sanitización reactiva
 * Uso: const cleanName = useSanitized(form.name)
 * @param {Ref|string} value - Valor reactivo o string
 * @returns {ComputedRef|string} Valor sanitizado
 */
export function useSanitized(value, sanitizer = sanitizeInput) {
  // Si es ref, retornar computed
  if (value && typeof value === 'object' && 'value' in value) {
    return computed(() => sanitizer(value.value))
  }
  // Si es valor plano, sanitizar directo
  return sanitizer(value)
}
