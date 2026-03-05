<template>
  <PageSection variant="default" id="timer-555-calculator">
    <PageSectionHeader
      title="*Calculadora* Timer 555"
      subtitle="Astable y monostable con valores rapidos para R y C"
    />

    <PageSectionContent>
      <div class="timer555-layout">
        <div class="timer555-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Parametros
            </div>
            <div class="panel-tabs">
              <button
                v-for="option in modeOptions"
                :key="option.value"
                type="button"
                class="panel-tab"
                :class="{ active: form.mode === option.value }"
                @click="form.mode = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>

          <form class="panel-form" @submit.prevent="onCalculate">
            <div class="form-grid">
              <div class="form-field" v-if="isAstable">
                <label>R1</label>
                <div class="unit-input">
                  <input v-model.number="form.r1_value" type="number" min="0" step="0.1" />
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
                  <input v-model.number="form.r2_value" type="number" min="0" step="0.1" />
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
                  <input v-model.number="form.r_value" type="number" min="0" step="0.1" />
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
                  <input v-model.number="form.c_value" type="number" min="0" step="0.1" />
                  <select v-model="form.c_unit" class="unit-select">
                    <option value="pf">pF</option>
                    <option value="nf">nF</option>
                    <option value="uf">µF</option>
                  </select>
                </div>
              </div>
              <div class="form-field">
                <label>Vcc (V)</label>
                <input v-model.number="form.vcc_v" type="number" min="0" step="0.1" />
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-primary-action">
                Calcular
              </button>
              <button type="button" class="btn-secondary-action" @click="reset">
                Limpiar
              </button>
            </div>

            <div class="pinout-card">
              <img
                src="/images/calculadoras/555_Pinout.webp"
                alt="Pinout NE555"
                class="pinout-image"
              />
            </div>
          </form>
        </div>

        <div class="timer555-panel output-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-wave-square"></i>
              Resultado
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
                <span>Ciclo</span>
                <strong>{{ formattedDuty }}</strong>
              </div>
              <div class="value-row">
                <span>Periodo</span>
                <strong>{{ formattedPeriod }}</strong>
              </div>
            </div>

            <div class="output-hint">
              Ajusta valores y presiona calcular para obtener el resultado.
            </div>
          </div>
        </div>
      </div>

      <div class="timer555-back">
        <Link url="/calculadoras">
          <span class="timer555-back-link">← VOLVER A CALCULADORAS</span>
        </Link>
      </div>
    </PageSectionContent>
  </PageSection>

  <WorkshopFooter />
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import PageSection from '/src/vue/components/layout/PageSection.vue'
import PageSectionHeader from '/src/vue/components/layout/PageSectionHeader.vue'
import PageSectionContent from '/src/vue/components/layout/PageSectionContent.vue'
import Link from '/src/vue/components/generic/Link.vue'
import WorkshopFooter from '/src/vue/components/footer/WorkshopFooter.vue'
import { useCalculator } from '@/composables/useCalculator'
import { Timer555Input, Timer555Output } from '@/domain/timer555/contract'
import { calculateTimer555 } from '@/domain/timer555/model'
import { createValidationResult } from '@/validation'
import { validateCapacitance, validateResistance, validateVoltage } from '@/validation/physical'

const modeOptions = [
  { label: 'Astable', value: 'astable' },
  { label: 'Monostable', value: 'monostable' }
]

const form = reactive({
  mode: 'astable',
  r1_value: 1,
  r1_unit: 'kohm',
  r2_value: 330,
  r2_unit: 'kohm',
  r_value: 1,
  r_unit: 'kohm',
  c_value: 2.2,
  c_unit: 'uf',
  vcc_v: 5
})

const isAstable = computed(() => form.mode === 'astable')
const isMonostable = computed(() => form.mode === 'monostable')

function toInput(): Timer555Input {
  const resistanceFactor = (unit: string) => {
    if (unit === 'ohm') return 1
    if (unit === 'kohm') return 1000
    if (unit === 'mohm') return 1_000_000
    return 1
  }

  const capacitanceFactor = (unit: string) => {
    if (unit === 'pf') return 1e-12
    if (unit === 'nf') return 1e-9
    if (unit === 'uf') return 1e-6
    return 1e-6
  }

  if (form.mode === 'astable') {
    return {
      mode: 'astable_standard',
      R1_ohm: form.r1_value * resistanceFactor(form.r1_unit),
      R2_ohm: form.r2_value * resistanceFactor(form.r2_unit),
      C_farad: form.c_value * capacitanceFactor(form.c_unit),
      Vcc_volt: form.vcc_v
    }
  }

  return {
    mode: 'monostable',
    R_ohm: form.r_value * resistanceFactor(form.r_unit),
    C_farad: form.c_value * capacitanceFactor(form.c_unit),
    Vcc_volt: form.vcc_v
  }
}

