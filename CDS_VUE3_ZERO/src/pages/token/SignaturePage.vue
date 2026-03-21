<template>
  <div class="signature-page">
    <div class="card card--wide">
      <h1>Firma digital</h1>
      <p v-if="requestMeta">Solicitud {{ requestMeta.request_type || 'firma' }} para OT #{{ requestMeta.repair_id }}.</p>
      <p v-else>Firma dentro del recuadro y presiona Enviar.</p>

      <div class="canvas-wrap">
        <canvas ref="canvasRef" width="600" height="260" data-testid="signature-canvas"></canvas>
      </div>

      <div class="actions">
        <button class="btn-outline" data-testid="signature-clear" :disabled="!isRequestReady" @click="clearCanvas">Limpiar</button>
        <button class="btn-primary" :disabled="saving || !isRequestReady" data-testid="signature-submit" @click="submitSignature">
          {{ saving ? 'Enviando...' : 'Enviar' }}
        </button>
      </div>

      <p v-if="status" class="status" data-testid="signature-status">{{ status }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'
import { fetchSignatureRequestByToken, openSignatureRequestStream } from '@/services/tokenRequestService'

const route = useRoute()
const token = route.params.token
const canvasRef = ref(null)
const drawing = ref(false)
const status = ref('')
const saving = ref(false)
const requestMeta = ref(null)
const loadingRequest = ref(true)

const isRequestReady = computed(() => {
  return !loadingRequest.value && String(requestMeta.value?.status || '') === 'pending'
})

let stopStream = () => {}

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
  if (!isRequestReady.value) return
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

async function loadRequestMeta() {
  loadingRequest.value = true
  status.value = ''

  try {
    requestMeta.value = await fetchSignatureRequestByToken(token)
  } catch (requestError) {
    requestMeta.value = null
    status.value = extractErrorMessage(requestError)
  } finally {
    loadingRequest.value = false
  }
}

function connectStream() {
  stopStream()
  stopStream = () => {}

  if (!token || !isRequestReady.value) return

  stopStream = openSignatureRequestStream(token, {
    onEvent: (eventName) => {
      if (eventName === 'signature_received') {
        requestMeta.value = requestMeta.value ? { ...requestMeta.value, status: 'signed' } : null
        status.value = 'La firma ya fue registrada.'
        stopStream()
        stopStream = () => {}
        return
      }

      if (eventName === 'signature_cancelled') {
        requestMeta.value = requestMeta.value ? { ...requestMeta.value, status: 'cancelled' } : null
        status.value = 'La solicitud de firma fue cancelada.'
        stopStream()
        stopStream = () => {}
      }
    }
  })
}

async function submitSignature() {
  if (!isRequestReady.value) return
  saving.value = true
  status.value = ''
  try {
    const canvas = canvasRef.value
    const dataUrl = canvas.toDataURL('image/png')
    await api.post('/signatures/submit', { token, image_base64: dataUrl })
    requestMeta.value = requestMeta.value ? { ...requestMeta.value, status: 'signed' } : null
    status.value = 'Firma enviada correctamente.'
  } catch {
    status.value = 'No se pudo enviar la firma.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadRequestMeta()
  connectStream()

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

onBeforeUnmount(() => {
  stopStream()
})
</script>

<style scoped src="./commonTokenPage.css"></style>
