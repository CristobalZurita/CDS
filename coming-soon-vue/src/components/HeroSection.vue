<template>
  <section class="hero">

    <!-- Capa PCB: trazas crecientes, ICs, pads — detrás de todo -->
    <canvas ref="pcbCanvas" class="pcb-canvas" aria-hidden="true"></canvas>

    <!-- Máscara: queso del sánguche — protege el texto de las animaciones -->
    <div class="hero-mask" aria-hidden="true"></div>

    <!-- Contenido principal -->
    <div class="hero-content">

      <img
        src="/images/logo/NUEVO_cirujano.webp"
        alt="Cirujano de Sintetizadores"
        class="hero-logo"
        width="1800"
        height="1220"
        loading="eager"
      />

      <h1 class="hero-title">
        Pr<span class="ct" aria-label="ó">o<span class="ct-mark">´</span></span>xima
        Inauguraci<span class="ct" aria-label="ó">o<span class="ct-mark">´</span></span>n
      </h1>

      <ul class="services-type" aria-label="Servicios">
        <li>Restauraci<span class="ct" aria-label="ó">o<span class="ct-mark">´</span></span>n</li>
        <li class="sep" aria-hidden="true">·</li>
        <li>Mantenci<span class="ct" aria-label="ó">o<span class="ct-mark">´</span></span>n</li>
        <li class="sep" aria-hidden="true">·</li>
        <li>Reparaci<span class="ct" aria-label="ó">o<span class="ct-mark">´</span></span>n</li>
      </ul>

      <div class="hero-body">
        <p class="hero-body-sub">
          <strong class="url-line">www.cirujanodesintetizadores.cl</strong>
          <span class="body-tagline">—  El Quirófano Electrónico abre pronto —</span>
        </p>
      </div>

      <div class="hero-actions">
        <a
          href="https://wa.me/56982957538?text=Hola%2C%20me%20interesa%20una%20cotizaci%C3%B3n"
          class="btn btn-wa"
          target="_blank"
          rel="noopener noreferrer"
        >
          <i class="fa-brands fa-whatsapp"></i>
          Escríbenos
        </a>
        <a href="#contacto" class="btn btn-dark">
          <i class="fas fa-envelope"></i>
          Dejar mensaje
        </a>
      </div>

    </div>

    <!-- Osciloscopio: franja inferior, formas de onda ciclando -->
    <div class="osc-wrap" aria-hidden="true">
      <canvas ref="oscCanvas" class="osc-canvas"></canvas>
    </div>

  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// ── Refs ──────────────────────────────────────────────────────
const pcbCanvas = ref(null)
const oscCanvas = ref(null)
let raf       = null
let startTime = null

// ── Utilidades ────────────────────────────────────────────────
function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}
function toRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

// ══════════════════════════════════════════════════════════════
//  PCB ANIMATION — routing pad-a-pad real en L
// ══════════════════════════════════════════════════════════════

const GRID = 20   // grilla ortogonal en px

let traces  = []
let chips   = []
let pcbTick = 0

function snap(v) { return Math.round(v / GRID) * GRID }

// Zona central del texto Y franja del osciloscopio — trazas no se originan aquí
function inCenter(x, y, W, H) {
  const inText = x > W * 0.22 && x < W * 0.78 && y > H * 0.16 && y < H * 0.84
  const inOsc  = y > H * 0.88          // franja inferior del osciloscopio
  return inText || inOsc
}
function edgePt(W, H) {
  const M = GRID * 2; let x, y, t = 0
  do {
    x = snap(M + Math.random() * (W - 2 * M))
    y = snap(M + Math.random() * (H - 2 * M))
  } while (inCenter(x, y, W, H) && ++t < 20)
  return { x, y }
}

