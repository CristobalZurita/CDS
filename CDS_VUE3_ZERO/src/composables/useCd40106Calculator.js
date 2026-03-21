import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

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

function clampMs(value, min, max) {
  return Math.min(Math.max(value, min), max)
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

function drawGate(ctx, x, y, w, h, palette) {
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

function drawResistor(ctx, x, y, length, vertical, palette) {
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

function drawCap(ctx, x, y, palette) {
  ctx.strokeStyle = palette.stroke
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(x - 10, y)
  ctx.lineTo(x + 10, y)
  ctx.moveTo(x - 10, y + 8)
  ctx.lineTo(x + 10, y + 8)
  ctx.stroke()
}

function drawLed(ctx, x, y, on, palette) {
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

export function useCd40106Calculator() {
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

  const formattedFrequency = computed(() => (
    frequencyHz.value ? formatFrequency(frequencyHz.value) : '-'
  ))

  const formattedPeriod = computed(() => (
    periodMs.value ? formatTime(periodMs.value / 1000) : '-'
  ))

  function reset() {
    form.r_value = 100
    form.r_unit = 'kohm'
    form.c_value = 0.1
    form.c_unit = 'uf'
    form.vcc_v = 9
  }

  function getBlinkDurations() {
    const base = periodMs.value || 800
    return {
      onMs: clampMs(base * 0.5, 80, 2500),
      offMs: clampMs(base * 0.5, 80, 2500),
    }
  }

  function getCanvasPalette() {
    const canvas = canvasRef.value
    if (!canvas || typeof window === 'undefined') {
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
    const styles = getComputedStyle(canvas)
    const read = (name) => styles.getPropertyValue(name).trim() || 'transparent'
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

  function drawCircuit() {
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

    ctx.font = '14px "Aptos", "Segoe UI", Arial, sans-serif'
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

  function setCanvasElement(element) {
    canvasRef.value = element || null
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

  return {
    form,
    formattedFrequency,
    formattedPeriod,
    reset,
    setCanvasElement,
  }
}
