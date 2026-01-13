/**
 * Utility functions for the application
 */

export function useUtils() {
  return {
    parseCustomText,
    formatDate,
    formatPrice,
    slugify,
    debounce,
    throttle,
    clamp
  }
}

export function parseCustomText(text) {
  if (!text) return text
  
  // Convert **text** to <strong>text</strong>
  let parsed = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  
  // Convert *text* to <em>text</em>
  parsed = parsed.replace(/\*(.+?)\*/g, '<em>$1</em>')
  
  return parsed
}

export function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('es-CL')
}

export function formatPrice(price) {
  if (!price && price !== 0) return ''
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(price)
}

export function slugify(text) {
  if (!text) return ''
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