// ── Traza real: pad A → esquina 90° → pad B ──────────────────
function makeTrace(W, H) {
  const a = edgePt(W, H)
  let b, t = 0
  do { b = edgePt(W, H) }
  while (Math.hypot(b.x - a.x, b.y - a.y) < GRID * 7 && ++t < 20)

  // Punto de esquina — routing en L (elige la dirección que no cruce el centro)
  let hFirst = Math.random() > 0.5
  let kx = hFirst ? b.x : a.x
  let ky = hFirst ? a.y : b.y
  // Si la esquina cae en el centro, intentar la otra dirección
  if (inCenter(kx, ky, W, H)) {
    hFirst = !hFirst
    kx = hFirst ? b.x : a.x
    ky = hFirst ? a.y : b.y
  }

  const segs = []
  const L1 = Math.abs(kx - a.x) + Math.abs(ky - a.y)
  if (L1 >= GRID) segs.push({ x1: a.x, y1: a.y, x2: kx, y2: ky, L: L1 })
  const L2 = Math.abs(b.x - kx) + Math.abs(b.y - ky)
  if (L2 >= GRID) segs.push({ x1: kx, y1: ky, x2: b.x, y2: b.y, L: L2 })

  if (segs.length === 0) return null

  return {
    segs,
    totalLen: segs.reduce((s, g) => s + g.L, 0),
    drawn:    0,
    alpha:    0,
    phase:    'in',
    hold:     80 + Math.floor(Math.random() * 150),
    holdN:    0,
    lw:       1.5,
  }
}

// ── DIP IC chip (pins solo izq/der, como chip real) ──────────
function makeDIP(W, H) {
  const pps    = 4 + Math.floor(Math.random() * 4)  // pins por lado: 4-7
  const pitch  = 20                                   // 20px entre pins (~2.54mm)
  const pinLen = 18                                   // largo del pin desde el cuerpo
  const bodyH  = (pps - 1) * pitch + 14
  const bodyW  = 36 + Math.floor(Math.random() * 3) * 10 // 36, 46 o 56px

  let x, y, tt = 0
  do {
    x = snap(bodyW / 2 + pinLen + GRID * 2 + Math.random() * (W - bodyW - 2 * (pinLen + GRID * 2)))
    y = snap(bodyH / 2 + GRID * 2 + Math.random() * (H - bodyH - GRID * 4))
  } while (inCenter(x, y, W, H) && ++tt < 20)

  return {
    x, y, bodyW, bodyH, pps, pitch, pinLen,
    alpha: 0,
    phase: 'in',
    hold:  200 + Math.floor(Math.random() * 220),
    holdN: 0,
  }
}

// ── Lifecycle ────────────────────────────────────────────────
function updatePcb(W, H) {
  pcbTick++
  if (traces.length < 14 && pcbTick % 20 === 0) {
    const t = makeTrace(W, H)
    if (t) traces.push(t)
  }
  if (chips.length < 5 && pcbTick % 90 === 0) chips.push(makeDIP(W, H))

  traces.forEach(t => {
    if (t.phase === 'in') {
      t.drawn = Math.min(t.drawn + 2, t.totalLen)
      t.alpha = Math.min(t.alpha + 0.03, 0.70)
      if (t.drawn >= t.totalLen) t.phase = 'hold'
    } else if (t.phase === 'hold') {
      if (++t.holdN >= t.hold) t.phase = 'out'
    } else {
      t.alpha -= 0.008
    }
  })
  traces = traces.filter(t => t.alpha > 0)

  chips.forEach(c => {
    if (c.phase === 'in') {
      c.alpha = Math.min(c.alpha + 0.025, 0.82)
      if (c.alpha >= 0.82) c.phase = 'hold'
    } else if (c.phase === 'hold') {
      if (++c.holdN >= c.hold) c.phase = 'out'
    } else {
      c.alpha -= 0.009
    }
  })
  chips = chips.filter(c => c.alpha > 0)
}

// ── Pad / anular ring ────────────────────────────────────────
function drawPad(ctx, px, py, outerR, holeR, colCopper, colBg) {
  ctx.beginPath()
  ctx.arc(px, py, outerR, 0, Math.PI * 2)
  ctx.fillStyle = colCopper
  ctx.fill()
  ctx.beginPath()
  ctx.arc(px, py, holeR, 0, Math.PI * 2)
  ctx.fillStyle = colBg
  ctx.fill()
}

