<template>
  <div class="photo-upload-page">
    <div class="card">
      <h1>Subir Foto</h1>
      <p>Envía una foto para esta reparación.</p>

      <div class="form-group">
        <label>Foto (cámara o galería)</label>
        <input type="file" accept="image/*" capture="environment" @change="onFileChange" />
      </div>

      <div class="form-group">
        <label>Descripción (opcional)</label>
        <input v-model="caption" type="text" />
      </div>

      <div class="actions">
        <button class="btn btn-primary" :disabled="!file || loading" @click="submitPhoto">
          {{ loading ? 'Enviando...' : 'Enviar foto' }}
        </button>
      </div>

      <p v-if="status" class="status">{{ status }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/services/api'

const route = useRoute()
const token = route.params.token
const file = ref(null)
const caption = ref('')
const status = ref('')
const loading = ref(false)

const onFileChange = (event) => {
  const files = event.target.files
  file.value = files && files.length ? files[0] : null
}

const submitPhoto = async () => {
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
  } catch (e) {
    status.value = 'No se pudo enviar la foto.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.photo-upload-page {
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
  max-width: 560px;
  width: 100%;
  border: 1px solid #e5e7eb;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 1rem 0;
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
