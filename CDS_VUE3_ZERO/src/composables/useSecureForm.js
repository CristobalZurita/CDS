/**
 * useSecureForm - Composable para formularios con sanitización automática
 * 
 * Uso:
 * const { form, sanitizeForm, sanitizeField } = useSecureForm({
 *   name: '',
 *   email: '',
 *   description: ''
 * })
 * 
 * // Al enviar:
 * const cleanData = sanitizeForm()
 * await api.post('/clients', cleanData)
 */

import { reactive } from 'vue'
import { sanitizeInput, sanitizeEmail, sanitizePhone, sanitizeHTML } from '@/utils/sanitize'

export function useSecureForm(initialValues = {}) {
  const form = reactive({ ...initialValues })

  /**
   * Sanitiza un campo específico
   * @param {string} field - Nombre del campo
   * @param {string} type - Tipo de sanitización ('text', 'email', 'phone', 'html')
   */
  function sanitizeField(field, type = 'text') {
    const value = form[field]
    if (typeof value !== 'string') return value

    switch (type) {
      case 'email':
        return sanitizeEmail(value) || value
      case 'phone':
        return sanitizePhone(value) || value
      case 'html':
        return sanitizeHTML(value)
      case 'text':
      default:
        return sanitizeInput(value)
    }
  }

  /**
   * Sanitiza todo el formulario
   * @param {Object} options - Mapa de campo => tipo de sanitización
   * @example sanitizeForm({ name: 'text', email: 'email', notes: 'html' })
   */
  function sanitizeForm(options = {}) {
    const clean = {}
    
    for (const [key, value] of Object.entries(form)) {
      // Si hay opciones específicas para este campo, usarlas
      if (options[key]) {
        clean[key] = sanitizeField(key, options[key])
      } else if (typeof value === 'string') {
        // Default: sanitizar como texto plano
        clean[key] = sanitizeInput(value)
      } else {
        // No es string, copiar tal cual
        clean[key] = value
      }
    }
    
    return clean
  }

  /**
   * Resetea el formulario a valores iniciales
   */
  function resetForm() {
    Object.assign(form, initialValues)
  }

  return {
    form,
    sanitizeField,
    sanitizeForm,
    resetForm
  }
}

/**
 * Helper para sanitizar antes de enviar a API
 * @param {Object} data - Datos a enviar
 * @param {Object} fieldTypes - Tipos de campo
 * @returns {Object} Datos limpios
 */
export function sanitizeForAPI(data, fieldTypes = {}) {
  const clean = {}
  
  for (const [key, value] of Object.entries(data)) {
    if (typeof value !== 'string') {
      clean[key] = value
      continue
    }
    
    switch (fieldTypes[key]) {
      case 'email':
        clean[key] = sanitizeEmail(value) || value
        break
      case 'phone':
        clean[key] = sanitizePhone(value) || value
        break
      case 'html':
        clean[key] = sanitizeHTML(value)
        break
      case 'text':
      default:
        clean[key] = sanitizeInput(value)
    }
  }
  
  return clean
}