// ── Render ───────────────────────────────────────────────────
function drawPcb(ctx, W, H, copperHex, bgHex, darkHex) {
  ctx.clearRect(0, 0, W, H)

  // ─ Trazas ──────────────────────────────────────────────────
  traces.forEach(t => {
    if (t.alpha <= 0) return
    const col    = toRgba(copperHex, t.alpha)
    const colBg  = bgHex                          // color sólido para agujeros

    // Línea de traza
    ctx.strokeStyle = col
    ctx.lineWidth   = t.lw
    ctx.lineJoin    = 'miter'
    ctx.lineCap     = 'square'
    ctx.beginPath()
    let rem = t.drawn, moved = false
    for (const seg of t.segs) {
      if (rem <= 0) break
      const r  = Math.min(rem, seg.L) / seg.L
      const ex = seg.x1 + (seg.x2 - seg.x1) * r
      const ey = seg.y1 + (seg.y2 - seg.y1) * r
      if (!moved) { ctx.moveTo(seg.x1, seg.y1); moved = true }
      ctx.lineTo(ex, ey)
      rem -= seg.L
    }
    ctx.stroke()

    // Pads anulares en cada vértice ya dibujado
    const padR  = 4.0
    const holeR = 1.6
    let cl = 0
    for (const seg of t.segs) {
      if (cl > t.drawn) break
      drawPad(ctx, seg.x1, seg.y1, padR, holeR, col, colBg)
      cl += seg.L
    }

    // Vía en la esquina de la L cuando la traza está ≥ 50 % dibujada
    if (t.segs.length >= 2 && t.drawn >= t.totalLen * 0.5) {
      const mid = t.segs[0]   // esquina de la L
      const vR  = Math.max(5, t.lw * 3.5)
      const vH  = Math.max(2, t.lw * 1.3)
      // Anillo exterior de la vía
      ctx.beginPath()
      ctx.arc(mid.x1, mid.y1, vR + 2.5, 0, Math.PI * 2)
      ctx.strokeStyle = col
      ctx.lineWidth   = 1
      ctx.stroke()
      drawPad(ctx, mid.x1, mid.y1, vR, vH, col, colBg)
    }
  })

  // ─ DIP ICs ─────────────────────────────────────────────────
  chips.forEach(c => {
    if (c.alpha <= 0) return
    const col    = toRgba(copperHex, c.alpha)
    const colBg  = bgHex
    const colBod = toRgba(darkHex, c.alpha * 0.85)  // cuerpo oscuro del IC
    const { x, y, bodyW, bodyH, pps, pitch, pinLen } = c
    const x0     = x - bodyW / 2
    const y0     = y - bodyH / 2
    const startY = y - ((pps - 1) * pitch) / 2

    // Cuerpo (rectángulo oscuro + borde cobre)
    ctx.fillStyle = colBod
    ctx.fillRect(x0, y0, bodyW, bodyH)
    ctx.strokeStyle = col
    ctx.lineWidth   = 1.5
    ctx.strokeRect(x0, y0, bodyW, bodyH)

    // Muesca semicircular en el extremo superior (pin-1 side)
    ctx.beginPath()
    ctx.arc(x, y0, 5.5, 0, Math.PI)
    ctx.strokeStyle = col
    ctx.lineWidth   = 1.5
    ctx.stroke()

    // Indicador pin-1 (punto dentro del cuerpo)
    ctx.beginPath()
    ctx.arc(x0 + 6, startY, 2.2, 0, Math.PI * 2)
    ctx.fillStyle = col
    ctx.fill()

    // Pins izquierda y derecha (igual que en un DIP real)
    for (let i = 0; i < pps; i++) {
      const py = startY + i * pitch

      // — Pin izquierdo —
      ctx.beginPath()
      ctx.moveTo(x0, py)
      ctx.lineTo(x0 - pinLen, py)
      ctx.strokeStyle = col
      ctx.lineWidth   = 2
      ctx.stroke()
      drawPad(ctx, x0 - pinLen, py, 4.5, 1.8, col, colBg)

      // — Pin derecho —
      ctx.beginPath()
      ctx.moveTo(x + bodyW / 2, py)
      ctx.lineTo(x + bodyW / 2 + pinLen, py)
      ctx.strokeStyle = col
      ctx.lineWidth   = 2
      ctx.stroke()
      drawPad(ctx, x + bodyW / 2 + pinLen, py, 4.5, 1.8, col, colBg)
    }

    // Texto del chip (pequeño, dentro del cuerpo)
    if (bodyW > 40 && bodyH > 50) {
      ctx.save()
      ctx.translate(x, y)
      ctx.rotate(-Math.PI / 2)
      ctx.fillStyle   = toRgba(copperHex, c.alpha * 0.5)
      ctx.font        = `600 ${Math.min(9, bodyW * 0.18)}px monospace`
      ctx.textAlign   = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('IC', 0, 0)
      ctx.restore()
    }
  })
}

