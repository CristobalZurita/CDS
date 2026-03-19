import { computed, ref } from 'vue'

function createLeadForm() {
  return { nombre: '', email: '', telefono: '' }
}

function formatQuotationCost(value) {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}

export function useCotizadorFlowState() {
  const step = ref(1)
  const brands = ref([])
  const selectedBrand = ref('')
  const models = ref([])
  const selectedModel = ref('')
  const faults = ref([])
  const selectedFaultIds = ref([])
  const quoteResult = ref(null)
  const leadForm = ref(createLeadForm())
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
    return formatQuotationCost(quoteResult.value.final_cost)
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
    quoteTurnstileToken.value = ''
    quoteTurnstileRenderKey.value += 1
  }

  function resetLeadTurnstile() {
    leadTurnstileToken.value = ''
    leadTurnstileRenderKey.value += 1
  }

  function onQuoteVerify(token) {
    quoteTurnstileToken.value = token
  }

  function onLeadVerify(token) {
    leadTurnstileToken.value = token
  }

  function setBrandSelection(brandId) {
    selectedBrand.value = brandId
    selectedModel.value = ''
    models.value = []
    faults.value = []
    selectedFaultIds.value = []
    if (!brandId) return
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function setModelSelection(instrumentId) {
    selectedModel.value = instrumentId
    faults.value = []
    selectedFaultIds.value = []
    if (!instrumentId) return
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function toggleFaultSelection(faultId) {
    const idx = selectedFaultIds.value.indexOf(faultId)
    selectedFaultIds.value = idx === -1
      ? [...selectedFaultIds.value, faultId]
      : selectedFaultIds.value.filter((id) => id !== faultId)
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function activateNotFoundMode() {
    notFoundMode.value = true
    selectedBrand.value = ''
    selectedModel.value = ''
    models.value = []
    faults.value = []
    selectedFaultIds.value = []
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function deactivateNotFoundMode() {
    notFoundMode.value = false
    manualBrand.value = ''
    manualModel.value = ''
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function goToLeadStep() {
    resetLeadTurnstile()
    step.value = 4
  }

  function resetAll() {
    step.value = 1
    selectedBrand.value = ''
    selectedModel.value = ''
    models.value = []
    faults.value = []
    selectedFaultIds.value = []
    quoteResult.value = null
    leadForm.value = createLeadForm()
    acceptedDisclaimer.value = false
    quoteTurnstileToken.value = ''
    quoteTurnstileRenderKey.value = 0
    leadTurnstileToken.value = ''
    leadTurnstileRenderKey.value = 0
    leadSubmitted.value = false
    notFoundMode.value = false
    manualBrand.value = ''
    manualModel.value = ''
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
