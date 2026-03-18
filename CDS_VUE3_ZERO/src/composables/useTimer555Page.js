import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { timer555ModeOptions, useTimer555Calculator } from '@/composables/useTimer555Calculator'

function formatFrequency(value) {
  if (!Number.isFinite(value)) return '-'
  const abs = Math.abs(value)

  if (abs >= 1e6) return `${(value / 1e6).toFixed(3)} MHz`
  if (abs >= 1e3) return `${(value / 1e3).toFixed(3)} kHz`
  if (abs >= 1) return `${value.toFixed(3)} Hz`
  if (abs >= 1e-3) return `${(value * 1e3).toFixed(3)} mHz`
  if (abs === 0) return '0 Hz'
  return `${value.toExponential(3)} Hz`
}

function formatTime(value) {
  if (!Number.isFinite(value)) return '-'
  const abs = Math.abs(value)

  if (abs >= 1) return `${value.toFixed(3)} s`
  if (abs >= 1e-3) return `${(value * 1e3).toFixed(3)} ms`
  if (abs >= 1e-6) return `${(value * 1e6).toFixed(3)} µs`
  if (abs >= 1e-9) return `${(value * 1e9).toFixed(3)} ns`
  if (abs === 0) return '0 s'
  return `${value.toExponential(3)} s`
}

