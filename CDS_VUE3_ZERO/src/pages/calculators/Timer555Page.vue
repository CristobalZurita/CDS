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

<style scoped>
.calc-page {
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.1), transparent 35%),
    radial-gradient(circle at bottom right, rgba(3, 134, 0, 0.06), transparent 28%);
}

.calc-container {
  max-width: 1520px;
  margin: 0 auto;
  display: grid;
  gap: 1.5rem;
}

.calc-header h1 {
  margin: 0;
  font-size: var(--cds-text-3xl);
  line-height: var(--cds-leading-tight);
}

.calc-header p {
  margin: 0.4rem 0 0;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-base);
}

.timer555-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 960px) {
  .timer555-layout {
    grid-template-columns: minmax(350px, 1fr) minmax(420px, 1.4fr);
    align-items: start;
  }

  .output-panel--right {
    grid-column: 1 / -1;
  }
}

@media (min-width: 1280px) {
  .timer555-layout {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    align-items: stretch;
  }

  .output-panel--right {
    grid-column: auto;
  }

  .timer555-panel {
    height: 100%;
  }
}

.timer555-panel {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(233, 236, 230, 0.7));
  border: 1px solid rgba(62, 60, 56, 0.13);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.55rem;
  padding: 0.9rem 1.1rem;
  background: rgba(62, 60, 56, 0.05);
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
}

.panel-title {
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cds-dark);
}

.panel-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.32rem;
  width: 100%;
}

.panel-tab {
  padding: 0.34rem 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(62, 60, 56, 0.22);
  background: transparent;
  color: var(--cds-dark);
  font-size: 0.94rem;
  font-weight: var(--cds-font-semibold);
  text-align: center;
  white-space: nowrap;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.panel-tab:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}

.panel-tab--active,
.panel-tab--active:hover {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

.panel-form {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

.form-grid {
  display: grid;
  gap: 0.85rem;
}

.form-field {
  display: grid;
  gap: 0.3rem;
}

.form-field label {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-dark);
  letter-spacing: 0.02em;
}

.unit-input {
  display: grid;
  grid-template-columns: 1fr auto;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--cds-white);
  transition: border-color 0.15s;
}

.unit-input:focus-within {
  border-color: var(--cds-primary);
}

.unit-input input {
  border: none;
  outline: none;
  padding: 0.65rem 0.75rem;
  font-size: var(--cds-text-base);
  background: transparent;
  color: var(--cds-dark);
  min-width: 0;
}

.unit-select {
  border: none;
  border-left: 1.5px solid rgba(62, 60, 56, 0.15);
  outline: none;
  padding: 0 0.6rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  background: rgba(62, 60, 56, 0.04);
  color: var(--cds-dark);
  cursor: pointer;
}

.input-solo {
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  border-radius: 0.5rem;
  padding: 0.65rem 0.75rem;
  font-size: var(--cds-text-base);
  background: var(--cds-white);
  color: var(--cds-dark);
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s;
}

.input-solo:focus {
  border-color: var(--cds-primary);
}

.mode-hint {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  background: rgba(62, 60, 56, 0.05);
  border: 1px solid rgba(62, 60, 56, 0.12);
  border-radius: 0.5rem;
  padding: 0.52rem 0.7rem;
}

.form-actions {
  display: flex;
}

.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  border: 1.5px solid rgba(62, 60, 56, 0.25);
  background: transparent;
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.btn-reset:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}

.chip-card {
  border-radius: var(--cds-radius-md);
  background: rgba(62, 60, 56, 0.04);
  border: 1px solid rgba(62, 60, 56, 0.1);
  padding: 0.4rem;
}

.chip-svg {
  width: 100%;
  display: block;
}

.chip-body {
  fill: var(--cds-dark);
  stroke: color-mix(in srgb, var(--cds-dark) 88%, black);
  stroke-width: 2;
}

.chip-notch {
  fill: color-mix(in srgb, var(--cds-dark) 84%, black);
}

.chip-model {
  fill: var(--cds-white);
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 0.03em;
}

.pin-red {
  fill: #c9413a;
}

.pin-green {
  fill: #4f9f52;
}

.pin-blue {
  fill: #4d73b6;
}

