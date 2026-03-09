<template>
  <main class="calc-page" id="cd40106-calculator">
    <section class="calc-container">
      <header class="calc-header">
        <h1>Oscilador CD40106</h1>
        <p>Schmitt trigger con R y C para estimar frecuencia y periodo.</p>
      </header>

      <div class="cd40106-layout">
        <section class="cd40106-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Parámetros
            </div>
          </div>

          <div class="panel-form">
            <div class="form-grid">
              <div class="form-field">
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
                <i class="fa-solid fa-rotate-left"></i>
                Resetear parámetros
              </button>
            </div>

            <div class="pinout-card">
              <img src="/images/calculadoras/CD40106.webp" alt="Pinout CD40106" class="pinout-image" />
            </div>
          </div>
        </section>

        <section class="cd40106-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Resultado
            </div>
          </div>

          <div class="output-body">
            <div class="circuit-card">
              <canvas ref="canvasRef" class="circuit-canvas" width="420" height="260" />
              <div class="circuit-label">Oscilador Schmitt</div>
            </div>

            <div class="output-values">
              <div class="value-row">
                <span>Frecuencia</span>
                <strong>{{ formattedFrequency }}</strong>
              </div>
              <div class="value-row">
                <span>Periodo</span>
                <strong>{{ formattedPeriod }}</strong>
              </div>
            </div>

            <p class="output-hint">La frecuencia es aproximada y cambia al ajustar R y C.</p>
          </div>
        </section>
      </div>

      <router-link to="/calculadoras" class="back-link">← Volver a calculadoras</router-link>
    </section>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const form = reactive({
  r_value: 100,
  r_unit: 'kohm',
  c_value: 0.1,
  c_unit: 'uf',
  vcc_v: 9,
})

const canvasRef = ref(null)
let blinkTimer = null
let ledOn = false

function resistanceFactor(unit) {
  if (unit === 'ohm') return 1
  if (unit === 'kohm') return 1000
  if (unit === 'mohm') return 1000000
  return 1
}

function capacitanceFactor(unit) {
  if (unit === 'pf') return 1e-12
  if (unit === 'nf') return 1e-9
  if (unit === 'uf') return 1e-6
  return 1e-6
}

const frequencyHz = computed(() => {
  const r = Number(form.r_value) * resistanceFactor(form.r_unit)
  const c = Number(form.c_value) * capacitanceFactor(form.c_unit)
  if (!Number.isFinite(r) || !Number.isFinite(c) || r <= 0 || c <= 0) return 0
  return 1 / (1.2 * r * c)
})

const periodMs = computed(() => {
  if (!frequencyHz.value) return 0
  return 1000 / frequencyHz.value
})

const formattedFrequency = computed(() => {
  if (!frequencyHz.value) return '—'
  return `${frequencyHz.value.toFixed(3)} Hz`
})

const formattedPeriod = computed(() => {
  if (!periodMs.value) return '—'
  return `${periodMs.value.toFixed(3)} ms`
})

function reset() {
  form.r_value = 100
  form.r_unit = 'kohm'
  form.c_value = 0.1
  form.c_unit = 'uf'
  form.vcc_v = 9
}

function clampMs(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function getBlinkDurations() {
  const base = periodMs.value || 800
  return {
    onMs: clampMs(base * 0.5, 80, 2500),
    offMs: clampMs(base * 0.5, 80, 2500),
  }
}

function getCanvasPalette() {
  if (typeof window === 'undefined') {
    return {
      panelFill: 'transparent',
      stroke: 'transparent',
      chipFill: 'transparent',
      chipText: 'transparent',
      ledOn: 'transparent',
      ledOff: 'transparent',
      ledGlow: 'transparent',
    }
  }
  const root = document.getElementById('cd40106-calculator')
  const styles = root ? getComputedStyle(root) : null
  const read = (name) => styles?.getPropertyValue(name).trim() || 'transparent'
  return {
    panelFill: read('--smd-panel-fill'),
    stroke: read('--smd-stroke'),
    chipFill: read('--smd-chip-fill'),
    chipText: read('--smd-chip-text'),
    ledOn: read('--smd-led-on'),
    ledOff: read('--smd-led-off'),
    ledGlow: read('--smd-led-glow'),
  }
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

function drawGate(ctx, x, y, w, h, p) {
  ctx.fillStyle = p.chipFill
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + w, y + h / 2)
  ctx.lineTo(x, y + h)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.fillStyle = p.chipText
  ctx.beginPath()
  ctx.arc(x + w + 6, y + h / 2, 6, 0, Math.PI * 2)
  ctx.fill()
}

function drawResistor(ctx, x, y, length, vertical, p) {
  const steps = 6
  const amplitude = 6
  ctx.strokeStyle = p.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  if (vertical) {
    ctx.moveTo(x, y)
    for (let i = 0; i < steps; i += 1) {
      const dir = i % 2 === 0 ? amplitude : -amplitude
      ctx.lineTo(x + dir, y + (length / steps) * (i + 1))
    }
  } else {
    ctx.moveTo(x, y)
    for (let i = 0; i < steps; i += 1) {
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

  drawGate(ctx, 200, 90, 70, 70, p)

  drawResistor(ctx, 130, 60, 50, true, p)
  ctx.fillText('R', 118, 85)

  drawCap(ctx, 130, 180, p)
  ctx.fillText('C', 118, 195)

  ctx.beginPath()
  ctx.moveTo(130, topY)
  ctx.lineTo(130, 60)
  ctx.lineTo(130, 180)
  ctx.lineTo(130, bottomY)
  ctx.stroke()

  drawLed(ctx, 320, 150, ledOn, p)
  ctx.beginPath()
  ctx.moveTo(270, 125)
  ctx.lineTo(320, 125)
  ctx.lineTo(320, 142)
  ctx.moveTo(320, 158)
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

watch([
  frequencyHz,
  () => form.r_value,
  () => form.r_unit,
  () => form.c_value,
  () => form.c_unit,
], () => {
  startBlink()
})
</script>

<style scoped>
.calc-page {
  --smd-panel-fill: rgba(245, 243, 238, 0.85);
  --smd-stroke: #3e3c38;
  --smd-chip-fill: #3e3c38;
  --smd-chip-text: #ffffff;
  --smd-led-on: #ec6b00;
  --smd-led-off: #c4c0b4;
  --smd-led-glow: rgba(236, 107, 0, 0.4);

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

.cd40106-layout {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 900px) {
  .cd40106-layout {
    grid-template-columns: minmax(320px, 1fr) minmax(380px, 1.4fr);
    align-items: start;
  }
}

.cd40106-panel {
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
  gap: 0.5rem;
  padding: 0.85rem 1.1rem;
  background: rgba(62, 60, 56, 0.05);
  border-bottom: 1px solid rgba(62, 60, 56, 0.1);
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
}

.input-solo:focus {
  border-color: var(--cds-primary);
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
}

.pinout-card {
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  background: rgba(62, 60, 56, 0.04);
  border: 1px solid rgba(62, 60, 56, 0.1);
}

.pinout-image {
  width: 100%;
  display: block;
}

.output-panel {
  display: flex;
  flex-direction: column;
}

.output-body {
  padding: 1rem 1.1rem 1.25rem;
  display: grid;
  gap: 1rem;
}

.circuit-card {
  background: rgba(62, 60, 56, 0.04);
  border: 1px solid rgba(62, 60, 56, 0.1);
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

.output-values {
  display: grid;
  gap: 0.5rem;
}

.value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0.85rem;
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
}
</style>
