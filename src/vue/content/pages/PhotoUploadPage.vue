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

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.photo-upload-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: $color-gray-100-legacy;
  padding: $spacer-lg;
}

.card {
  background: $color-white;
  border-radius: $border-radius-lg;
  padding: $spacer-xl;
  max-width: 560px;
  width: 100%;
  border: 1px solid $color-gray-200-legacy;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: $spacer-sm;
  margin: $spacer-md 0;
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
