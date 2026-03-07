import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

export function useCotizadorIAPage() {
  const router = useRouter()

  const step = ref(1)
  const instrumentBrand = ref('')
  const instrumentModel = ref('')
  const diagnosticSummary = ref('')
  const acceptedDisclaimer = ref(false)
  const turnstileToken = ref('')

  const canContinueStep1 = computed(() => {
    return String(instrumentBrand.value || '').trim().length > 0 &&
      String(instrumentModel.value || '').trim().length > 0
  })

  const canContinueStep2 = computed(() => {
    return String(diagnosticSummary.value || '').trim().length >= 8
  })

  const canGenerate = computed(() => {
    return acceptedDisclaimer.value && String(turnstileToken.value || '').length > 0
  })

  const quotationRange = computed(() => '$20.000 CLP - valor referencial inicial')

  function onVerify(token) {
    turnstileToken.value = token
  }

  function resetAll() {
    instrumentBrand.value = ''
    instrumentModel.value = ''
    diagnosticSummary.value = ''
    acceptedDisclaimer.value = false
    turnstileToken.value = ''
    step.value = 1
  }

  function goToSchedule() {
    router.push('/agendar')
  }

  return {
    step,
    instrumentBrand,
    instrumentModel,
    diagnosticSummary,
    acceptedDisclaimer,
    turnstileToken,
    canContinueStep1,
    canContinueStep2,
    canGenerate,
    quotationRange,
    onVerify,
    resetAll,
    goToSchedule
  }
}
