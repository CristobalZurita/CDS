<template>
  <div class="oscilloscope-strip" aria-hidden="true">
    <canvas ref="canvasRef" class="oscilloscope-canvas"></canvas>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const canvasRef = ref(null)

const WAVE_DUR = 5
const MORPH_DUR = 1.6

const WAVEFORMS = [
  { id: 'sine', label: 'SINE' },
  { id: 'triangle', label: 'TRIANGLE' },
  { id: 'sawtooth', label: 'SAWTOOTH ▶' },
  { id: 'revsaw', label: '◀ SAWTOOTH' },
  { id: 'square', label: 'SQUARE' },
  { id: 'pwm', label: 'PWM' },
  { id: 'noise', label: 'WHITE NOISE' },
  { id: 'sh', label: 'S & H' },
]

let raf = null
let startTime = null
let shValues = []
let noiseTable = null
let lastNoiseWidth = 0

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

function toRgba(hex, alpha) {
  const value = String(hex || '#ec6b00').trim()
  const safe = value.startsWith('#') ? value : '#ec6b00'
  const r = parseInt(safe.slice(1, 3), 16)
  const g = parseInt(safe.slice(3, 5), 16)
  const b = parseInt(safe.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v))
}

function lerp(a, b, t) {
  return a + (b - a) * t
}

function easeInOutSine(t) {
  const x = clamp(t, 0, 1)
  return -(Math.cos(Math.PI * x) - 1) / 2
}

function fract(x) {
  return x - Math.floor(x)
}

function hash1(x) {
  const s = Math.sin(x * 127.1 + 311.7) * 43758.5453123
  return fract(s)
}

function noise1(x) {
  const i = Math.floor(x)
  const f = fract(x)
  const a = hash1(i) * 2 - 1
  const b = hash1(i + 1) * 2 - 1
  const u = f * f * (3 - 2 * f)
  return lerp(a, b, u)
}

function buildSH(n) {
  shValues = Array.from({ length: n + 2 }, (_, i) => noise1(i * 0.731 + 3.17))
}

function ensureNoiseTable(width) {
  if (!noiseTable || lastNoiseWidth !== width) {
    lastNoiseWidth = width
    noiseTable = Float32Array.from({ length: width + 1 }, (_, i) => noise1(i * 0.137 + 9.31))
  }
}

function waveY(type, p, duty, shN, noiseArr) {
  switch (type) {
    case 'sine':
      return Math.sin(p * Math.PI * 2)
    case 'triangle':
      return p < 0.5 ? 4 * p - 1 : 3 - 4 * p
    case 'sawtooth':
      return 2 * p - 1
    case 'revsaw':
      return 1 - 2 * p
    case 'square':
      return p < 0.5 ? -1 : 1
    case 'pwm':
      return p < duty ? -1 : 1
    case 'noise': {
      const idx = Math.floor(clamp(p, 0, 0.999999) * (noiseArr.length - 1))
      return noiseArr[idx] ?? 0
    }
    case 'sh': {
      const idx = Math.floor(clamp(p, 0, 0.999999) * shN)
      return shValues[idx] ?? 0
    }
    default:
      return 0
  }
}

function morphWave(typeA, typeB, p, duty, shN, noiseArr, morphT) {
  const a = waveY(typeA, p, duty, shN, noiseArr)
  const b = waveY(typeB, p, duty, shN, noiseArr)
  return lerp(a, b, morphT)
}

function getMorphState(elapsed) {
  const cycle = WAVE_DUR
  const total = WAVEFORMS.length
  const globalCyclePos = elapsed / cycle
  const curIdx = Math.floor(globalCyclePos) % total
  const nextIdx = (curIdx + 1) % total
  const cycleT = fract(globalCyclePos)

  const morphStart = (WAVE_DUR - MORPH_DUR) / WAVE_DUR
  const morphRaw = clamp((cycleT - morphStart) / (1 - morphStart), 0, 1)
  const morphT = easeInOutSine(morphRaw)

  return { curIdx, nextIdx, morphT }
}

function drawGrid(ctx, width, height, primaryHex) {
  ctx.strokeStyle = toRgba(primaryHex, 0.08)
  ctx.lineWidth = 1

  const rows = 4
  const cols = 12

  ctx.beginPath()

  for (let i = 1; i < rows; i++) {
    const y = (height / rows) * i
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
  }

  for (let i = 1; i < cols; i++) {
    const x = (width / cols) * i
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
  }

  ctx.stroke()

  ctx.strokeStyle = toRgba(primaryHex, 0.14)
  ctx.beginPath()
  ctx.moveTo(0, height / 2)
  ctx.lineTo(width, height / 2)
  ctx.stroke()
}

