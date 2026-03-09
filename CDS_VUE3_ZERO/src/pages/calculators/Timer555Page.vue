<template>
  <main class="calc-page" id="timer-555-calculator">
    <section class="calc-container">

      <header class="calc-header">
        <h1>Calculadora Timer 555</h1>
        <p>Modo astable y monostable — calcula frecuencia y tiempos en tiempo real.</p>
      </header>

      <div class="timer555-layout">

        <!-- ── Panel izquierdo: parámetros ── -->
        <div class="timer555-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i> Parámetros
            </div>
            <div class="panel-tabs">
              <button
                v-for="option in timer555ModeOptions"
                :key="option.value"
                type="button"
                class="panel-tab"
                :class="{ 'panel-tab--active': form.mode === option.value }"
                @click="form.mode = option.value"
              >{{ option.label }}</button>
            </div>
          </div>

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

              <div class="form-field">
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
                <input v-model.number="form.vcc_v" type="number" min="0" step="0.1" inputmode="decimal" class="input-solo" />
              </div>

            </div>

            <div class="form-actions">
              <button type="button" class="btn-reset" @click="reset">
                <i class="fa-solid fa-rotate-left"></i> Resetear parámetros
              </button>
            </div>

            <div class="pinout-card">
              <img
                src="/images/calculadoras/555_Pinout.webp"
                alt="Pinout NE555"
                class="pinout-image"
              />
            </div>
          </div>
        </div>

        <!-- ── Panel derecho: resultado ── -->
        <div class="timer555-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i> Resultado
            </div>
          </div>

          <div class="output-body">
            <div class="circuit-card">
              <canvas
                ref="canvasRef"
                class="circuit-canvas"
                width="420"
                height="260"
              />
              <div class="circuit-label">{{ circuitLabel }}</div>
            </div>

            <div class="output-values">
              <div class="value-row">
                <span>Frecuencia</span>
                <strong>{{ formattedFrequency }}</strong>
              </div>
              <div class="value-row">
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
              <div class="value-row">
                <span>Periodo</span>
                <strong>{{ formattedPeriod }}</strong>
              </div>
            </div>

            <p class="output-hint">
              Los valores se calculan en tiempo real al cambiar los parámetros.
            </p>
          </div>
        </div>

      </div>

      <router-link to="/calculadoras" class="back-link">
        ← Volver a calculadoras
      </router-link>

    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { timer555ModeOptions, useTimer555Calculator } from '@/composables/useTimer555Calculator'

const { form, isAstable, isMonostable, result, reset } = useTimer555Calculator()

// ── Valores formateados ──────────────────────────────────────────────────────

const formattedFrequency = computed(() => {
  if (!result.value || result.value.frequency_hz == null) return '—'
  return `${result.value.frequency_hz.toFixed(3)} Hz`
})

const formattedHigh = computed(() => {
  if (!result.value || result.value.t_high_s == null) return '—'
  return `${(result.value.t_high_s * 1000).toFixed(3)} ms`
})

const formattedLow = computed(() => {
  if (!result.value || result.value.t_low_s == null) return '—'
  return `${(result.value.t_low_s * 1000).toFixed(3)} ms`
})

const formattedDuty = computed(() => {
  if (!result.value || result.value.duty_cycle == null) return '—'
  return `${(result.value.duty_cycle * 100).toFixed(2)} %`
})

const formattedPeriod = computed(() => {
  if (!result.value || result.value.period_s == null) return '—'
  return `${(result.value.period_s * 1000).toFixed(3)} ms`
})

const circuitLabel = computed(() =>
  isAstable.value ? 'Oscilador astable' : 'Pulso monostable'
)

// ── Canvas animado ───────────────────────────────────────────────────────────

const canvasRef = ref(null)
let blinkTimer = null
let ledOn = false

function getCanvasPalette() {
  if (typeof window === 'undefined') {
    return {
      panelFill: 'transparent', stroke: 'transparent', chipFill: 'transparent',
      chipText: 'transparent', ledOn: 'transparent', ledOff: 'transparent', ledGlow: 'transparent'
    }
  }
  const el = document.getElementById('timer-555-calculator')
  const s = el ? getComputedStyle(el) : null
  const r = (name) => s?.getPropertyValue(name).trim() || 'transparent'
  return {
    panelFill: r('--t555-panel-fill'),
    stroke:    r('--t555-stroke'),
    chipFill:  r('--t555-chip-fill'),
    chipText:  r('--t555-chip-text'),
    ledOn:     r('--t555-led-on'),
    ledOff:    r('--t555-led-off'),
    ledGlow:   r('--t555-led-glow'),
  }
}

