<template>
  <main class="calc-page" id="timer-555-calculator">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Calculadora Timer 555</h1>
        <p>Astable, monostable y biestable con conexiones reales del CI 555.</p>
      </header>

      <div class="timer555-layout">
        <article class="timer555-panel">
          <header class="panel-header">
            <h2 class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Parametros
            </h2>

            <div class="panel-tabs" role="tablist" aria-label="Modo de funcionamiento">
              <button
                v-for="option in timer555ModeOptions"
                :key="option.value"
                type="button"
                class="panel-tab"
                :class="{ 'panel-tab--active': form.mode === option.value }"
                @click="form.mode = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </header>

          <div class="panel-form">
            <div class="form-grid">
              <div class="form-field" v-if="isAstable">
                <label>R1</label>
                <div class="unit-input">
                  <input v-model.number="form.r1_value" type="number" min="0" step="0.1" inputmode="decimal" />
                  <select v-model="form.r1_unit" class="unit-select">
                    <option value="ohm">Ω</option>
                    <option value="kohm">kΩ</option>
                    <option value="mohm">MΩ</option>
                  </select>
                </div>
              </div>

              <div class="form-field" v-if="isAstable">
                <label>R2</label>
                <div class="unit-input">
                  <input v-model.number="form.r2_value" type="number" min="0" step="0.1" inputmode="decimal" />
                  <select v-model="form.r2_unit" class="unit-select">
                    <option value="ohm">Ω</option>
                    <option value="kohm">kΩ</option>
                    <option value="mohm">MΩ</option>
                  </select>
                </div>
              </div>

              <div class="form-field" v-if="isMonostable">
                <label>R</label>
                <div class="unit-input">
                  <input v-model.number="form.r_value" type="number" min="0" step="0.1" inputmode="decimal" />
                  <select v-model="form.r_unit" class="unit-select">
                    <option value="ohm">Ω</option>
                    <option value="kohm">kΩ</option>
                    <option value="mohm">MΩ</option>
                  </select>
                </div>
              </div>

              <div class="form-field" v-if="!isBistable">
                <label>C</label>
                <div class="unit-input">
                  <input v-model.number="form.c_value" type="number" min="0" step="0.1" inputmode="decimal" />
                  <select v-model="form.c_unit" class="unit-select">
                    <option value="pf">pF</option>
                    <option value="nf">nF</option>
                    <option value="uf">µF</option>
                  </select>
                </div>
              </div>

              <div class="form-field">
                <label>Vcc (V)</label>
                <input
                  v-model.number="form.vcc_v"
                  type="number"
                  min="0"
                  step="0.1"
                  inputmode="decimal"
                  class="input-solo"
                  :disabled="isBistable"
                />
              </div>
            </div>

            <div class="mode-hint" v-if="isBistable">
              <i class="fa-solid fa-circle-info"></i>
              En biestable la salida se alterna por disparo SET/RESET. Vcc se fija en 5V para evitar inconsistencias.
            </div>

            <div class="form-actions">
              <button type="button" class="btn-reset" @click="reset">
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parametros
              </button>
            </div>

            <section class="pinout-card">
              <img src="/images/calculadoras/555_Pinout.webp" alt="Pinout NE555" class="pinout-image" />
            </section>
          </div>
        </article>

        <article class="timer555-panel output-panel output-panel--center">
          <header class="panel-header">
            <h2 class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Conexion real
            </h2>
          </header>

          <div class="output-body">
            <section class="circuit-card" aria-label="Circuito de referencia 555">
              <div class="diagram-stage">
                <img :src="activeDiagramSrc" :alt="activeDiagramAlt" class="diagram-image" />
                <span
                  class="diagram-led"
                  :class="{ 'diagram-led--on': outputBlinkOn }"
                  :style="pin3LedStyle"
                ></span>
              </div>
              <div class="circuit-label">{{ circuitLabel }}</div>
            </section>

            <section class="wave-card" aria-label="Previsualizacion de onda de salida">
              <svg class="wave-svg" viewBox="0 0 332 120" role="img" aria-label="Forma de onda de salida">
                <line x1="18" y1="18" x2="18" y2="102" class="wave-axis" />
                <line x1="18" y1="102" x2="316" y2="102" class="wave-axis" />

                <path v-if="isAstable" :d="`M22 90 H ${waveDutyX} V 34 H 278 V 90 H 310`" class="wave-path" />
                <path v-else-if="isMonostable" d="M22 90 H 98 V 34 H 192 V 90 H 310" class="wave-path" />
                <path
                  v-else
                  :d="bistableOutputWavePath"
                  :class="['wave-path', 'wave-path-output', { 'wave-path-output--high': bistableOutputHigh }]"
                />

                <text x="24" y="28" class="wave-label">{{ isBistable ? 'Salida (0V / 5V)' : 'Pulso' }}</text>
                <text x="284" y="112" class="wave-label">Tiempo</text>
              </svg>
            </section>
          </div>
        </article>

        <article class="timer555-panel output-panel output-panel--right">
          <header class="panel-header">
            <h2 class="panel-title">
              <i class="fa-solid fa-circle-info"></i>
              Modo y salida
            </h2>
          </header>

          <div class="output-body">
            <div class="output-values" v-if="!isBistable">
              <div class="value-row">
                <span>Frecuencia</span>
                <strong>{{ formattedFrequency }}</strong>
              </div>

              <div class="value-row" v-if="isAstable">
                <span>Tiempo alto</span>
                <strong>{{ formattedHigh }}</strong>
              </div>

              <div class="value-row" v-if="isAstable">
                <span>Tiempo bajo</span>
                <strong>{{ formattedLow }}</strong>
              </div>

              <div class="value-row" v-if="isAstable">
                <span>Ciclo de trabajo</span>
                <strong>{{ formattedDuty }}</strong>
              </div>

              <div class="value-row" v-if="isAstable">
                <span>Periodo</span>
                <strong>{{ formattedPeriod }}</strong>
              </div>

              <div class="value-row" v-if="isMonostable">
                <span>Duracion del pulso</span>
                <strong>{{ formattedPulse }}</strong>
              </div>
            </div>

            <div class="output-values" v-else>
              <section class="bistable-guide">
                <h3>Como usar modo biestable</h3>
                <p>1. Parte en RESET (salida en 0 V).</p>
                <p>2. Cada click en el pulsador envia un pulso y alterna <strong>SET / RESET</strong>.</p>
                <p>3. Pulso siguiente: <strong>{{ bistableNextPulseLabel }}</strong>.</p>
                <p>4. La salida en pin 3 queda memorizada en <strong>{{ bistableOutputHigh ? 'HIGH (5V)' : 'LOW (0V)' }}</strong>.</p>
                <p class="bistable-guide-note">No parpadea sola; cambia solo con SET o RESET.</p>
              </section>

              <div class="value-row">
                <span>SET</span>
                <strong>Pin 2 a nivel bajo</strong>
              </div>
              <div class="value-row">
                <span>RESET</span>
                <strong>Pin 4 a nivel bajo</strong>
              </div>
              <div class="value-row">
                <span>Salida (pin 3)</span>
                <strong>{{ bistableOutputHigh ? 'HIGH (5V)' : 'LOW (0V)' }}</strong>
              </div>

              <div class="bistable-controls">
                <button
                  type="button"
                  class="bistable-btn"
                  :class="{ 'bistable-btn--active': bistableStateLabel === 'SET' }"
                  disabled
                >Seleccionar SET</button>
                <button
                  type="button"
                  class="bistable-btn"
                  :class="{ 'bistable-btn--active': bistableStateLabel === 'RESET' }"
                  disabled
                >Seleccionar RESET</button>
              </div>

              <button
                type="button"
                class="push-trigger"
                :class="{ 'push-trigger--pressed': pushPressed }"
                @click="triggerBistablePulse"
              >
                <img src="/images/calculadoras/push.webp" alt="Pulsador virtual SET RESET" class="push-image" />
                <span class="push-text">
                  {{ `Presionar pulsador (pulso a ${bistableNextPulseLabel})` }}
                </span>
              </button>
            </div>

            <p class="output-hint">{{ resultSummary }}</p>
          </div>
        </article>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { timer555ModeOptions, useTimer555Calculator } from '@/composables/useTimer555Calculator'

