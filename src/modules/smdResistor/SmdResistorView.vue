<template>
  <PageSection variant="default" id="smd-40106-calculator-root">
    <PageSectionHeader
      title="*Oscilador* CD40106"
      subtitle="Schmitt trigger con R y C para sintetizadores digitales"
    />

    <PageSectionContent>
      <div class="cd40106-layout">
        <div class="cd40106-panel">
          <div class="panel-header">
            <div class="panel-title">
              <i class="fa-solid fa-sliders"></i>
              Parametros
            </div>
          </div>

          <form class="panel-form" @submit.prevent="onCalculate">
            <div class="form-grid">
              <div class="form-field">
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
                src="https://res.cloudinary.com/dgwwi77ic/image/upload/v1773305907/CD40106.webp"
                alt="Pinout CD40106"
                class="pinout-image"
              />
            </div>
          </form>
        </div>

        <div class="cd40106-panel output-panel">
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

            <div class="output-hint">
              La frecuencia es aproximada. Ajusta R y C para cambiar el tono.
            </div>
          </div>
        </div>
      </div>

      <div class="cd40106-back">
        <Link url="/calculadoras">
          <span class="cd40106-back-link">← VOLVER A CALCULADORAS</span>
        </Link>
      </div>
    </PageSectionContent>
  </PageSection>

  <WorkshopFooter />
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useCloudinaryImage } from '@/composables/useCloudinary'
import PageSection from '/src/vue/components/layout/PageSection.vue'
import PageSectionHeader from '/src/vue/components/layout/PageSectionHeader.vue'
import PageSectionContent from '/src/vue/components/layout/PageSectionContent.vue'
import Link from '/src/vue/components/generic/Link.vue'
import WorkshopFooter from '/src/vue/components/footer/WorkshopFooter.vue'

const form = reactive({
  r_value: 100,
  r_unit: 'kohm',
  c_value: 0.1,
  c_unit: 'uf',
  vcc_v: 9
})

const canvasRef = ref<HTMLCanvasElement | null>(null)
let blinkTimer: number | null = null
let ledOn = false

const frequencyHz = computed(() => {
  const r = form.r_value * resistanceFactor(form.r_unit)
  const c = form.c_value * capacitanceFactor(form.c_unit)
  if (!r || !c) return 0
  return 1 / (1.2 * r * c)
})

const periodMs = computed(() => {
  if (!frequencyHz.value) return 0
  return 1000 / frequencyHz.value
})

const formattedFrequency = computed(() => {
  if (!frequencyHz.value) return '---'
  return `${frequencyHz.value.toFixed(2)} Hz`
})

const formattedPeriod = computed(() => {
  if (!periodMs.value) return '---'
  return `${periodMs.value.toFixed(2)} ms`
})

function onCalculate() {
  startBlink()
}

function reset() {
  form.r_value = 100
  form.r_unit = 'kohm'
  form.c_value = 0.1
  form.c_unit = 'uf'
  form.vcc_v = 9
  startBlink()
}

const clampMs = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max)

const getBlinkDurations = () => {
  const base = periodMs.value || 800
  const onMs = clampMs(base * 0.5, 80, 2500)
  const offMs = clampMs(base * 0.5, 80, 2500)
  return { onMs, offMs }
}

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
  const root = document.getElementById('smd-40106-calculator-root')
  const styles = root ? getComputedStyle(root) : null
  const read = (name: string) => (styles?.getPropertyValue(name).trim() || 'transparent')
  return {
    panelFill: read('--smd-panel-fill'),
    stroke: read('--smd-stroke'),
    chipFill: read('--smd-chip-fill'),
    chipText: read('--smd-chip-text'),
    ledOn: read('--smd-led-on'),
    ledOff: read('--smd-led-off'),
    ledGlow: read('--smd-led-glow')
  }
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

  drawGate(ctx, 200, 90, 70, 70, palette)
  drawResistor(ctx, 130, 60, 50, true, palette)
  ctx.fillText('R', 118, 85)
  drawCap(ctx, 130, 180, palette)
  ctx.fillText('C', 118, 195)

  ctx.beginPath()
  ctx.moveTo(130, topY)
  ctx.lineTo(130, 60)
  ctx.lineTo(130, 180)
  ctx.lineTo(130, bottomY)
  ctx.stroke()

  drawLed(ctx, 320, 150, ledOn, palette)
  ctx.beginPath()
  ctx.moveTo(270, 125)
  ctx.lineTo(320, 125)
  ctx.lineTo(320, 142)
  ctx.moveTo(320, 158)
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

const drawGate = (ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, palette: ReturnType<typeof getCanvasPalette>) => {
  ctx.fillStyle = palette.chipFill
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x, y)
  ctx.lineTo(x + w, y + h / 2)
  ctx.lineTo(x, y + h)
  ctx.closePath()
  ctx.fill()
  ctx.stroke()

  ctx.fillStyle = palette.chipText
  ctx.beginPath()
  ctx.arc(x + w + 6, y + h / 2, 6, 0, Math.PI * 2)
  ctx.fill()
}

const drawResistor = (ctx: CanvasRenderingContext2D, x: number, y: number, length: number, vertical: boolean, palette: ReturnType<typeof getCanvasPalette>) => {
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

const drawCap = (ctx: CanvasRenderingContext2D, x: number, y: number, palette: ReturnType<typeof getCanvasPalette>) => {
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x - 10, y)
  ctx.lineTo(x + 10, y)
  ctx.moveTo(x - 10, y + 8)
  ctx.lineTo(x + 10, y + 8)
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

watch([frequencyHz, () => form.r_kohm, () => form.c_uf], () => {
  startBlink()
})
</script>
