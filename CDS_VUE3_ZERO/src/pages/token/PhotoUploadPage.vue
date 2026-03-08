<template>
  <div class="photo-upload-page">
    <div class="card">
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
import api from '@new/services/api'

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

<style scoped>
.photo-upload-page {
  min-height: 100vh;
  background: var(--cds-light);
  padding: 1rem;
  display: grid;
  place-items: center;
}

.card {
  width: min(640px, 100%);
  background: var(--cds-white);
  border: 1px solid color-mix(in srgb, var(--cds-light) 75%, white);
  border-radius: 0.8rem;
  padding: 1rem;
  display: grid;
  gap: 0.9rem;
}

.card h1 {
  margin: 0;
  font-size: var(--cds-text-2xl);
}

.card p {
  margin: 0;
  color: var(--cds-text-muted);
}

.form-group {
  display: grid;
  gap: 0.35rem;
}

.form-group label {
  font-size: var(--cds-text-sm);
  font-weight: var(--cds-font-medium);
}

.form-group input {
  min-height: 44px;
  border: 2px solid var(--cds-light-4);
  border-radius: 0.5rem;
  padding: 0.75rem 0.875rem;
  font-size: var(--cds-text-base);
}

.actions {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.btn-primary {
  min-height: 44px;
  padding: 0.65rem 1rem;
  border-radius: 0.6rem;
  background: var(--cds-primary);
  border: 1px solid var(--cds-primary);
  color: var(--cds-white);
  cursor: pointer;
  font-size: var(--cds-text-base);
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.status {
  color: var(--cds-primary);
  font-weight: var(--cds-font-medium);
}
</style>
