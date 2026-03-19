import { computed, ref } from 'vue'
import {
  activateCotizadorNotFoundMode,
  createCotizadorLeadForm,
  deactivateCotizadorNotFoundMode,
  formatCotizadorCost,
  resetCotizadorFlowState,
  resetCotizadorLeadTurnstile,
  resetCotizadorQuoteTurnstile,
  setCotizadorBrandSelection,
  setCotizadorModelSelection,
  toggleCotizadorFaultSelection
} from './cotizadorFlowStateSupport'

export function useCotizadorFlowState() {
  const step = ref(1)
  const brands = ref([])
  const selectedBrand = ref('')
  const models = ref([])
  const selectedModel = ref('')
  const faults = ref([])
  const selectedFaultIds = ref([])
  const quoteResult = ref(null)
  const leadForm = ref(createCotizadorLeadForm())
  const acceptedDisclaimer = ref(false)
  const quoteTurnstileToken = ref('')
  const quoteTurnstileRenderKey = ref(0)
  const leadTurnstileToken = ref('')
  const leadTurnstileRenderKey = ref(0)
  const leadSubmitted = ref(false)
  const notFoundMode = ref(false)
  const manualBrand = ref('')
  const manualModel = ref('')

  const canContinueStep1 = computed(() =>
    notFoundMode.value
      ? Boolean(manualBrand.value.trim() && manualModel.value.trim())
      : Boolean(selectedBrand.value && selectedModel.value)
  )

  const canContinueStep2 = computed(() =>
    selectedFaultIds.value.length > 0 &&
    String(quoteTurnstileToken.value || '').length > 0
  )

  const canSubmitLead = computed(() =>
    String(leadForm.value.nombre || '').trim().length > 0 &&
    String(leadForm.value.email || '').trim().length > 0 &&
    acceptedDisclaimer.value &&
    String(leadTurnstileToken.value || '').length > 0
  )

  const formattedFinalCost = computed(() => {
    if (!quoteResult.value) return '—'
    return formatCotizadorCost(quoteResult.value.final_cost)
  })

  const selectedBrandName = computed(() => {
    if (notFoundMode.value) return manualBrand.value
    const match = brands.value.find((brand) => brand.id === selectedBrand.value)
    return match ? match.name : selectedBrand.value
  })

  const selectedModelName = computed(() => {
    if (notFoundMode.value) return manualModel.value
    const match = models.value.find((model) => model.id === selectedModel.value)
    return match ? match.model : selectedModel.value
  })

  const selectedFaultNames = computed(() =>
    faults.value
      .filter((fault) => selectedFaultIds.value.includes(fault.id))
      .map((fault) => fault.name)
  )

  function resetQuoteTurnstile() {
    resetCotizadorQuoteTurnstile({
      quoteTurnstileToken,
      quoteTurnstileRenderKey
    })
  }

  function resetLeadTurnstile() {
    resetCotizadorLeadTurnstile({
      leadTurnstileToken,
      leadTurnstileRenderKey
    })
  }

  function onQuoteVerify(token) {
    quoteTurnstileToken.value = token
  }

  function onLeadVerify(token) {
    leadTurnstileToken.value = token
  }

  function setBrandSelection(brandId) {
    setCotizadorBrandSelection({
      selectedBrand,
      selectedModel,
      models,
      faults,
      selectedFaultIds,
      quoteTurnstileToken,
      quoteTurnstileRenderKey,
      leadTurnstileToken,
      leadTurnstileRenderKey
    }, brandId)
  }

  function setModelSelection(instrumentId) {
    setCotizadorModelSelection({
      selectedModel,
      faults,
      selectedFaultIds,
      quoteTurnstileToken,
      quoteTurnstileRenderKey,
      leadTurnstileToken,
      leadTurnstileRenderKey
    }, instrumentId)
  }

  function toggleFaultSelection(faultId) {
    toggleCotizadorFaultSelection({
      selectedFaultIds,
      quoteTurnstileToken,
      quoteTurnstileRenderKey,
      leadTurnstileToken,
      leadTurnstileRenderKey
    }, faultId)
  }

  function activateNotFoundMode() {
    activateCotizadorNotFoundMode({
      notFoundMode,
      selectedBrand,
      selectedModel,
      models,
      faults,
      selectedFaultIds,
      quoteTurnstileToken,
      quoteTurnstileRenderKey,
      leadTurnstileToken,
      leadTurnstileRenderKey
    })
  }

  function deactivateNotFoundMode() {
    deactivateCotizadorNotFoundMode({
      notFoundMode,
      manualBrand,
      manualModel,
      leadTurnstileToken,
      leadTurnstileRenderKey,
      quoteTurnstileToken,
      quoteTurnstileRenderKey
    })
  }

  function goToLeadStep() {
    resetLeadTurnstile()
    step.value = 4
  }

  function resetAll() {
    resetCotizadorFlowState({
      step,
      selectedBrand,
      selectedModel,
      models,
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
      manualModel
    })
  }

  return {
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
    resetAll
  }
}
