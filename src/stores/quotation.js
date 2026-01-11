/**
 * Quotation Store - Pinia
 * Manages quotation state and selected instrument data
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useQuotationStore = defineStore('quotation', () => {
  // State
  const selectedInstrument = ref(null)
  const selectedFaults = ref([])
  const currentQuotation = ref(null)
  const quotationHistory = ref([])

  // Computed
  const hasSelected = computed(() => selectedInstrument.value !== null)
  const hasFaults = computed(() => selectedFaults.value.length > 0)
  const hasQuotation = computed(() => currentQuotation.value !== null)

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
  }

  const reset = () => {
    selectedInstrument.value = null
    selectedFaults.value = []
    currentQuotation.value = null
  }

  const clearInstrument = () => {
    selectedInstrument.value = null
  }

  const clearFaults = () => {
    selectedFaults.value = []
  }

  return {
    // State
    selectedInstrument,
    selectedFaults,
    currentQuotation,
    quotationHistory,
    // Computed
    hasSelected,
    hasFaults,
    hasQuotation,
    // Methods
    setInstrument,
    setFaults,
    setQuotation,
    reset,
    clearInstrument,
    clearFaults
  }
})
