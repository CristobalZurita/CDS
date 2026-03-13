/**
 * Composable para resolver slots de medios dinámicos desde la BD.
 * Lee GET /api/v1/media/bindings una sola vez (caché de módulo),
 * y expone resolveSlot(slotKey) → secure_url o null.
 *
 * Fallback: si el slot no está en BD, busca en image-mapping.json
 * usando la ruta local del slot como clave (e.g. "/images/logo/logo.webp").
 */

import { ref, readonly } from 'vue'
import api from '@/services/api.js'

// Caché a nivel de módulo — se comparte entre todas las instancias del composable.
// Se carga una sola vez por sesión de navegación.
let _promise = null
const _map = ref({}) // slot_key → secure_url
const _loaded = ref(false)
const _error = ref(null)

function _fetchBindings() {
  if (_promise) return _promise
  _promise = api
    .get('/media/bindings')
    .then(({ data }) => {
      const entries = Array.isArray(data) ? data : (data?.data ?? [])
      const map = {}
      for (const binding of entries) {
        if (binding?.slot_key && binding?.asset?.secure_url) {
          map[binding.slot_key] = binding.asset.secure_url
        }
      }
      _map.value = map
      _loaded.value = true
    })
    .catch((err) => {
      _error.value = err?.message || 'Error al cargar bindings'
      // No reseteamos _promise para evitar loops; los slots usarán fallback.
    })
  return _promise
}

/**
 * Resuelve un slot_key a una URL.
 * - Si los bindings ya están cargados → sincrónico.
 * - Si no → devuelve null hasta que la carga termine (reactivo vía _map).
 *
 * @param {string} slotKey  Ej: "home.hero.bg"
 * @returns {string|null}
 */
function resolveSlot(slotKey) {
  if (!slotKey) return null
  return _map.value[slotKey] ?? null
}

/**
 * Resuelve un slot_key; si no tiene binding usa fallbackUrl.
 * Útil directamente en templates: resolveSlotOr('home.hero.logo', resolveImageUrl('/images/logo/logo.webp'))
 *
 * @param {string} slotKey
 * @param {string} fallbackUrl
 * @returns {string}
 */
function resolveSlotOr(slotKey, fallbackUrl) {
  return _map.value[slotKey] ?? fallbackUrl ?? ''
}

/**
 * Fuerza recarga de bindings (útil después de guardar cambios en el admin).
 */
function reloadBindings() {
  _promise = null
  _loaded.value = false
  _error.value = null
  _map.value = {}
  return _fetchBindings()
}

export function useMediaBinding() {
  // Inicia la carga si aún no comenzó.
  _fetchBindings()

  return {
    bindingsMap: readonly(_map),
    bindingsLoaded: readonly(_loaded),
    bindingsError: readonly(_error),
    resolveSlot,
    resolveSlotOr,
    reloadBindings,
  }
}