// ══════════════════════════════════════════════════════════════
//  WAVEFORM ANIMATION — morph continuo + frecuencia variable
// ══════════════════════════════════════════════════════════════

const WAVE_DUR   = 5      // segundos por episodio
const MORPH_DUR  = 1      // segundos de morphing al final de cada episodio
const WAVEFORMS = [
  { id: 'sine',     label: 'SINE'        },
  { id: 'triangle', label: 'TRIANGLE'    },
  { id: 'sawtooth', label: 'SAWTOOTH ▶'  },
  { id: 'revsaw',   label: '◀ SAWTOOTH'  },
  { id: 'square',   label: 'SQUARE'      },
  { id: 'pwm',      label: 'PWM'         },
  { id: 'noise',    label: 'WHITE NOISE' },
  { id: 'sh',       label: 'S & H'       },
]

// Estado persistente del osciloscopio
let oscEpStart      = 0    // elapsed al inicio del episodio
let oscCurIdx       = 0    // índice waveform actual
let oscNextIdx      = 1    // índice waveform hacia el que morphea
let oscPrevEpStart  = -1   // detecta cambio de episodio
let oscEpisodeNoise = null // noise estable por episodio (no regenerar cada frame)
let oscEpisodeShN   = 8    // nº muestras S&H estable por episodio

let shValues = []
function buildSH(n) {
  shValues = Array.from({ length: n + 2 }, () => Math.random() * 2 - 1)
}

function lerp(a, b, t) { return a + (b - a) * t }
function smoothstep(t)  { return t * t * (3 - 2 * t) }

function waveY(type, p, duty, shN, noiseArr) {
  switch (type) {
    case 'sine':     return Math.sin(p * Math.PI * 2)
    case 'triangle': return p < 0.5 ? 4 * p - 1 : 3 - 4 * p
    case 'sawtooth': return 2 * p - 1
    case 'revsaw':   return 1 - 2 * p
    case 'square':   return p < 0.5 ? -1 : 1
    case 'pwm':      return p < duty ? -1 : 1
    case 'noise':    return noiseArr[Math.floor(p * (noiseArr.length - 1))]
    case 'sh':       return shValues[Math.floor(p * shN)] ?? 0
    default:         return 0
  }
}

