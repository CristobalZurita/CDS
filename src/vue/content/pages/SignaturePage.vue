<template>
  <div class="signature-page">
    <div class="card">
      <h1>Firma digital</h1>
      <p>Firma dentro del recuadro y presiona Enviar.</p>

      <div class="canvas-wrap">
        <canvas ref="canvasRef" width="600" height="260" data-testid="signature-canvas"></canvas>
      </div>

      <div class="actions">
        <button class="btn btn-outline-secondary" data-testid="signature-clear" @click="clearCanvas">Limpiar</button>
        <button class="btn btn-primary" :disabled="saving" data-testid="signature-submit" @click="submitSignature">
          {{ saving ? 'Enviando...' : 'Enviar' }}
        </button>
      </div>

      <p v-if="status" class="status" data-testid="signature-status">{{ status }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'

const route = useRoute()
const token = route.params.token
const canvasRef = ref(null)
const drawing = ref(false)
const status = ref('')
const saving = ref(false)

const getPos = (event, canvas) => {
  const rect = canvas.getBoundingClientRect()
  const x = (event.touches ? event.touches[0].clientX : event.clientX) - rect.left
  const y = (event.touches ? event.touches[0].clientY : event.clientY) - rect.top
  return { x, y }
}

const getInkColor = () => {
  if (typeof window === 'undefined') return 'currentColor'
  const root = document.querySelector('.signature-page')
  if (!root) return 'currentColor'
  return getComputedStyle(root).getPropertyValue('--signature-ink').trim() || 'currentColor'
}

const startDraw = (event) => {
  drawing.value = true
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const { x, y } = getPos(event, canvas)
  ctx.beginPath()
  ctx.moveTo(x, y)
}

const draw = (event) => {
  if (!drawing.value) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const { x, y } = getPos(event, canvas)
  ctx.lineTo(x, y)
  ctx.stroke()
}

const endDraw = () => {
  drawing.value = false
}

const clearCanvas = () => {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
}

const submitSignature = async () => {
  saving.value = true
  status.value = ''
  try {
    const canvas = canvasRef.value
    const dataUrl = canvas.toDataURL('image/png')
    await api.post('/signatures/submit', { token, image_base64: dataUrl })
    status.value = 'Firma enviada correctamente.'
  } catch (e) {
    status.value = 'No se pudo enviar la firma.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.strokeStyle = getInkColor()

  canvas.addEventListener('mousedown', startDraw)
  canvas.addEventListener('mousemove', draw)
  canvas.addEventListener('mouseup', endDraw)
  canvas.addEventListener('mouseleave', endDraw)
  canvas.addEventListener('touchstart', startDraw)
  canvas.addEventListener('touchmove', draw)
  canvas.addEventListener('touchend', endDraw)
})
</script>

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.signature-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: $color-gray-100-legacy;
  padding: $spacer-lg;
  --signature-ink: #{$color-signature-ink-legacy};
}

.card {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacer-xl;
  max-width: 720px;
  width: 100%;
  border: 1px solid $color-gray-200-legacy;
}

.canvas-wrap {
  border: 2px dashed $color-gray-300-legacy;
  border-radius: $border-radius-lg;
  padding: $spacer-sm;
  margin: $spacer-md 0;
  overflow: hidden;
}

canvas {
  width: 100%;
  height: auto;
  background: $color-white;
}

.actions {
  display: flex;
  gap: $spacer-md;
}

.status {
  margin-top: $spacer-md;
  color: $color-success;
}
</style>
