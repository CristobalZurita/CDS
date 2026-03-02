/**
 * useQuotation - Composable para gestionar cotizaciones
 *
 * Este composable conecta el frontend con el endpoint /quotations/estimate del backend.
 * Maneja los estados de loading, error y result de las cotizaciones.
 */

import { ref, computed } from 'vue'
import { post } from '@/services/api'
import { useQuotationStore } from '@/stores/quotation'
import { showSuccess, showError } from '@/services/toastService'
import type { ComputedRef, Ref } from 'vue'

interface QuotationResponse {
  data?: any
  min_price: number
  max_price: number
  exceeds_recommendation?: boolean
  summary?: Record<string, any>
  disclaimer?: string
  [key: string]: any
}

interface GuidedQuotationPayload {
  selected_symptoms?: string[]
  guided_answers?: Record<string, any>
  customer_notes?: string
  visual_issue_count?: number
  marked_faults?: string[]
}

interface PriceRange {
  min: number
  max: number
  mid: number
  formattedMin: string
  formattedMax: string
  formattedMid: string
}

export interface UseQuotationComposable {
  // State
  loading: Ref<boolean>
  error: Ref<string | null>
  quotation: Ref<QuotationResponse | null>
  lastRequestTime: Ref<Date | null>

  // Methods
  estimate: (
    instrumentId: string,
    payloadOrFaults: string[] | GuidedQuotationPayload,
    turnstileToken?: string | null
  ) => Promise<QuotationResponse>
  reset: () => void
  copyPriceRange: () => boolean

  // Computed
  hasQuotation: ComputedRef<boolean>
  exceedsRecommendation: ComputedRef<boolean>
  priceRange: ComputedRef<PriceRange>
  minPrice: ComputedRef<number>
  maxPrice: ComputedRef<number>
  midPrice: ComputedRef<number>
  formattedMinPrice: ComputedRef<string>
  formattedMaxPrice: ComputedRef<string>
  formattedMidPrice: ComputedRef<string>
}

export function useQuotation(): UseQuotationComposable {
  const quotationStore = useQuotationStore()

  // State
  const loading = ref(false)
  const error = ref<string | null>(null)
  const quotation = ref<QuotationResponse | null>(null)
  const lastRequestTime = ref<Date | null>(null)

  /**
   * Genera una cotización estimada basada en instrumento y fallas
   *
   * @param {string} instrumentId - ID del instrumento (ej: 'moog-minimoog')
   * @param {Array<string>} faults - Lista de IDs de fallas (ej: ['POWER', 'FILTER_PROBLEM'])
   * @param {string | null} turnstileToken - Token de Turnstile para validación
   * @returns {Promise<QuotationResponse>} - Cotización generada
   * @throws {Error} - Si hay error en la solicitud
   */
  const estimate = async (
    instrumentId: string,
    payloadOrFaults: string[] | GuidedQuotationPayload,
    turnstileToken: string | null = null
  ): Promise<QuotationResponse> => {
    if (!instrumentId) {
      error.value = 'Debe seleccionar un instrumento'
      throw new Error('Instrumento no seleccionado')
    }

    const isLegacyFaultList = Array.isArray(payloadOrFaults)
    if (isLegacyFaultList && payloadOrFaults.length === 0) {
      error.value = 'Debe seleccionar al menos una falla'
      throw new Error('No hay fallas seleccionadas')
    }

    loading.value = true
    error.value = null
    lastRequestTime.value = new Date()

    try {
      const requestBody = isLegacyFaultList
        ? {
            instrument_id: instrumentId,
            faults: payloadOrFaults,
            turnstile_token: turnstileToken,
          }
        : {
            instrument_id: instrumentId,
            faults: [],
            ...payloadOrFaults,
            turnstile_token: turnstileToken,
          }

      const response = await post<QuotationResponse>('/quotations/estimate', {
        ...requestBody,
      })

      const data = response.data.data || response.data

      quotation.value = data
      quotationStore.setQuotation(data)
      showSuccess('Cotización generada exitosamente')
      return data
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Error al generar cotización'
      error.value = errorMessage
      quotation.value = null
      showError(errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Reinicia los estados de la cotización
   */
  const reset = (): void => {
    quotation.value = null
    error.value = null
    loading.value = false
    lastRequestTime.value = null
    quotationStore.reset()
  }

  /**
   * Copia el rango de precio al portapapeles
   */
  const copyPriceRange = (): boolean => {
    if (!quotation.value) return false

    const text = `Cotización: $${quotation.value.min_price} - $${quotation.value.max_price} CLP`
    navigator.clipboard
      .writeText(text)
      .then(() => {
        return true
      })
      .catch(() => {
        return false
      })
    return true
  }

  // Computed properties
  const hasQuotation = computed((): boolean => quotation.value !== null)

  const exceedsRecommendation = computed((): boolean => quotation.value?.exceeds_recommendation ?? false)

  const minPrice = computed((): number => quotation.value?.min_price ?? 0)

  const maxPrice = computed((): number => quotation.value?.max_price ?? 0)

  const midPrice = computed((): number => {
    if (!quotation.value) return 0
    return Math.round((quotation.value.min_price + quotation.value.max_price) / 2)
  })

  const formattedMinPrice = computed((): string => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(minPrice.value)
  })

  const formattedMaxPrice = computed((): string => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(maxPrice.value)
  })

  const formattedMidPrice = computed((): string => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(midPrice.value)
  })

  const priceRange = computed((): PriceRange => ({
    min: minPrice.value,
    max: maxPrice.value,
    mid: midPrice.value,
    formattedMin: formattedMinPrice.value,
    formattedMax: formattedMaxPrice.value,
    formattedMid: formattedMidPrice.value
  }))

  return {
    // State
    loading,
    error,
    quotation,
    lastRequestTime,

    // Methods
    estimate,
    reset,
    copyPriceRange,

    // Computed
    hasQuotation,
    exceedsRecommendation,
    priceRange,
    minPrice,
    maxPrice,
    midPrice,
    formattedMinPrice,
    formattedMaxPrice,
    formattedMidPrice
  }
}
