import api from './api'

// Catálogo servido desde keyboards_database.json — static-first, IA como fallback

export async function listQuotationBrands() {
  const { data } = await api.get('/catalog/brands')
  return Array.isArray(data) ? data : []
}

export async function listQuotationModelsByBrand(brandId) {
  const { data } = await api.get(`/catalog/models/${brandId}`)
  return Array.isArray(data) ? data : []
}

export async function listApplicableQuotationFaults(instrumentId) {
  const { data } = await api.get(`/catalog/faults/${instrumentId}`)
  return Array.isArray(data) ? data : []
}

export async function requestQuotationEstimate({ instrumentId, faultIds, turnstileToken }) {
  const { data } = await api.post('/catalog/quote', {
    instrument_id: instrumentId,
    faults: faultIds,
    turnstile_token: turnstileToken,
  })
  return data
}

export async function submitQuotationLead({
  leadForm,
  selectedBrandName,
  selectedModelName,
  quoteResult,
  turnstileToken,
}) {
  const { data } = await api.post('/leads', {
    nombre: leadForm?.nombre,
    email: leadForm?.email,
    telefono: leadForm?.telefono || null,
    equipment_brand: selectedBrandName,
    equipment_model: selectedModelName,
    quote_result: quoteResult,
    turnstile_token: turnstileToken,
  })
  return data
}

export function normalizeQuotationEstimate(data, { selectedBrandName = '', selectedModelName = '' } = {}) {
  const finalCost = data?.summary?.final_cost ?? data?.final_cost ?? data?.min_price ?? 0

  return {
    equipment_info: {
      brand: data?.brand_name || selectedBrandName,
      model: selectedModelName,
    },
    from_db: Boolean(data?.from_db),
    base_cost: Number(data?.min_price || 0),
    complexity_factor: Number(data?.summary?.complexity_factor || 1),
    value_factor: Number(data?.summary?.value_factor || 1),
    final_cost: Number(finalCost),
    min_price: Number(data?.min_price || 0),
    max_price: Number(data?.max_price || data?.min_price || 0),
    complexity: data?.complexity || '',
    valor_usd_min: Number(data?.valor_usd_min || 0),
    valor_usd_max: Number(data?.valor_usd_max || 0),
    tiempo_estimado: data?.tiempo_estimado || '',
    fallas_seleccionadas: Array.isArray(data?.fallas_seleccionadas) ? data.fallas_seleccionadas : [],
    disclaimer: data?.disclaimer || '',
    summary: data?.summary || {},
  }
}