.pin-label {
  fill: var(--cds-text-muted);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.pinout-card {
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  background: rgba(62, 60, 56, 0.04);
  border: 1px solid rgba(62, 60, 56, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 320px;
}

.pinout-image {
  width: 100%;
  max-width: none;
  transform: translateY(2px);
  display: block;
}

@media (max-width: 959px) {
  .pinout-card {
    min-height: 0;
  }

  .pinout-image {
    width: 100%;
    transform: none;
  }
}

.output-panel {
  display: flex;
  flex-direction: column;
}

.output-body {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 0.9rem;
  align-content: start;
  flex: 1;
}

.circuit-card {
  background: rgba(62, 60, 56, 0.04);
  border: 1px solid rgba(62, 60, 56, 0.1);
  border-radius: var(--cds-radius-md);
  overflow: hidden;
}

.diagram-stage {
  position: relative;
  isolation: isolate;
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
}

.diagram-image {
  width: 100%;
  display: block;
  background: color-mix(in srgb, var(--cds-white) 74%, transparent);
}

.diagram-led {
  position: absolute;
  z-index: 3;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  background: #8d887d;
  border: 1.6px solid color-mix(in srgb, var(--cds-dark) 75%, black);
  transition: background 0.12s ease, box-shadow 0.12s ease, opacity 0.12s ease;
  pointer-events: none;
  opacity: 0.55;
}

.diagram-led--on {
  background: var(--cds-primary);
  opacity: 1;
  animation: ledPulse 0.85s ease-in-out infinite alternate;
  box-shadow:
    0 0 0.35rem rgba(236, 107, 0, 0.62),
    0 0 0.8rem rgba(236, 107, 0, 0.45);
}

@keyframes ledPulse {
  from {
    box-shadow:
      0 0 0.22rem rgba(236, 107, 0, 0.5),
      0 0 0.5rem rgba(236, 107, 0, 0.3);
  }
  to {
    box-shadow:
      0 0 0.45rem rgba(236, 107, 0, 0.78),
      0 0 1.05rem rgba(236, 107, 0, 0.58);
  }
}

.circuit-label {
  padding: 0.45rem 0.75rem 0.65rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
}

.wave-card {
  border: 1px solid rgba(62, 60, 56, 0.1);
  border-radius: 0.55rem;
  background: rgba(62, 60, 56, 0.04);
  overflow: hidden;
}

.wave-svg {
  width: 100%;
  height: auto;
  display: block;
}

.wave-axis {
  stroke: color-mix(in srgb, var(--cds-dark) 60%, transparent);
  stroke-width: 1.8;
}

.wave-path {
  stroke: var(--cds-primary);
  stroke-width: 4;
  fill: none;
  stroke-linejoin: round;
  stroke-linecap: round;
}

.wave-path-output {
  stroke: color-mix(in srgb, var(--cds-dark) 80%, white);
  stroke-width: 3.2;
  transition: stroke 0.18s ease;
}

.wave-path-output--high {
  stroke: var(--cds-primary);
}

.wave-label {
  fill: var(--cds-text-muted);
  font-size: 12px;
  font-weight: 700;
}

.output-values {
  display: grid;
  gap: 0.5rem;
}

.bistable-guide {
  display: grid;
  gap: 0.25rem;
  margin-bottom: 0.25rem;
  padding: 0.7rem 0.8rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 26%, rgba(62, 60, 56, 0.18));
  border-radius: 0.55rem;
  background: color-mix(in srgb, var(--cds-primary) 7%, var(--cds-white));
}

.bistable-guide h3 {
  margin: 0;
  font-size: var(--cds-text-base);
  color: var(--cds-dark);
}

.bistable-guide p {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.bistable-guide strong {
  color: var(--cds-dark);
}

.bistable-guide-note {
  color: var(--cds-primary) !important;
  font-weight: var(--cds-font-semibold);
}

.bistable-controls {
  display: flex;
  gap: 0.45rem;
}

.bistable-btn {
  flex: 1;
  min-height: 38px;
  border-radius: 0.5rem;
  border: 1.5px solid rgba(62, 60, 56, 0.22);
  background: rgba(255, 255, 255, 0.88);
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: default;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.bistable-btn:not(:disabled):hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 7%, white);
}

.bistable-btn:disabled {
  opacity: 1;
}

.bistable-btn--active {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 10%, white);
}

.push-trigger {
  display: grid;
  justify-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.6rem;
  border-radius: 0.6rem;
  border: 1.5px solid rgba(62, 60, 56, 0.18);
  background: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  transition: border-color 0.15s, transform 0.12s, background 0.15s;
}

.push-trigger:hover {
  border-color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 6%, white);
}

.push-trigger--pressed {
  transform: translateY(1px) scale(0.992);
}

.push-image {
  width: min(160px, 100%);
  display: block;
  border-radius: 0.45rem;
}

.push-text {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  font-weight: var(--cds-font-semibold);
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  padding: 0.56rem 0.85rem;
  background: rgba(62, 60, 56, 0.04);
  border-radius: 0.45rem;
  border: 1px solid rgba(62, 60, 56, 0.08);
}

.value-row span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.value-row strong {
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-primary);
  text-align: right;
}

.output-hint {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-align: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.65rem 1rem;
  border: 1px solid color-mix(in srgb, var(--cds-primary) 35%, transparent);
  border-radius: 0.6rem;
  text-decoration: none;
  color: var(--cds-primary);
  font-weight: var(--cds-font-semibold);
  width: fit-content;
  font-size: var(--cds-text-sm);
  transition: background 0.15s;
}

.back-link:hover {
  background: color-mix(in srgb, var(--cds-primary) 8%, transparent);
}
</style>