const { form, isAstable, isMonostable, isBistable, result, reset } = useTimer555Calculator()
const bistableOutputHigh = ref(false)
const outputBlinkOn = ref(false)
const pushPressed = ref(false)

let blinkTimer = null
let pushTimer = null

function formatFrequency(value) {
  if (!Number.isFinite(value)) return '—'
  const abs = Math.abs(value)

  if (abs >= 1e6) return `${(value / 1e6).toFixed(3)} MHz`
  if (abs >= 1e3) return `${(value / 1e3).toFixed(3)} kHz`
  if (abs >= 1) return `${value.toFixed(3)} Hz`
  if (abs >= 1e-3) return `${(value * 1e3).toFixed(3)} mHz`
  if (abs === 0) return '0 Hz'
  return `${value.toExponential(3)} Hz`
}

function formatTime(value) {
  if (!Number.isFinite(value)) return '—'
  const abs = Math.abs(value)

  if (abs >= 1) return `${value.toFixed(3)} s`
  if (abs >= 1e-3) return `${(value * 1e3).toFixed(3)} ms`
  if (abs >= 1e-6) return `${(value * 1e6).toFixed(3)} µs`
  if (abs >= 1e-9) return `${(value * 1e9).toFixed(3)} ns`
  if (abs === 0) return '0 s'
  return `${value.toExponential(3)} s`
}