function drawWave(ctx, W, H, elapsed, primaryHex) {
  ctx.clearRect(0, 0, W, H)

  // ── Avance de episodio PRIMERO, luego calcular timeInEp ─────────
  // (si se calcula timeInEp antes del reset, en el frame de transición
  //  vale > WAVE_DUR y morphT llega a 1.0 apuntando al índice equivocado)
  if (elapsed - oscEpStart >= WAVE_DUR) {
    oscEpStart = elapsed
    oscCurIdx  = oscNextIdx
    oscNextIdx = (oscCurIdx + 1) % WAVEFORMS.length
  }
  const timeInEp = elapsed - oscEpStart  // siempre fresco tras el posible reset

  // morphT: 0 = solo current, 1 = solo next (último segundo del episodio)
  const morphRaw = Math.max(0, (timeInEp - (WAVE_DUR - MORPH_DUR)) / MORPH_DUR)
  const morphT   = smoothstep(Math.min(1, morphRaw))

  // Frecuencia: barrido logarítmico lento 20 Hz → 20 kHz
  // freqNorm 0→1→0 cada ~19.6 s  |  freq 1→50 ciclos visibles (escala log)
  const freqNorm = Math.sin(elapsed * 0.32) * 0.5 + 0.5
  const freq     = Math.pow(50, freqNorm)

  // PWM duty continuo
  const duty = 0.5 + 0.35 * Math.sin(elapsed * 1.2)

  // Noise y S&H: estables por episodio — se regeneran solo al cambiar de onda
  const isNewEp = oscEpStart !== oscPrevEpStart || !oscEpisodeNoise || oscEpisodeNoise.length !== W
  if (isNewEp) {
    oscPrevEpStart  = oscEpStart
    oscEpisodeNoise = Float32Array.from({ length: W }, () => Math.random() * 2 - 1)
    oscEpisodeShN   = Math.max(4, Math.round(freq * 4))
    buildSH(oscEpisodeShN)
  }
  const shN      = oscEpisodeShN
  const noiseArr = oscEpisodeNoise

  const curType  = WAVEFORMS[oscCurIdx].id
  const nextType = WAVEFORMS[oscNextIdx].id
  const curLabel = WAVEFORMS[oscCurIdx].label

  // ── Eje central ───────────────────────────────────────────
  ctx.strokeStyle = toRgba(primaryHex, 0.12)
  ctx.lineWidth   = 1
  ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke()

  // ── Forma de onda con morph ───────────────────────────────
  const amp = H * 0.36
  ctx.strokeStyle = toRgba(primaryHex, 0.88)
  ctx.lineWidth   = 2
  // Para cuadrada/pwm en cualquiera de los dos extremos: lineJoin miter
  const isSharp = (curType === 'square' || curType === 'pwm' ||
                   nextType === 'square' || nextType === 'pwm')
  ctx.lineJoin = isSharp ? 'miter' : 'round'
  ctx.lineCap  = 'round'

  ctx.beginPath()
  for (let x = 0; x <= W; x++) {
    const dist = Math.abs(x - W / 2) / (W / 2)   // 0 en centro → 1 en bordes
    const t    = dist * freq
    const p    = t % 1
    const pRaw = (x / W * freq) % 1  // lineal + freq, sin simetría — noise y S&H
    const yA  = waveY(curType,  (curType  === 'noise' || curType  === 'sh') ? pRaw : p, duty, shN, noiseArr)
    const yB  = waveY(nextType, (nextType === 'noise' || nextType === 'sh') ? pRaw : p, duty, shN, noiseArr)
    const yn  = lerp(yA, yB, morphT)
    const y   = H / 2 - yn * amp
    x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
  }
  ctx.stroke()

  // ── Label ─────────────────────────────────────────────────
  ctx.fillStyle = toRgba(primaryHex, 0.5)
  ctx.font      = `var(--cds-font-semibold) 10px monospace`
  ctx.textAlign = 'right'
  const lbl = curType === 'pwm' ? `PWM ${Math.round(duty * 100)}%` : curLabel
  ctx.fillText(lbl, W - 8, H - 5)
}

// ══════════════════════════════════════════════════════════════
//  LOOP PRINCIPAL
// ══════════════════════════════════════════════════════════════

function loop(ts) {
  if (!startTime) startTime = ts
  const elapsed    = (ts - startTime) / 1000
  const copperHex  = cssVar('--cds-primary') || '#ec6b00'
  const bgHex      = cssVar('--cds-light')   || '#d3d0c3'
  const darkHex    = cssVar('--cds-dark')    || '#5a5a5a'

  const pcb = pcbCanvas.value
  if (pcb && pcb.offsetWidth > 0) {
    const ctx = pcb.getContext('2d')
    const W   = (pcb.width  = pcb.offsetWidth)
    const H   = (pcb.height = pcb.offsetHeight)
    updatePcb(W, H)
    drawPcb(ctx, W, H, copperHex, bgHex, darkHex)
  }

  const osc = oscCanvas.value
  if (osc && osc.offsetWidth > 0) {
    const ctx = osc.getContext('2d')
    const W   = (osc.width  = osc.offsetWidth)
    const H   = (osc.height = osc.offsetHeight)
    drawWave(ctx, W, H, elapsed, copperHex)
  }

  raf = requestAnimationFrame(loop)
}

onMounted(() => { buildSH(8); raf = requestAnimationFrame(loop) })
onUnmounted(() => { if (raf) cancelAnimationFrame(raf) })
</script>

<style scoped>
/* ─── Sección ───────────────────────────────────── */
.hero {
  background: var(--cds-light);
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* ─── Canvas PCB — capa base detrás de todo ─────── */
.pcb-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.88;
}

/* ─── Máscara: queso del sánguche ───────────────── */
/* Misma bg que el hero. box-shadow difumina hacia   */
/* afuera: cerca = opaco, lejos = transparente.      */
.hero-mask {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -52%);
  width: min(92vw, 1040px);
  height: 74%;
  background: var(--cds-light);
  border-radius: 2.5rem;
  box-shadow: 0 0 70px 70px var(--cds-light);
  pointer-events: none;
  z-index: 1;
}

