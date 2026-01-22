<template>
  <div class="signature-page">
    <div class="card">
      <h1>Firma digital</h1>
      <p>Firma dentro del recuadro y presiona Enviar.</p>

      <div class="canvas-wrap">
        <canvas ref="canvasRef" width="600" height="260"></canvas>
      </div>

      <div class="actions">
        <button class="btn btn-outline-secondary" @click="clearCanvas">Limpiar</button>
        <button class="btn btn-primary" :disabled="saving" @click="submitSignature">
          {{ saving ? 'Enviando...' : 'Enviar' }}
        </button>
      </div>

      <p v-if="status" class="status">{{ status }}</p>
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
  ctx.strokeStyle = '#222'

  canvas.addEventListener('mousedown', startDraw)
  canvas.addEventListener('mousemove', draw)
  canvas.addEventListener('mouseup', endDraw)
  canvas.addEventListener('mouseleave', endDraw)
  canvas.addEventListener('touchstart', startDraw)
  canvas.addEventListener('touchmove', draw)
  canvas.addEventListener('touchend', endDraw)
})
</script>

<style scoped>
.signature-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f3f4f6;
  padding: 1.5rem;
}
.card {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  max-width: 720px;
  width: 100%;
  border: 1px solid #e5e7eb;
}
.canvas-wrap {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 0.5rem;
  margin: 1rem 0;
  overflow: hidden;
}
canvas {
  width: 100%;
  height: auto;
  background: #fff;
}
.actions {
  display: flex;
  gap: 1rem;
}
.status {
  margin-top: 1rem;
  color: #059669;
}
</style>
