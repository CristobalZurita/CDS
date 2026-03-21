/**
 * services/storeCatalogService.js
 * Reemplaza el existente. Usa el api.js ya configurado en el proyecto.
 */
import api from './api.js'

/** Listado paginado con filtros */
export async function fetchProducts({
  categoryId = null,
  search     = '',
  page       = 1,
  limit      = 24,
  sort       = 'name',   // name | price_asc | price_desc | newest
} = {}) {
  const params = { page, limit, sort }
  if (categoryId) params.category_id = categoryId
  if (search.trim()) params.search = search.trim()

  const { data } = await api.get('/shop/products', { params })
  return data  // { items: [], total: N, page: N, pages: N }
}

/** Detalle de un producto */
export async function fetchProduct(id) {
  const { data } = await api.get(`/shop/products/${id}`)
  return data
}

/** Árbol de categorías */
export async function fetchCategories() {
  const { data } = await api.get('/shop/categories')
  return data  // [{ id, name, description, product_count }]
}

/** Crear pedido */
export async function createOrder(payload) {
  /*
    payload: {
      customer: { name, email, phone, rut? },
      shipping: { address, commune, region },
      items: [{ product_id, qty, unit_price }],
      notes?: string,
      payment_method: 'webpay' | 'transfer' | 'store',
    }
  */
  const { data } = await api.post('/shop/orders', payload)
  return data  // { id, code, total, status, webpay_url? }
}

/** Iniciar pago Webpay (retorna redirect URL) */
export async function initiateWebpay(orderId) {
  const { data } = await api.post(`/shop/orders/${orderId}/pay/webpay`)
  return data  // { url, token }
}

/** Confirmar pago (callback Webpay) */
export async function confirmWebpay({ token_ws }) {
  const { data } = await api.post('/shop/pay/webpay/confirm', { token_ws })
  return data
}
