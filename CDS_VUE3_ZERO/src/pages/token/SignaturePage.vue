<template>
  <div class="signature-page">
    <div class="card card--wide">
      <h1>Firma digital</h1>
      <p>Firma dentro del recuadro y presiona Enviar.</p>

      <div class="canvas-wrap">
        <canvas ref="canvasRef" width="600" height="260" data-testid="signature-canvas"></canvas>
      </div>

      <div class="actions">
        <button class="btn-outline" data-testid="signature-clear" @click="clearCanvas">Limpiar</button>
        <button class="btn-primary" :disabled="saving" data-testid="signature-submit" @click="submitSignature">
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
import api from '@/services/api'

const route = useRoute()
const token = route.params.token
const canvasRef = ref(null)
const drawing = ref(false)
const status = ref('')
const saving = ref(false)

function getPos(event, canvas) {
  const rect = canvas.getBoundingClientRect()
  const x = (event.touches ? event.touches[0].clientX : event.clientX) - rect.left
  const y = (event.touches ? event.touches[0].clientY : event.clientY) - rect.top
  return { x, y }
}

function getInkColor() {
  if (typeof window === 'undefined') return '#222222'
  const root = document.querySelector('.signature-page')
  if (!root) return '#222222'
  return getComputedStyle(root).getPropertyValue('--signature-ink').trim() || '#222222'
}

function startDraw(event) {
  drawing.value = true
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const { x, y } = getPos(event, canvas)
  ctx.beginPath()
  ctx.moveTo(x, y)
}

function draw(event) {
  if (!drawing.value) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const { x, y } = getPos(event, canvas)
  ctx.lineTo(x, y)
  ctx.stroke()
}

function endDraw() {
  drawing.value = false
}

function clearCanvas() {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
}

async function submitSignature() {
  saving.value = true
  status.value = ''
  try {
    const canvas = canvasRef.value
    const dataUrl = canvas.toDataURL('image/png')
    await api.post('/signatures/submit', { token, image_base64: dataUrl })
    status.value = 'Firma enviada correctamente.'
  } catch {
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

<style scoped src="./commonTokenPage.css"></style>