const formattedFrequency = computed(() =>
  result.value?.frequency_hz == null ? '—' : formatFrequency(result.value.frequency_hz)
)

const formattedHigh = computed(() =>
  result.value?.t_high_s == null ? '—' : formatTime(result.value.t_high_s)
)

const formattedLow = computed(() =>
  result.value?.t_low_s == null ? '—' : formatTime(result.value.t_low_s)
)

const formattedDuty = computed(() =>
  result.value?.duty_cycle == null ? '—' : `${(result.value.duty_cycle * 100).toFixed(2)} %`
)

const formattedPeriod = computed(() =>
  result.value?.period_s == null ? '—' : formatTime(result.value.period_s)
)

const formattedPulse = computed(() =>
  result.value?.period_s == null ? '—' : formatTime(result.value.period_s)
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

const pin3LedStyle = computed(() => {
  if (isAstable.value) {
    return { left: '80.09%', top: '44%' }
  }
  if (isMonostable.value) {
    return { left: '80.5%', top: '44.68%' }
  }
  return { left: '94.5%', top: '49.5%' }
})

const waveDutyX = computed(() => {
  const duty = result.value?.duty_cycle
  if (!Number.isFinite(duty)) return 150
  const clamped = Math.min(Math.max(duty, 0.08), 0.92)
  return Math.round(22 + clamped * 256)
})

const bistableOutputWavePath = computed(() =>
  bistableOutputHigh.value ? 'M22 44 H 310' : 'M22 90 H 310'
)

const bistableStateLabel = computed(() =>
  bistableOutputHigh.value ? 'SET' : 'RESET'
)

const bistableNextPulseLabel = computed(() =>
  bistableOutputHigh.value ? 'RESET' : 'SET'
)

function clampMs(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

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
</script>

<style scoped src="./commonCalculatorPage.css"></style>
<style scoped src="./Timer555Page.css"></style>