function validator(i: Timer555Input) {
  const result = createValidationResult()

  if (i.C_farad !== undefined) {
    const e = validateCapacitance(i.C_farad)
    if (e) result.errors.push(e)
  }

  if (i.Vcc_volt !== undefined) {
    const e = validateVoltage(i.Vcc_volt)
    if (e) result.errors.push(e)
  }

  if (i.mode === 'monostable' && i.R_ohm !== undefined) {
    const e = validateResistance(i.R_ohm)
    if (e) result.errors.push(e)
  }

  if (i.mode === 'astable_standard') {
    if (i.R1_ohm !== undefined) {
      const e = validateResistance(i.R1_ohm)
      if (e) result.errors.push(e)
    }
    if (i.R2_ohm !== undefined) {
      const e = validateResistance(i.R2_ohm)
      if (e) result.errors.push(e)
    }
  }

  if (result.errors.length > 0) {
    result.valid = false
  }

  return result
}

const { result, calculate } = useCalculator(validator, calculateTimer555)

const resultValue = computed(() =>
  result.value?.state === 'OK' ? (result.value.value as Timer555Output) : null
)

const canvasRef = ref<HTMLCanvasElement | null>(null)
let blinkTimer: number | null = null
let ledOn = false

const circuitLabel = computed(() =>
  isAstable.value ? 'Oscilador astable' : 'Pulso monostable'
)

const formattedFrequency = computed(() => {
  if (!resultValue.value || !resultValue.value.frequency_hz) return '---'
  return `${resultValue.value.frequency_hz.toFixed(3)} Hz`
})

const formattedHigh = computed(() => {
  if (!resultValue.value || !resultValue.value.t_high_s) return '---'
  return `${(resultValue.value.t_high_s * 1000).toFixed(3)} ms`
})

const formattedLow = computed(() => {
  if (!resultValue.value || !resultValue.value.t_low_s) return '---'
  return `${(resultValue.value.t_low_s * 1000).toFixed(3)} ms`
})

const formattedDuty = computed(() => {
  if (!resultValue.value || !resultValue.value.duty_cycle) return '---'
  return `${(resultValue.value.duty_cycle * 100).toFixed(2)} %`
})

const formattedPeriod = computed(() => {
  if (!resultValue.value || !resultValue.value.period_s) return '---'
  return `${(resultValue.value.period_s * 1000).toFixed(3)} ms`
})

function onCalculate() {
  calculate(toInput())
}

function reset() {
  form.mode = 'astable'
  form.r1_value = 1
  form.r1_unit = 'kohm'
  form.r2_value = 330
  form.r2_unit = 'kohm'
  form.r_value = 1
  form.r_unit = 'kohm'
  form.c_value = 2.2
  form.c_unit = 'uf'
  form.vcc_v = 5
  result.value = null
}

const clampMs = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max)

const getCanvasPalette = () => {
  if (typeof window === 'undefined') {
    return {
      panelFill: 'transparent',
      stroke: 'transparent',
      chipFill: 'transparent',
      chipText: 'transparent',
      ledOn: 'transparent',
      ledOff: 'transparent',
      ledGlow: 'transparent'
    }
  }
  const root = document.getElementById('timer-555-calculator')
  const styles = root ? getComputedStyle(root) : null
  const read = (name: string) => (styles?.getPropertyValue(name).trim() || 'transparent')
  return {
    panelFill: read('--timer555-panel-fill'),
    stroke: read('--timer555-stroke'),
    chipFill: read('--timer555-chip-fill'),
    chipText: read('--timer555-chip-text'),
    ledOn: read('--timer555-led-on'),
    ledOff: read('--timer555-led-off'),
    ledGlow: read('--timer555-led-glow')
  }
}

const getBlinkDurations = () => {
  if (!resultValue.value) {
    return { onMs: 500, offMs: 500 }
  }

  if (isAstable.value && resultValue.value.t_high_s && resultValue.value.t_low_s) {
    const onMs = clampMs(resultValue.value.t_high_s * 1000, 80, 2500)
    const offMs = clampMs(resultValue.value.t_low_s * 1000, 80, 2500)
    return { onMs, offMs }
  }

  if (resultValue.value.period_s) {
    const onMs = clampMs(resultValue.value.period_s * 1000, 120, 2000)
    return { onMs, offMs: clampMs(onMs * 1.2, 180, 2600) }
  }

  return { onMs: 500, offMs: 500 }
}

