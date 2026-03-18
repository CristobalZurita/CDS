import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'
import {
  listApplicableQuotationFaults,
  listQuotationBrands,
  listQuotationModelsByBrand,
  normalizeQuotationEstimate,
  requestQuotationEstimate,
} from '@/services/quotationService'

export function useCotizadorIAPage() {
  const router = useRouter()

  // ── Navegación ───────────────────────────────────────────────────────────────
  const step = ref(1)
  const loading = ref(false)
  const error = ref('')

  // ── Paso 1: Marca + Modelo ───────────────────────────────────────────────────
  const brands = ref([])
  const selectedBrand = ref('')
  const models = ref([])
  const selectedModel = ref('')

  // ── Paso 2: Fallas ───────────────────────────────────────────────────────────
  const faults = ref([])
  const selectedFaultIds = ref([])

  // ── Paso 3: Resultado del cálculo ────────────────────────────────────────────
  const quoteResult = ref(null)

  // ── Paso 4: Formulario de contacto (lead) ────────────────────────────────────
  const leadForm = ref({ nombre: '', email: '', telefono: '' })
  const acceptedDisclaimer = ref(false)
  const quoteTurnstileToken = ref('')
  const quoteTurnstileRenderKey = ref(0)
  const leadTurnstileToken = ref('')
  const leadTurnstileRenderKey = ref(0)
  const leadSubmitted = ref(false)

  // ── Modo "instrumento no encontrado" ─────────────────────────────────────────
  const notFoundMode = ref(false)
  const manualBrand = ref('')
  const manualModel = ref('')

  // ── Computed ─────────────────────────────────────────────────────────────────
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
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(quoteResult.value.final_cost)
  })

  const selectedBrandName = computed(() => {
    if (notFoundMode.value) return manualBrand.value
    const b = brands.value.find(b => b.id === selectedBrand.value)
    return b ? b.name : selectedBrand.value
  })

  const selectedModelName = computed(() => {
    if (notFoundMode.value) return manualModel.value
    const m = models.value.find(m => m.id === selectedModel.value)
    return m ? m.model : selectedModel.value
  })

  const selectedFaultNames = computed(() =>
    faults.value
      .filter(f => selectedFaultIds.value.includes(f.id))
      .map(f => f.name)
  )

  // ── API pública canónica del cotizador ──────────────────────────────────────

  async function loadBrands() {
    loading.value = true
    error.value = ''
    try {
      brands.value = await listQuotationBrands()
    } catch (e) {
      error.value = extractErrorMessage(e)
    } finally {
      loading.value = false
    }
  }

  async function onBrandSelect(brandId) {
    selectedBrand.value = brandId
    selectedModel.value = ''
    models.value = []
    faults.value = []
    selectedFaultIds.value = []
    if (!brandId) return
    resetQuoteTurnstile()
    resetLeadTurnstile()
    loading.value = true
    error.value = ''
    try {
      models.value = await listQuotationModelsByBrand(brandId)
    } catch (e) {
      error.value = extractErrorMessage(e)
    } finally {
      loading.value = false
    }
  }

  async function onModelSelect(instrumentId) {
    selectedModel.value = instrumentId
    faults.value = []
    selectedFaultIds.value = []
    if (!instrumentId) return
    resetQuoteTurnstile()
    resetLeadTurnstile()
    loading.value = true
    error.value = ''
    try {
      faults.value = await listApplicableQuotationFaults(instrumentId)
    } catch (e) {
      error.value = extractErrorMessage(e)
    } finally {
      loading.value = false
    }
  }

  function toggleFault(faultId) {
    const idx = selectedFaultIds.value.indexOf(faultId)
    if (idx === -1) {
      selectedFaultIds.value = [...selectedFaultIds.value, faultId]
    } else {
      selectedFaultIds.value = selectedFaultIds.value.filter(id => id !== faultId)
    }
    resetQuoteTurnstile()
    resetLeadTurnstile()
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
    } catch (e) {
      error.value = extractErrorMessage(e)
      resetQuoteTurnstile()
    } finally {
      loading.value = false
    }
  }

  async function submitLead() {
    loading.value = true
    error.value = ''
    try {
      await api.post('/leads', {
        nombre: leadForm.value.nombre,
        email: leadForm.value.email,
        telefono: leadForm.value.telefono || null,
        equipment_brand: selectedBrandName.value,
        equipment_model: selectedModelName.value,
        quote_result: quoteResult.value,
        turnstile_token: leadTurnstileToken.value
      })
      leadSubmitted.value = true
    } catch (e) {
      error.value = extractErrorMessage(e)
      resetLeadTurnstile()
    } finally {
      loading.value = false
    }
  }

  function activateNotFoundMode() {
    notFoundMode.value = true
    selectedBrand.value = ''
    selectedModel.value = ''
    models.value = []
    faults.value = []
    selectedFaultIds.value = []
    error.value = ''
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function deactivateNotFoundMode() {
    notFoundMode.value = false
    manualBrand.value = ''
    manualModel.value = ''
    error.value = ''
    resetQuoteTurnstile()
    resetLeadTurnstile()
  }

  function onQuoteVerify(token) {
    quoteTurnstileToken.value = token
    error.value = ''
  }

  function onLeadVerify(token) {
    leadTurnstileToken.value = token
    error.value = ''
  }

  function resetQuoteTurnstile() {
    quoteTurnstileToken.value = ''
    quoteTurnstileRenderKey.value += 1
  }

  function resetLeadTurnstile() {
    leadTurnstileToken.value = ''
    leadTurnstileRenderKey.value += 1
  }

  function goToLeadStep() {
    resetLeadTurnstile()
    step.value = 4
  }

  function goToSchedule() {
    router.push('/agendar')
  }

  function resetAll() {
    step.value = 1
    selectedBrand.value = ''
    selectedModel.value = ''
    models.value = []
    faults.value = []
    selectedFaultIds.value = []
    quoteResult.value = null
    leadForm.value = { nombre: '', email: '', telefono: '' }
    acceptedDisclaimer.value = false
    quoteTurnstileToken.value = ''
    quoteTurnstileRenderKey.value = 0
    leadTurnstileToken.value = ''
    leadTurnstileRenderKey.value = 0
    leadSubmitted.value = false
    notFoundMode.value = false
    manualBrand.value = ''
    manualModel.value = ''
    error.value = ''
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
    onQuoteVerify,
    onLeadVerify,
    goToLeadStep,
    goToSchedule,
    resetAll,
    activateNotFoundMode,
    deactivateNotFoundMode,
  }
}
