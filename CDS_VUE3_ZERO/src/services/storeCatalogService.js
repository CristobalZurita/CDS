import api, { extractErrorMessage } from '@/services/api'
import { useCloudinaryImage } from '@/composables/useCloudinary'
import { formatCurrency } from '@/utils/format'

const STORE_CATALOG_CACHE_KEY = 'cds_store_catalog_cache_v1'

export function normalizeStoreSearchText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export function readStoreCatalogCache() {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(STORE_CATALOG_CACHE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function writeStoreCatalogCache(rows) {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(STORE_CATALOG_CACHE_KEY, JSON.stringify(Array.isArray(rows) ? rows : []))
  } catch {
    // noop
  }
}

export function clearStoreCatalogCache() {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.removeItem(STORE_CATALOG_CACHE_KEY)
  } catch {
    // noop
  }
}

export function parseStoreDescriptionMeta(rawDescription) {
  const text = String(rawDescription || '').trim()
  if (!text.startsWith('{')) return { text }
  try {
    const payload = JSON.parse(text)
    return typeof payload === 'object' && payload ? payload : {}
  } catch {
    return { text }
  }
}

export function describeStoreProduct(product) {
  const meta = parseStoreDescriptionMeta(product?.description)
  if (meta.text && meta.text !== 'Importado desde Excel (N°)') return meta.text
  const parts = [meta.family || product?.family, meta.source, meta.origin_status || product?.origin_status]
    .map((part) => String(part || '').replaceAll('_', ' ').trim())
    .filter(Boolean)
  return parts.join(' · ') || 'Repuesto disponible'
}

export function resolveStoreProductImage(product) {
  const value = String(product?.image_url || '').trim()
  if (!value) return ''
  if (/^https?:\/\//i.test(value)) return value
  const normalized = value.startsWith('/') ? value : `/${value.replace(/^\/+/, '')}`
  return useCloudinaryImage(normalized)
}

export function formatStoreLinePrice(value) {
  const amount = Number(value || 0)
  return amount > 0 ? formatCurrency(amount) : 'Por cotizar'
}

export function formatStoreSummaryAmount(value, totals) {
  const amount = Number(value || 0)
  return totals?.hasQuotedAmount && amount > 0 ? formatCurrency(amount) : 'Por cotizar'
}

export function buildIndexedStoreCatalog(catalog) {
  return (Array.isArray(catalog) ? catalog : []).map((product) => ({
    ...product,
    _searchIndex: normalizeStoreSearchText(
      [product.name, product.sku, product.family, product.category, describeStoreProduct(product)]
        .filter(Boolean)
        .join(' ')
    ),
  }))
}

export function filterStoreCatalog(catalog, { searchTerm = '', selectedCategory = '', selectedAvailability = 'all' } = {}) {
  const normalizedSearch = normalizeStoreSearchText(searchTerm)
  return buildIndexedStoreCatalog(catalog)
    .filter((product) => {
      if (selectedCategory && product.category !== selectedCategory) return false
      if (selectedAvailability === 'sellable' && Number(product.sellable_stock || 0) <= 0) return false
      if (
        selectedAvailability === 'reserved' &&
        !(Number(product.available_stock || 0) > 0 && Number(product.sellable_stock || 0) <= 0)
      ) return false
      if (selectedAvailability === 'out' && Number(product.available_stock || 0) > 0) return false
      if (!normalizedSearch) return true
      return product._searchIndex.includes(normalizedSearch)
    })
    .sort((a, b) =>
      String(a.name || '').localeCompare(String(b.name || ''), 'es', { sensitivity: 'base' })
    )
}

export function listStoreCategories(catalog) {
  const values = new Set(
    (Array.isArray(catalog) ? catalog : [])
      .map((product) => String(product.category || '').trim())
      .filter(Boolean)
  )
  return Array.from(values).sort((a, b) => a.localeCompare(b, 'es'))
}

export function normalizeStoreCatalogPayload(payload) {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.data)) return payload.data
  if (Array.isArray(payload?.items)) return payload.items
  if (Array.isArray(payload?.results)) return payload.results
  return []
}

export async function fetchStoreCatalog({ isAuthenticated = false } = {}) {
  const endpoint = isAuthenticated ? '/inventory/' : '/inventory/public/'
  const params = isAuthenticated
    ? { limit: 5000 }
    : { limit: 5000, enabled_only: false, in_stock_only: false }

  const response = await api.get(endpoint, { params })
  return normalizeStoreCatalogPayload(response?.data)
}

export async function loadStoreCatalogSnapshot({ isAuthenticated = false } = {}) {
  try {
    const rows = await fetchStoreCatalog({ isAuthenticated })

    if (rows.length > 0) {
      writeStoreCatalogCache(rows)
      return {
        rows,
        error: '',
        fromCache: false
      }
    }

    clearStoreCatalogCache()
    return {
      rows: [],
      error: '',
      fromCache: false
    }
  } catch (requestError) {
    const cached = readStoreCatalogCache()

    if (cached.length > 0) {
      return {
        rows: cached,
        error: 'No se pudo actualizar desde backend. Mostrando la última copia local del catálogo.',
        fromCache: true
      }
    }

    return {
      rows: [],
      error: extractErrorMessage(requestError),
      fromCache: false
    }
  }
}
