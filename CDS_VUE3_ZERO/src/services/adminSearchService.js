import api from '@/services/api'

function normalizeAdminSearchResult(entry) {
  if (!entry || typeof entry !== 'object') return null

  return {
    type: String(entry?.type || ''),
    id: Number(entry?.id || 0),
    label: String(entry?.label || ''),
    subtitle: String(entry?.subtitle || ''),
    client_id: Number(entry?.client_id || 0),
    repair_id: Number(entry?.repair_id || 0),
    quote_id: Number(entry?.quote_id || 0),
    product_id: Number(entry?.product_id || 0),
    ticket_id: Number(entry?.ticket_id || 0),
    manual_id: Number(entry?.manual_id || 0),
    purchase_request_id: Number(entry?.purchase_request_id || 0)
  }
}

export async function searchAdminRecords(query, { limit = 8 } = {}) {
  const trimmedQuery = String(query || '').trim()
  if (trimmedQuery.length < 2) return []

  const response = await api.get('/search/', {
    params: {
      query: trimmedQuery,
      limit
    }
  })

  const payload = Array.isArray(response?.data) ? response.data : []
  return payload.map(normalizeAdminSearchResult).filter(Boolean)
}

export function resolveAdminSearchRoute(result) {
  const type = String(result?.type || '').toLowerCase()

  if (type === 'repair' && Number(result?.repair_id || result?.id || 0) > 0) {
    return { name: 'admin-repair-detail', params: { id: Number(result.repair_id || result.id) } }
  }

  if (type === 'purchase_request') return { name: 'admin-purchase-requests' }
  if (type === 'inventory') return { name: 'admin-inventory' }
  if (type === 'quote') return { name: 'admin-quotes' }
  if (type === 'ticket') return { name: 'admin-tickets' }
  if (type === 'manual') return { name: 'admin-manuals' }
  if (['client', 'device'].includes(type)) return { name: 'admin-clients' }

  return { name: 'admin-dashboard' }
}

export function formatAdminSearchType(type) {
  const labels = {
    client: 'Cliente',
    device: 'Dispositivo',
    repair: 'OT',
    quote: 'Cotizacion',
    inventory: 'Inventario',
    ticket: 'Ticket',
    manual: 'Manual',
    purchase_request: 'Compra'
  }

  return labels[String(type || '').toLowerCase()] || 'Registro'
}
