<template>
  <div class="photo-upload-page">
    <div class="card card--narrow">
      <h1>Subir foto</h1>
      <p v-if="requestMeta">Envía una foto {{ requestMeta.photo_type || 'client' }} para la OT #{{ requestMeta.repair_id }}.</p>
      <p v-else>Envía una foto para esta reparación.</p>

      <div class="form-group">
        <label for="photo-file">Foto (cámara o galería)</label>
        <input
          id="photo-file"
          type="file"
          accept="image/*"
          capture="environment"
          data-testid="photo-upload-file"
          @change="onFileChange"
        />
      </div>

      <div class="form-group">
        <label for="photo-caption">Descripción (opcional)</label>
        <input id="photo-caption" v-model="caption" type="text" data-testid="photo-upload-caption" />
      </div>

      <div class="actions">
        <button
          class="btn-primary"
          data-testid="photo-upload-submit"
          :disabled="!file || loading || !isRequestReady"
          @click="submitPhoto"
        >
          {{ loading ? 'Enviando...' : 'Enviar foto' }}
        </button>
      </div>

      <p v-if="status" class="status" data-testid="photo-upload-status">{{ status }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api, { extractErrorMessage } from '@/services/api'
import { fetchPhotoRequestByToken } from '@/services/tokenRequestService'

const route = useRoute()
const token = route.params.token
const file = ref(null)
const caption = ref('')
const status = ref('')
const loading = ref(false)
const requestMeta = ref(null)
const loadingRequest = ref(true)

const isRequestReady = computed(() => {
  return !loadingRequest.value && String(requestMeta.value?.status || '') === 'pending'
})

function onFileChange(event) {
  const files = event.target.files
  file.value = files && files.length ? files[0] : null
}

async function loadRequestMeta() {
  loadingRequest.value = true
  status.value = ''

  try {
    requestMeta.value = await fetchPhotoRequestByToken(token)
  } catch (requestError) {
    requestMeta.value = null
    status.value = extractErrorMessage(requestError)
  } finally {
    loadingRequest.value = false
  }
}

async function submitPhoto() {
  if (!file.value || !isRequestReady.value) return

  loading.value = true
  status.value = ''
  const formData = new FormData()
  formData.append('token', token)
  formData.append('file', file.value)
  if (caption.value) formData.append('caption', caption.value)

  try {
    await api.post('/photo-requests/submit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    requestMeta.value = requestMeta.value ? { ...requestMeta.value, status: 'uploaded' } : null
    status.value = 'Foto enviada correctamente.'
  } catch {
    status.value = 'No se pudo enviar la foto.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRequestMeta()
})
</script>

<style scoped src="./commonTokenPage.css"></style>