/* ─── Contenido — siempre encima de la máscara ──── */
.hero-content {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: clamp(3rem, 6vw, 5rem) clamp(1.25rem, 5vw, 3em) clamp(6rem, 14vw, 8rem);
  gap: clamp(1.2rem, 2.5vw, 1.8rem);
  width: 100%;
  max-width: 1440px;
margin-top: -4.5rem; /* compensa el padding inferior para que el osciloscopio quede pegado */
}

/* ─── Canvas osciloscopio — franja inferior ──────── */
.osc-wrap {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: clamp(5rem, 12vw, 9rem);
  pointer-events: none;
  z-index: 2;
}

.osc-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* ─── Logo ──────────────────────────────────────── */
.hero-logo {
  width: 50vw;
  max-width: none;
  height: auto;
  animation: fadeUp 0.7s 0.05s ease both;
  margin-bottom: -0.5rem;
}

/* ─── Titular ───────────────────────────────────── */
.hero-title {
  font-family: var(--cds-headings-font-family);
  font-size: clamp(2.8rem, 7vw, 6.5rem);
  font-weight: var(--cds-font-semibold);
  line-height: 0.95;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--cds-black);
  white-space: nowrap;
  animation: fadeUp 0.65s 0.18s ease both;
}

/* ── Regla exclusiva del acento ─────────────────── */
.ct {
  display: inline-block;
  position: relative;
}
.ct-mark {
  position: absolute;
  top:  -.32em;
  left: 70%;
  transform: translateX(-50%);
  font-size:      0.7em;
  line-height:    1;
  pointer-events: none;
  user-select:    none;
}

/* ─── Servicios ─────────────────────────────────── */
.services-type {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: baseline;
  gap: 0.4em 0.6em;
  font-family: var(--cds-font-family-base);
  font-size: clamp(2rem, 3.6vw, 2.1rem);
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--cds-primary);
  animation: fadeUp 0.6s 0.30s ease both;
}
.sep {
  color: var(--cds-dark);
  opacity: 0.3;
}

/* ─── Cuerpo ────────────────────────────────────── */
.hero-body {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  animation: fadeUp 0.6s 0.42s ease both;
}
.hero-body-sub {
  font-size: clamp(1.4rem, 5.5vw, 2.8rem);
  font-weight: var(--cds-font-medium);
  line-height: 1.3;
  color: var(--cds-black);
  opacity: 0.75;
}
.url-line     { display: block; font-weight: var(--cds-font-bold); }
.body-tagline { display: block; }

/* ─── Botones ───────────────────────────────────── */
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: center;
  animation: fadeUp 0.6s 0.54s ease both;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 83.6px;
  padding: 1.14rem 2.47rem;
  border-radius: var(--cds-radius-pill);
  font-family: var(--cds-font-family-base);
  font-size: 1.76rem;
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.07em;
  text-transform: uppercase;
  text-decoration: none;
  transition: transform 0.15s, opacity 0.15s;
}
.btn:hover  { transform: translateY(-2px); opacity: 0.88; }
.btn:active { transform: translateY(0); }
.btn-wa   { background: var(--cds-whatsapp); color: var(--cds-white); }
.btn-dark { background: var(--cds-primary);     color: var(--cds-light); }

/* ─── Entrada ───────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ─── Tablet (600–899px) ────────────────────────── */
@media (min-width: 600px) and (max-width: 899px) {
  .hero-title { white-space: normal; }
}

/* ─── Mobile (<600px) ───────────────────────────── */
@media (max-width: 599px) {
  .hero                    { justify-content: flex-start; }
  .hero-title              { white-space: normal; }
  .hero-actions            { flex-direction: column; align-items: center; }
  .services-type           { letter-spacing: 0.12em; flex-direction: column; align-items: center; }
  .services-type .sep      { display: none; }
  .services-type .ct-mark  { font-size: 1.1em; }
  .hero-logo               { width: 95vw; }
  .hero-content            { margin-top: 0; padding-top: clamp(1.2rem, 3vw, 2rem); padding-bottom: clamp(5.5rem, 14vw, 10rem); }
  .hero-body               { text-align: center; width: 100%; }
}

/* ─── Landscape móvil ───────────────────────────── */
@media (max-width: 900px) and (orientation: landscape) {
  .hero-logo { width: auto; max-height: 28vh; }
}
</style>