function clampMs(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function getBlinkDurations() {
  if (!result.value) return { onMs: 500, offMs: 500 }
  if (isAstable.value && result.value.t_high_s && result.value.t_low_s) {
    return {
      onMs:  clampMs(result.value.t_high_s  * 1000, 80, 2500),
      offMs: clampMs(result.value.t_low_s * 1000, 80, 2500),
    }
  }
  if (result.value.period_s) {
    const onMs = clampMs(result.value.period_s * 1000, 120, 2000)
    return { onMs, offMs: clampMs(onMs * 1.2, 180, 2600) }
  }
  return { onMs: 500, offMs: 500 }
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

function drawChip(ctx, x, y, w, h, p) {
  ctx.fillStyle = p.chipFill
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  roundRect(ctx, x, y, w, h, 8)
  ctx.fill()
  ctx.stroke()
  ctx.fillStyle = p.chipText
  ctx.font = 'bold 16px sans-serif'
  ctx.fillText('555', x + 24, y + 50)
}

function drawResistor(ctx, x, y, length, vertical, p) {
  const steps = 6
  const amplitude = 6
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  if (vertical) {
    ctx.moveTo(x, y)
    for (let i = 0; i < steps; i++) {
      const dir = i % 2 === 0 ? amplitude : -amplitude
      ctx.lineTo(x + dir, y + (length / steps) * (i + 1))
    }
  } else {
    ctx.moveTo(x, y)
    for (let i = 0; i < steps; i++) {
      const dir = i % 2 === 0 ? amplitude : -amplitude
      ctx.lineTo(x + (length / steps) * (i + 1), y + dir)
    }
  }
  ctx.stroke()
}

function drawCap(ctx, x, y, p) {
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x - 10, y)
  ctx.lineTo(x + 10, y)
  ctx.moveTo(x - 10, y + 8)
  ctx.lineTo(x + 10, y + 8)
  ctx.stroke()
}

function drawSwitch(ctx, x, y, p) {
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + 18, y - 8)
  ctx.moveTo(x, y)
  ctx.lineTo(x, y + 16)
  ctx.stroke()
}

function drawLed(ctx, x, y, on, p) {
  ctx.fillStyle = on ? p.ledOn : p.ledOff
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.arc(x, y, 8, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  if (on) {
    ctx.strokeStyle = p.ledGlow
    ctx.lineWidth = 4
    ctx.beginPath()
    ctx.arc(x, y, 14, 0, Math.PI * 2)
    ctx.stroke()
  }
}

function drawCircuit() {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const p = getCanvasPalette()

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  ctx.fillStyle = p.panelFill
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  roundRect(ctx, 8, 8, canvas.width - 16, canvas.height - 16, 18)
  ctx.fill()
  ctx.stroke()

  const topY = 40
  const bottomY = 220
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(40, topY)
  ctx.lineTo(380, topY)
  ctx.moveTo(40, bottomY)
  ctx.lineTo(380, bottomY)
  ctx.stroke()

  ctx.font = '14px sans-serif'
  ctx.fillStyle = p.stroke
  ctx.fillText('Vcc', 48, topY - 12)
  ctx.fillText('Gnd', 48, bottomY + 10)

  drawChip(ctx, 170, 90, 80, 90, p)

  if (isAstable.value) {
    drawResistor(ctx, 110, 55, 55, true, p)
    ctx.fillText('R1', 94, 80)
    drawResistor(ctx, 110, 120, 55, true, p)
    ctx.fillText('R2', 94, 145)
    drawCap(ctx, 110, 185, p)
    ctx.fillText('C1', 94, 200)
    ctx.beginPath()
    ctx.moveTo(110, topY)
    ctx.lineTo(110, 55)
    ctx.lineTo(110, 175)
    ctx.lineTo(110, bottomY)
    ctx.stroke()
  } else {
    drawResistor(ctx, 95, 80, 50, true, p)
    ctx.fillText('R', 80, 105)
    drawCap(ctx, 140, 185, p)
    ctx.fillText('C', 126, 200)
    drawSwitch(ctx, 70, 160, p)
    ctx.beginPath()
    ctx.moveTo(95, topY)
    ctx.lineTo(95, 80)
    ctx.lineTo(95, 130)
    ctx.lineTo(140, 130)
    ctx.lineTo(140, 175)
    ctx.lineTo(140, bottomY)
    ctx.stroke()
  }

  drawResistor(ctx, 300, 120, 40, true, p)
  ctx.fillText('RL', 286, 140)
  drawLed(ctx, 320, 190, ledOn, p)
  ctx.beginPath()
  ctx.moveTo(250, 135)
  ctx.lineTo(300, 135)
  ctx.lineTo(300, 160)
  ctx.lineTo(320, 160)
  ctx.lineTo(320, 185)
  ctx.moveTo(320, 195)
  ctx.lineTo(320, bottomY)
  ctx.stroke()
}

function stopBlink() {
  if (blinkTimer !== null) {
    window.clearTimeout(blinkTimer)
    blinkTimer = null
  }
}

function startBlink() {
  stopBlink()
  const { onMs, offMs } = getBlinkDurations()
  ledOn = false
  const tick = () => {
    ledOn = !ledOn
    drawCircuit()
    blinkTimer = window.setTimeout(tick, ledOn ? onMs : offMs)
  }
  tick()
}

onMounted(() => {
  drawCircuit()
  startBlink()
})

onBeforeUnmount(() => {
  stopBlink()
})

watch([result, () => form.mode], () => {
  startBlink()
})
</script>

<style scoped>
/* ── Paleta del canvas ─────────────────────────────────────────── */
.calc-page {
  --t555-panel-fill: rgba(245, 243, 238, 0.85);
  --t555-stroke:     #3e3c38;
  --t555-chip-fill:  #3e3c38;
  --t555-chip-text:  #ffffff;
  --t555-led-on:     #ec6b00;
  --t555-led-off:    #c4c0b4;
  --t555-led-glow:   rgba(236, 107, 0, 0.4);
}

/* ── Página ────────────────────────────────────────────────────── */
.calc-page {
  padding: var(--cds-space-xl) var(--cds-space-md) var(--cds-space-2xl);
  background:
    radial-gradient(circle at top left, rgba(236, 107, 0, 0.1), transparent 35%),
    radial-gradient(circle at bottom right, rgba(3, 134, 0, 0.06), transparent 28%);
}

.calc-container {
  max-width: 1100px;
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

/* ── Layout 2 columnas ─────────────────────────────────────────── */
.timer555-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 900px) {
  .timer555-layout {
    grid-template-columns: minmax(320px, 1fr) minmax(380px, 1.4fr);
    align-items: start;
  }
}

/* ── Panel ─────────────────────────────────────────────────────── */
.timer555-panel {
  background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(233,236,230,0.7));
  border: 1px solid rgba(62,60,56,0.13);
  border-radius: var(--cds-radius-lg);
  box-shadow: var(--cds-shadow-sm);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.85rem 1.1rem;
  background: rgba(62,60,56,0.05);
  border-bottom: 1px solid rgba(62,60,56,0.1);
}

