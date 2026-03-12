<template>
  <div class="photo-upload-page">
    <div class="card card--narrow">
      <h1>Subir foto</h1>
      <p>Envía una foto para esta reparación.</p>

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
          :disabled="!file || loading"
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
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const token = route.params.token
const file = ref(null)
const caption = ref('')
const status = ref('')
const loading = ref(false)

function onFileChange(event) {
  const files = event.target.files
  file.value = files && files.length ? files[0] : null
}

async function submitPhoto() {
  if (!file.value) return

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
    status.value = 'Foto enviada correctamente.'
  } catch {
    status.value = 'No se pudo enviar la foto.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped src="./commonTokenPage.css"></style>