function drawTrace(ctx, width, sampler, color, lineWidth = 2) {
  ctx.strokeStyle = color
  ctx.lineWidth = lineWidth
  ctx.lineJoin = 'round'
  ctx.lineCap = 'round'
  ctx.beginPath()

  for (let x = 0; x <= width; x += 1) {
    const y = sampler(x)
    if (x === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }

  ctx.stroke()
}

function sampleUnifiedField({
  x,
  width,
  elapsed,
  curType,
  nextType,
  morphT,
  duty,
  shN,
  noiseArr,
  freqBase,
}) {
  const xNorm = x / width
  const drift = elapsed * 0.48
  const phase = fract(xNorm * freqBase + drift)

  const oscClean = morphWave(curType, nextType, phase, duty, shN, noiseArr, morphT)

  const modWave = morphWave(
    curType,
    nextType,
    fract(
      phase * (1.7 + 0.6 * Math.sin(elapsed * 0.33)) +
      0.11 * Math.sin(elapsed * 0.8)
    ),
    duty,
    shN,
    noiseArr,
    morphT
  )

  const modSine = Math.sin(
    phase * Math.PI * 2 * (2.0 + 0.4 * Math.sin(elapsed * 0.41)) +
    elapsed * 0.9
  )

  const modulator = lerp(modSine, modWave, 0.55)

  const fmIndexBase = 0.45
  const fmIndexMorph = 1.15
  const fmIndex = fmIndexBase + fmIndexMorph * morphT

  const fmPhase =
    phase * Math.PI * 2 +
    oscClean * 0.75 +
    modulator * fmIndex

  const fmOut = Math.sin(fmPhase)

  const oscVsFmLfo = Math.sin(elapsed * 0.35) * 0.5 + 0.5
  const oscVsFm = 0.18 + oscVsFmLfo * 0.34

  return lerp(oscClean, fmOut, oscVsFm)
}

function drawWave(ctx, width, height, elapsed, primaryHex) {
  ctx.clearRect(0, 0, width, height)
  drawGrid(ctx, width, height, primaryHex)

  const { curIdx, nextIdx, morphT } = getMorphState(elapsed)
  const curType = WAVEFORMS[curIdx].id
  const nextType = WAVEFORMS[nextIdx].id

  const freqNorm = Math.sin(elapsed * 0.3) * 0.5 + 0.5
  const freqBase = lerp(2.5, 11.5, freqNorm)
  const duty = 0.5 + 0.28 * Math.sin(elapsed * 1.15)

  ensureNoiseTable(width)

  const shN = Math.max(5, Math.round(freqBase * 3.5))
  buildSH(shN)

  const amplitudeMain = height * 0.32

  drawTrace(
    ctx,
    width,
    (x) => {
      const yNorm = sampleUnifiedField({
        x,
        width,
        elapsed,
        curType,
        nextType,
        morphT,
        duty,
        shN,
        noiseArr: noiseTable,
        freqBase,
      })
      return height / 2 - yNorm * amplitudeMain
    },
    toRgba(primaryHex, 0.96),
    2.2
  )
}

function loop(timestamp) {
  if (!startTime) startTime = timestamp

  const canvas = canvasRef.value
  if (!canvas || canvas.offsetWidth <= 0) {
    raf = requestAnimationFrame(loop)
    return
  }

  const elapsed = (timestamp - startTime) / 1000
  const ctx = canvas.getContext('2d')
  const dpr = window.devicePixelRatio || 1

  const width = canvas.offsetWidth
  const height = canvas.offsetHeight

  canvas.width = Math.floor(width * dpr)
  canvas.height = Math.floor(height * dpr)
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  const primaryHex = cssVar('--cds-primary') || '#ec6b00'
  drawWave(ctx, width, height, elapsed, primaryHex)

  raf = requestAnimationFrame(loop)
}

onMounted(() => {
  buildSH(8)
  raf = requestAnimationFrame(loop)
})

onUnmounted(() => {
  if (raf) cancelAnimationFrame(raf)
})
</script>

<style scoped>
.oscilloscope-strip {
  width: 100%;
  height: var(--oscilloscope-height, clamp(4.2rem, 10vw, 6.6rem));
  background: var(--cds-light);
  overflow: hidden;
}

.oscilloscope-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