.panel-title {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--cds-dark);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

/* ── Tabs de modo ──────────────────────────────────────────────── */
.panel-tabs {
  display: flex;
  gap: 0.3rem;
}

.panel-tab {
  padding: 0.3rem 0.85rem;
  border-radius: 999px;
  border: 1px solid rgba(62,60,56,0.22);
  background: transparent;
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.panel-tab:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}

.panel-tab--active {
  background: var(--cds-primary);
  border-color: var(--cds-primary);
  color: var(--cds-white);
}

/* ── Formulario ────────────────────────────────────────────────── */
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
  gap: 0;
  border: 1.5px solid rgba(62,60,56,0.25);
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
  border-left: 1.5px solid rgba(62,60,56,0.15);
  outline: none;
  padding: 0 0.6rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  background: rgba(62,60,56,0.04);
  color: var(--cds-dark);
  cursor: pointer;
}

.input-solo {
  border: 1.5px solid rgba(62,60,56,0.25);
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

.form-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  border: 1.5px solid rgba(62,60,56,0.25);
  background: transparent;
  color: var(--cds-dark);
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.btn-reset:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
}

/* ── Pinout ────────────────────────────────────────────────────── */
.pinout-card {
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  background: rgba(62,60,56,0.04);
  border: 1px solid rgba(62,60,56,0.1);
}

.pinout-image {
  width: 100%;
  display: block;
}

/* ── Output panel ──────────────────────────────────────────────── */
.output-panel {
  display: flex;
  flex-direction: column;
}

.output-body {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

/* ── Canvas ────────────────────────────────────────────────────── */
.circuit-card {
  background: rgba(62,60,56,0.04);
  border: 1px solid rgba(62,60,56,0.1);
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  text-align: center;
}

.circuit-canvas {
  display: block;
  width: 100%;
  max-width: 420px;
  height: auto;
  margin: 0 auto;
}

.circuit-label {
  padding: 0.4rem 0.75rem 0.6rem;
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ── Valores ───────────────────────────────────────────────────── */
.output-values {
  display: grid;
  gap: 0.5rem;
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0.85rem;
  background: rgba(62,60,56,0.04);
  border-radius: 0.45rem;
  border: 1px solid rgba(62,60,56,0.08);
}

.value-row span {
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
}

.value-row strong {
  font-size: var(--cds-text-base);
  font-weight: var(--cds-font-semibold);
  color: var(--cds-primary);
}

.output-hint {
  margin: 0;
  font-size: var(--cds-text-sm);
  color: var(--cds-text-muted);
  text-align: center;
}

/* ── Back link ─────────────────────────────────────────────────── */
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
