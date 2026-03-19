import api from './api'

const QUOTATION_BASE_PATH = '/quotations'

export async function listQuotationBrands() {
  const { data } = await api.get(`${QUOTATION_BASE_PATH}/instruments/brands`)
  return Array.isArray(data) ? data : []
}

export async function listQuotationModelsByBrand(brandId) {
  const { data } = await api.get(`${QUOTATION_BASE_PATH}/instruments/models/${brandId}`)
  return Array.isArray(data) ? data : []
}

export async function listApplicableQuotationFaults(instrumentId) {
  const { data } = await api.get(`${QUOTATION_BASE_PATH}/faults/applicable/${instrumentId}`)
  return Array.isArray(data) ? data : []
}

export async function requestQuotationEstimate({ instrumentId, faultIds, turnstileToken }) {
  const { data } = await api.post(`${QUOTATION_BASE_PATH}/estimate`, {
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
  const summaryFinalCost = data?.summary?.final_cost
  const normalizedFinalCost = summaryFinalCost ?? data?.max_price ?? data?.min_price ?? 0

  return {
    equipment_info: {
      brand: data?.brand_name || selectedBrandName,
      model: selectedModelName,
    },
    base_cost: Number(data?.base_total || 0),
    complexity_factor: Number(data?.summary?.complexity_factor || data?.multiplier || 1),
    value_factor: Number(data?.summary?.value_factor || 1),
    final_cost: Number(normalizedFinalCost),
    min_price: Number(data?.min_price || 0),
    max_price: Number(data?.max_price || 0),
    disclaimer: data?.disclaimer || '',
    summary: data?.summary || {},
  }
}
