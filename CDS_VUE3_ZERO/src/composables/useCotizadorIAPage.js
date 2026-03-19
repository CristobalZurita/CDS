import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { extractErrorMessage } from '@/services/api'
import {
  listApplicableQuotationFaults,
  listQuotationBrands,
  listQuotationModelsByBrand,
  normalizeQuotationEstimate,
  requestQuotationEstimate,
  submitQuotationLead,
} from '@/services/quotationService'
import { useCotizadorFlowState } from './useCotizadorFlowState'

export function useCotizadorIAPage() {
  const router = useRouter()
  const loading = ref(false)
  const error = ref('')

  const state = useCotizadorFlowState()
  const {
    step,
    brands,
    selectedBrand,
    models,
    selectedModel,
    faults,
    selectedFaultIds,
    quoteResult,
    leadForm,
    acceptedDisclaimer,
    quoteTurnstileToken,
    quoteTurnstileRenderKey,
    leadTurnstileToken,
    leadTurnstileRenderKey,
    leadSubmitted,
    notFoundMode,
    manualBrand,
    manualModel,
    canContinueStep1,
    canContinueStep2,
    canSubmitLead,
    formattedFinalCost,
    selectedBrandName,
    selectedModelName,
    selectedFaultNames,
    resetQuoteTurnstile,
    resetLeadTurnstile,
    onQuoteVerify,
    onLeadVerify,
    setBrandSelection,
    setModelSelection,
    toggleFaultSelection,
    activateNotFoundMode,
    deactivateNotFoundMode,
    goToLeadStep,
    resetAll,
  } = state

  async function loadBrands() {
    loading.value = true
    error.value = ''
    try {
      brands.value = await listQuotationBrands()
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function onBrandSelect(brandId) {
    setBrandSelection(brandId)
    error.value = ''
    if (!brandId) return

    loading.value = true
    try {
      models.value = await listQuotationModelsByBrand(brandId)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  async function onModelSelect(instrumentId) {
    setModelSelection(instrumentId)
    error.value = ''
    if (!instrumentId) return

    loading.value = true
    try {
      faults.value = await listApplicableQuotationFaults(instrumentId)
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
    } finally {
      loading.value = false
    }
  }

  function toggleFault(faultId) {
    toggleFaultSelection(faultId)
    error.value = ''
  }

  async function calculateQuote() {
    loading.value = true
    error.value = ''
    quoteResult.value = null

    try {
      const data = await requestQuotationEstimate({
        instrumentId: selectedModel.value,
        faultIds: selectedFaultIds.value,
        turnstileToken: quoteTurnstileToken.value,
      })
      quoteResult.value = normalizeQuotationEstimate(data, {
        selectedBrandName: selectedBrandName.value,
        selectedModelName: selectedModelName.value,
      })
      resetLeadTurnstile()
      step.value = 3
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      resetQuoteTurnstile()
    } finally {
      loading.value = false
    }
  }

  async function submitLead() {
    loading.value = true
    error.value = ''
    try {
      await submitQuotationLead({
        leadForm: leadForm.value,
        selectedBrandName: selectedBrandName.value,
        selectedModelName: selectedModelName.value,
        quoteResult: quoteResult.value,
        turnstileToken: leadTurnstileToken.value,
      })
      leadSubmitted.value = true
    } catch (requestError) {
      error.value = extractErrorMessage(requestError)
      resetLeadTurnstile()
    } finally {
      loading.value = false
    }
  }

  function enableNotFoundMode() {
    activateNotFoundMode()
    error.value = ''
  }

  function disableNotFoundMode() {
    deactivateNotFoundMode()
    error.value = ''
  }

  function handleQuoteVerify(token) {
    onQuoteVerify(token)
    error.value = ''
  }

  function handleLeadVerify(token) {
    onLeadVerify(token)
    error.value = ''
  }

  function resetCotizador() {
    resetAll()
    error.value = ''
  }

  function goToSchedule() {
    router.push('/agendar')
  }

  onMounted(loadBrands)

  return {
    step,
    loading,
    error,
    brands,
    selectedBrand,
    models,
    selectedModel,
    faults,
    selectedFaultIds,
    quoteResult,
    leadForm,
    acceptedDisclaimer,
    leadSubmitted,
    notFoundMode,
    manualBrand,
    manualModel,
    canContinueStep1,
    canContinueStep2,
    canSubmitLead,
    formattedFinalCost,
    selectedBrandName,
    selectedModelName,
    selectedFaultNames,
    quoteTurnstileToken,
    quoteTurnstileRenderKey,
    leadTurnstileToken,
    leadTurnstileRenderKey,
    onBrandSelect,
    onModelSelect,
    toggleFault,
    calculateQuote,
    submitLead,
    onQuoteVerify: handleQuoteVerify,
    onLeadVerify: handleLeadVerify,
    goToLeadStep,
    goToSchedule,
    resetAll: resetCotizador,
    activateNotFoundMode: enableNotFoundMode,
    deactivateNotFoundMode: disableNotFoundMode,
  }
}
