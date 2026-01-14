/**
 * useQuotation - Composable para gestionar cotizaciones
 * 
 * Este composable conecta el frontend con el endpoint /quotations/estimate del backend.
 * Maneja los estados de loading, error y result de las cotizaciones.
 */

import { ref, computed } from 'vue'
import { useApi } from './useApi'
import { useQuotationStore } from '@/stores/quotation'
import { showSuccess, showError } from '@/services/toastService'

export function useQuotation() {
  const { api } = useApi()
  const quotationStore = useQuotationStore()
  
  // State
  const loading = ref(false)
  const error = ref(null)
  const quotation = ref(null)
  const lastRequestTime = ref(null)
  
  /**
   * Genera una cotización estimada basada en instrumento y fallas
   * 
   * @param {string} instrumentId - ID del instrumento (ej: 'moog-minimoog')
   * @param {Array<string>} faults - Lista de IDs de fallas (ej: ['POWER', 'FILTER_PROBLEM'])
   * @returns {Promise<Object>} - Cotización generada
   * @throws {Error} - Si hay error en la solicitud
   */
  const estimate = async (instrumentId, faults) => {
    if (!instrumentId) {
      error.value = 'Debe seleccionar un instrumento'
      throw new Error('Instrumento no seleccionado')
    }
    
    if (!faults || faults.length === 0) {
      error.value = 'Debe seleccionar al menos una falla'
      throw new Error('No hay fallas seleccionadas')
    }
    
    loading.value = true
    error.value = null
    lastRequestTime.value = new Date()
    
    try {
      const response = await api.post('/quotations/estimate', {
        instrument_id: instrumentId,
        faults: faults
      })
      
      quotation.value = response.data
      quotationStore.setQuotation(response.data)
      showSuccess('Cotización generada exitosamente')
      return response.data
      
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Error al generar cotización'
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
  const reset = () => {
    quotation.value = null
    error.value = null
    loading.value = false
    lastRequestTime.value = null
    quotationStore.reset()
  }
  
  /**
   * Copia el rango de precio al portapapeles
   */
  const copyPriceRange = () => {
    if (!quotation.value) return false
    
    const text = `Cotización: $${quotation.value.min_price} - $${quotation.value.max_price} CLP`
    navigator.clipboard.writeText(text).then(() => {
      return true
    }).catch(() => {
      return false
    })
  }
  
  // Computed properties
  const hasQuotation = computed(() => quotation.value !== null)
  
  const exceedsRecommendation = computed(() => 
    quotation.value?.exceeds_recommendation ?? false
  )
  
  const minPrice = computed(() => quotation.value?.min_price ?? 0)
  
  const maxPrice = computed(() => quotation.value?.max_price ?? 0)
  
  const midPrice = computed(() => {
    if (!quotation.value) return 0
    return Math.round((quotation.value.min_price + quotation.value.max_price) / 2)
  })
  
  const formattedMinPrice = computed(() => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(minPrice.value)
  })
  
  const formattedMaxPrice = computed(() => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(maxPrice.value)
  })
  
  const formattedMidPrice = computed(() => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(midPrice.value)
  })
  
  const priceRange = computed(() => ({
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
