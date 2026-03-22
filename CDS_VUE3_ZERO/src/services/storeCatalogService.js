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
}

function compareStoreNames(a, b) {
  return String(a?.name || '').localeCompare(String(b?.name || ''), 'es', { sensitivity: 'base' })
}

export function sortStoreCatalog(catalog, { sortKey = 'featured' } = {}) {
  const rows = Array.isArray(catalog) ? [...catalog] : []

  switch (String(sortKey || 'featured')) {
    case 'name':
      return rows.sort(compareStoreNames)
    case 'price_asc':
      return rows.sort((a, b) => {
        const amountDiff = Number(a?.price || 0) - Number(b?.price || 0)
        return amountDiff !== 0 ? amountDiff : compareStoreNames(a, b)
      })
    case 'price_desc':
      return rows.sort((a, b) => {
        const amountDiff = Number(b?.price || 0) - Number(a?.price || 0)
        return amountDiff !== 0 ? amountDiff : compareStoreNames(a, b)
      })
    case 'stock_desc':
      return rows.sort((a, b) => {
        const stockDiff = Number(b?.sellable_stock || 0) - Number(a?.sellable_stock || 0)
        return stockDiff !== 0 ? stockDiff : compareStoreNames(a, b)
      })
    default:
      return rows
  }
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

export async function fetchStoreCatalog({
  isAuthenticated = false,
  limit = 5000,
  categoryId = null,
  search = '',
} = {}) {
  const endpoint = isAuthenticated ? '/inventory/' : '/inventory/public/'
  const params = isAuthenticated
    ? { limit }
    : { limit, enabled_only: false, in_stock_only: false }

  if (categoryId) params.category_id = categoryId
  if (String(search || '').trim()) params.search = String(search || '').trim()

  const response = await api.get(endpoint, { params })
  return normalizeStoreCatalogPayload(response?.data)
}

export const STORE_FEATURED_LIMIT = 12

// SKUs de productos destacados — verificados en la base de datos del inventario
export const FEATURED_SEARCH_TERMS = [
  'RES-10K-THT-AXIAL-0P25W',
  'CAPE-1U-50P0V',
  'OTROS-BOTON_PULSADOR_6X6X10MM_2PIN',
  'TRANSISTORES-LM7805'
]

// Imágenes de Cloudinary para destacados — la DB aún no tiene image_url para estos SKUs.
// El pulsador tiene extensión doble .jpg.webp: el SDK de Cloudinary la rompe (quita .webp →
// public_id queda ...PULSADOR.jpg → Cloudinary lo parsea como formato jpg → 404).
// Solución: URL directa construida desde la env, sin pasar por el SDK.
const _CLOUD = String(import.meta.env?.VITE_CLOUDINARY_CLOUD_NAME || '').trim()

const FEATURED_PRODUCT_IMAGE_OVERRIDES = {
  'RES-10K-THT-AXIAL-0P25W':            '/images/INVENTARIO/RESISTENCIA.webp',
  'CAPE-1U-50P0V':                       '/images/INVENTARIO/CAPACITOR_ELECTROLITICO.webp',
  'OTROS-BOTON_PULSADOR_6X6X10MM_2PIN': _CLOUD
    ? `https://res.cloudinary.com/${_CLOUD}/image/upload/INVENTARIO/PULSADOR_6X6_2_PIN.webp`
    : '',
  'TRANSISTORES-LM7805':                 '/images/INVENTARIO/TRANSISTOR_TO220.webp',
}

export async function fetchFeaturedProducts({ isAuthenticated = false } = {}) {
  const endpoint = isAuthenticated ? '/inventory/' : '/inventory/public/'
  const baseParams = isAuthenticated
    ? {}
    : { enabled_only: false, in_stock_only: false }

  const results = await Promise.all(
    FEATURED_SEARCH_TERMS.map(term =>
      api.get(endpoint, { params: { ...baseParams, search: term, limit: 2 } })
        .then(r => normalizeStoreCatalogPayload(r?.data))
        .catch(() => [])
    )
  )

  const seen = new Set()
  return results.flat()
    .filter(product => {
      const id = String(product.id)
      if (seen.has(id)) return false
      seen.add(id)
      return true
    })
    .map(product => {
      const imageOverride = FEATURED_PRODUCT_IMAGE_OVERRIDES[product.sku]
      if (imageOverride && !product.image_url) {
        return { ...product, image_url: imageOverride }
      }
      return product
    })
}

export async function searchStoreCatalog(query, { isAuthenticated = false, categoryId = null } = {}) {
  const endpoint = isAuthenticated ? '/inventory/' : '/inventory/public/'
  const params = { search: String(query || '').trim(), limit: 60 }
  if (!isAuthenticated) {
    params.enabled_only = false
    params.in_stock_only = false
  }
  if (categoryId) params.category_id = categoryId
  const response = await api.get(endpoint, { params })
  return normalizeStoreCatalogPayload(response?.data)
}

export async function loadStoreFeaturedSnapshot({ isAuthenticated = false } = {}) {
  try {
    const rows = await fetchFeaturedProducts({ isAuthenticated })
    if (rows.length > 0) return { rows, error: '' }
    // Los SKUs destacados no existen aún en esta DB — mostrar los primeros del catálogo público
    const fallback = await fetchStoreCatalog({ isAuthenticated, limit: STORE_FEATURED_LIMIT })
    return { rows: fallback, error: '' }
  } catch (requestError) {
    const cached = readStoreCatalogCache()
    if (cached.length > 0) {
      return {
        rows: cached.slice(0, STORE_FEATURED_LIMIT),
        error: 'No se pudo cargar. Mostrando productos guardados.',
        fromCache: true
      }
    }
    return { rows: [], error: extractErrorMessage(requestError) }
  }
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