function clampMs(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

export function useTimer555Page() {
  const { form, isAstable, isMonostable, isBistable, result, reset } = useTimer555Calculator()
  const bistableOutputHigh = ref(false)
  const outputBlinkOn = ref(false)
  const pushPressed = ref(false)

  let blinkTimer = null
  let pushTimer = null

  const formattedFrequency = computed(() =>
    result.value?.frequency_hz == null ? '-' : formatFrequency(result.value.frequency_hz)
  )

  const formattedHigh = computed(() =>
    result.value?.t_high_s == null ? '-' : formatTime(result.value.t_high_s)
  )

  const formattedLow = computed(() =>
    result.value?.t_low_s == null ? '-' : formatTime(result.value.t_low_s)
  )

  const formattedDuty = computed(() =>
    result.value?.duty_cycle == null ? '-' : `${(result.value.duty_cycle * 100).toFixed(2)} %`
  )

  const formattedPeriod = computed(() =>
    result.value?.period_s == null ? '-' : formatTime(result.value.period_s)
  )

  const formattedPulse = computed(() =>
    result.value?.period_s == null ? '-' : formatTime(result.value.period_s)
  )

  const circuitLabel = computed(() => {
    if (isAstable.value) return '555 astable real'
    if (isMonostable.value) return '555 monostable real'
    return '555 biestable real'
  })

  const activeDiagramSrc = computed(() => {
    if (isAstable.value) return '/images/calculadoras/NE555_AS.webp'
    if (isMonostable.value) return '/images/calculadoras/NE555_MONO.webp'
    return '/images/calculadoras/NE555_BI.webp'
  })

  const activeDiagramAlt = computed(() => {
    if (isAstable.value) return 'Esquema real NE555 astable'
    if (isMonostable.value) return 'Esquema real NE555 monostable'
    return 'Esquema real NE555 biestable'
  })

  const diagramMode = computed(() => {
    if (isAstable.value) return 'astable'
    if (isMonostable.value) return 'monostable'
    return 'bistable'
  })

  const waveDutyX = computed(() => {
    const duty = result.value?.duty_cycle
    if (!Number.isFinite(duty)) return 150
    const clamped = Math.min(Math.max(duty, 0.08), 0.92)
    return Math.round(22 + clamped * 256)
  })

  const bistableOutputWavePath = computed(() => (
    bistableOutputHigh.value ? 'M22 44 H 310' : 'M22 90 H 310'
  ))

  const bistableStateLabel = computed(() => (
    bistableOutputHigh.value ? 'SET' : 'RESET'
  ))

  const bistableNextPulseLabel = computed(() => (
    bistableOutputHigh.value ? 'RESET' : 'SET'
  ))

  function clearBlinkTimer() {
    if (blinkTimer !== null) {
      window.clearTimeout(blinkTimer)
      blinkTimer = null
    }
  }

  function clearPushTimer() {
    if (pushTimer !== null) {
      window.clearTimeout(pushTimer)
      pushTimer = null
    }
  }

  function setBistableOutput(state) {
    bistableOutputHigh.value = state
    if (isBistable.value) {
      outputBlinkOn.value = state
      clearBlinkTimer()
    }
  }

  function triggerBistablePulse() {
    if (!isBistable.value) return

    const isSetPulse = !bistableOutputHigh.value

    setBistableOutput(isSetPulse)

    pushPressed.value = true
    clearPushTimer()
    pushTimer = window.setTimeout(() => {
      pushPressed.value = false
    }, 180)
  }

  function restartBlinkLoop() {
    clearBlinkTimer()

    if (isBistable.value) {
      outputBlinkOn.value = bistableOutputHigh.value
      return
    }

    if (!result.value) {
      outputBlinkOn.value = false
      return
    }

    let onMs = 900
    let offMs = 900

    if (isAstable.value && Number.isFinite(result.value.t_high_s) && Number.isFinite(result.value.t_low_s)) {
      onMs = clampMs(result.value.t_high_s * 1000, 90, 2200)
      offMs = clampMs(result.value.t_low_s * 1000, 90, 2200)
    } else if (Number.isFinite(result.value.period_s)) {
      onMs = clampMs(result.value.period_s * 1000, 150, 2000)
      offMs = clampMs(onMs * 1.1, 180, 2400)
    }

    outputBlinkOn.value = false

    const tick = () => {
      outputBlinkOn.value = !outputBlinkOn.value
      blinkTimer = window.setTimeout(tick, outputBlinkOn.value ? onMs : offMs)
    }

    tick()
  }

  const resultSummary = computed(() => {
    if (isBistable.value) {
      return `Modo biestable: salida pin 3 en ${bistableOutputHigh.value ? 'HIGH (5V)' : 'LOW (0V)'} · siguiente pulso: ${bistableNextPulseLabel.value}.`
    }

    if (!result.value) {
      return 'Define parametros validos para obtener resultados.'
    }

    if (isAstable.value) {
      return `Frecuencia: ${formattedFrequency.value} · Duty: ${formattedDuty.value}`
    }

    return `Pulso: ${formattedPulse.value} · Frecuencia equivalente: ${formattedFrequency.value}`
  })

  watch([() => form.mode, result], restartBlinkLoop, { immediate: true })

  watch(() => form.mode, (mode) => {
    if (mode !== 'bistable') {
      pushPressed.value = false
      clearPushTimer()
      return
    }

    form.vcc_v = 5
    pushPressed.value = false
    setBistableOutput(false)
  })

  watch(() => form.vcc_v, (value) => {
    if (isBistable.value && value !== 5) {
      form.vcc_v = 5
    }
  })

  watch(bistableOutputHigh, () => {
    if (isBistable.value) {
      outputBlinkOn.value = bistableOutputHigh.value
    }
  })

  onBeforeUnmount(() => {
    clearBlinkTimer()
    clearPushTimer()
  })

  return {
    activeDiagramAlt,
    activeDiagramSrc,
    bistableNextPulseLabel,
    bistableOutputHigh,
    bistableOutputWavePath,
    bistableStateLabel,
    circuitLabel,
    diagramMode,
    form,
    formattedDuty,
    formattedFrequency,
    formattedHigh,
    formattedLow,
    formattedPeriod,
    formattedPulse,
    isAstable,
    isBistable,
    isMonostable,
    outputBlinkOn,
    pushPressed,
    reset,
    resultSummary,
    timer555ModeOptions,
    triggerBistablePulse,
    waveDutyX,
  }
}
