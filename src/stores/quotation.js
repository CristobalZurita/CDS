/**
 * Quotation Store - Pinia
 * Manages quotation state and selected instrument data
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useQuotationStore = defineStore('quotation', () => {
  // State
  const quotations = ref([])
  const selectedInstrument = ref(null)
  const selectedFaults = ref([])
  const currentQuotation = ref(null)
  const quotationHistory = ref([])
  const quotationItems = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // Computed
  const hasSelected = computed(() => selectedInstrument.value !== null)
  const hasFaults = computed(() => selectedFaults.value.length > 0)
  const hasQuotation = computed(() => currentQuotation.value !== null)
  const total = computed(() => {
    if (currentQuotation.value && Number.isFinite(Number(currentQuotation.value.total))) {
      return Number(currentQuotation.value.total)
    }
    return quotationItems.value.reduce((sum, item) => {
      const quantity = Number(item?.quantity || 0)
      const unitPrice = Number(item?.unitPrice || item?.unit_price || 0)
      return sum + (quantity * unitPrice)
    }, 0)
  })

  // Methods
  const setInstrument = (instrument) => {
    selectedInstrument.value = instrument
  }

  const setFaults = (faults) => {
    selectedFaults.value = faults
  }

  const setQuotation = (quotation) => {
    currentQuotation.value = quotation
    // Add to history
    quotationHistory.value.push({
      ...quotation,
      savedAt: new Date()
    })

    if (!quotation || quotation.id == null) {
      return
    }
    const quoteId = Number(quotation.id)
    const existingIndex = quotations.value.findIndex((item) => Number(item.id) === quoteId)
    if (existingIndex >= 0) {
      quotations.value[existingIndex] = quotation
    } else {
      quotations.value.push(quotation)
    }
  }

  const reset = () => {
    selectedInstrument.value = null
    selectedFaults.value = []
    currentQuotation.value = null
    quotationItems.value = []
    error.value = null
    isLoading.value = false
  }

  const clearInstrument = () => {
    selectedInstrument.value = null
  }

  const clearFaults = () => {
    selectedFaults.value = []
  }

  const addItem = (item) => {
    quotationItems.value.push(item)
  }

  const removeItem = (itemId) => {
    quotationItems.value = quotationItems.value.filter((item) => {
      const normalized = item?.id ?? item?.itemId
      return String(normalized) !== String(itemId)
    })
  }

  const updateItem = (itemId, updates) => {
    const index = quotationItems.value.findIndex((item) => {
      const normalized = item?.id ?? item?.itemId
      return String(normalized) === String(itemId)
    })
    if (index >= 0) {
      quotationItems.value[index] = {
        ...quotationItems.value[index],
        ...updates
      }
    }
  }

  const setError = (message) => {
    error.value = message
  }

  return {
    // State
    quotations,
    selectedInstrument,
    selectedFaults,
    currentQuotation,
    quotationHistory,
    quotationItems,
    loading: isLoading,
    isLoading,
    error,
    // Computed
    hasSelected,
    hasFaults,
    hasQuotation,
    total,
    // Methods
    setInstrument,
    setFaults,
    setQuotation,
    reset,
    clearInstrument,
    clearFaults,
    addItem,
    removeItem,
    updateItem,
    setError
  }
})