const drawCircuit = () => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const palette = getCanvasPalette()

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  ctx.fillStyle = palette.panelFill
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  roundRect(ctx, 8, 8, canvas.width - 16, canvas.height - 16, 18)
  ctx.fill()
  ctx.stroke()

  const topY = 40
  const bottomY = 220
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(40, topY)
  ctx.lineTo(380, topY)
  ctx.moveTo(40, bottomY)
  ctx.lineTo(380, bottomY)
  ctx.stroke()

  ctx.font = '14px "Cervo Neue", sans-serif'
  ctx.fillStyle = palette.stroke
  ctx.fillText('Vcc', 48, topY - 12)
  ctx.fillText('Gnd', 48, bottomY + 10)

  drawChip(ctx, 170, 90, 80, 90, palette)

  if (isAstable.value) {
    drawResistor(ctx, 110, 55, 55, true, palette)
    ctx.fillText('R1', 94, 80)
    drawResistor(ctx, 110, 120, 55, true, palette)
    ctx.fillText('R2', 94, 145)
    drawCap(ctx, 110, 185, palette)
    ctx.fillText('C1', 94, 200)
    ctx.beginPath()
    ctx.moveTo(110, topY)
    ctx.lineTo(110, 55)
    ctx.lineTo(110, 175)
    ctx.lineTo(110, bottomY)
    ctx.stroke()
  } else {
    drawResistor(ctx, 95, 80, 50, true, palette)
    ctx.fillText('R', 80, 105)
    drawCap(ctx, 140, 185, palette)
    ctx.fillText('C', 126, 200)
    drawSwitch(ctx, 70, 160, palette)
    ctx.beginPath()
    ctx.moveTo(95, topY)
    ctx.lineTo(95, 80)
    ctx.lineTo(95, 130)
    ctx.lineTo(140, 130)
    ctx.lineTo(140, 175)
    ctx.lineTo(140, bottomY)
    ctx.stroke()
  }

  drawResistor(ctx, 300, 120, 40, true, palette)
  ctx.fillText('RL', 286, 140)
  drawLed(ctx, 320, 190, ledOn, palette)
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

const roundRect = (ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => {
  ctx.beginPath()
  ctx.moveTo(x + r, y)
  ctx.arcTo(x + w, y, x + w, y + h, r)
  ctx.arcTo(x + w, y + h, x, y + h, r)
  ctx.arcTo(x, y + h, x, y, r)
  ctx.arcTo(x, y, x + w, y, r)
  ctx.closePath()
}

const drawChip = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  palette: ReturnType<typeof getCanvasPalette>
) => {
  ctx.fillStyle = palette.chipFill
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  roundRect(ctx, x, y, w, h, 8)
  ctx.fill()
  ctx.stroke()
  ctx.fillStyle = palette.chipText
  ctx.font = 'bold 16px "Cervo Neue", sans-serif'
  ctx.fillText('555', x + 24, y + 50)
}

const drawResistor = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  length: number,
  vertical: boolean,
  palette: ReturnType<typeof getCanvasPalette>
) => {
  const steps = 6
  const amplitude = 6
  ctx.strokeStyle = palette.stroke
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

const drawCap = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  palette: ReturnType<typeof getCanvasPalette>
) => {
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x - 10, y)
  ctx.lineTo(x + 10, y)
  ctx.moveTo(x - 10, y + 8)
  ctx.lineTo(x + 10, y + 8)
  ctx.stroke()
}

const drawSwitch = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  palette: ReturnType<typeof getCanvasPalette>
) => {
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + 18, y - 8)
  ctx.moveTo(x, y)
  ctx.lineTo(x, y + 16)
  ctx.stroke()
}

const drawLed = (ctx: CanvasRenderingContext2D, x: number, y: number, on: boolean, palette: ReturnType<typeof getCanvasPalette>) => {
  ctx.fillStyle = on ? palette.ledOn : palette.ledOff
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.arc(x, y, 8, 0, Math.PI * 2)
  ctx.fill()
  ctx.stroke()
  if (on) {
    ctx.strokeStyle = palette.ledGlow
    ctx.lineWidth = 4
    ctx.beginPath()
    ctx.arc(x, y, 14, 0, Math.PI * 2)
    ctx.stroke()
  }
}

const stopBlink = () => {
  if (blinkTimer !== null) {
    window.clearTimeout(blinkTimer)
    blinkTimer = null
  }
}

const startBlink = () => {
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

watch([resultValue, () => form.mode], () => {
  startBlink()
})
</script>
