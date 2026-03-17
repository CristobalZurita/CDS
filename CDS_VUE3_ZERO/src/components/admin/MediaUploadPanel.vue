<template>
  <section class="panel-card">
    <h2>Subir imágenes</h2>

    <div class="upload-controls">
      <label>
        <span>Destino</span>
        <select :value="destination" @change="emit('update:destination', $event.target.value)">
          <option value="uploads">General</option>
          <option value="instrumentos">Instrumentos</option>
          <option value="inventario">Inventario</option>
        </select>
      </label>
    </div>

    <div
      class="drop-zone"
      :class="{ 'drop-zone--active': isDragging }"
      @dragenter.prevent="isDragging = true"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <i class="fa-solid fa-cloud-arrow-up"></i>
      <p>Arrastrá imágenes aquí o hacé clic para seleccionar</p>
      <span>Podés seleccionar múltiples archivos o una carpeta completa</span>
      <input ref="fileInput" type="file" multiple accept="image/*" @change="onFileSelect" />
      <input ref="folderInput" type="file" multiple accept="image/*" webkitdirectory @change="onFileSelect" />
    </div>

    <div class="upload-extra-actions">
      <button class="btn-secondary" type="button" @click="folderInput?.click()">
        <i class="fa-solid fa-folder-open"></i> Seleccionar carpeta
      </button>
    </div>

    <p v-if="uploadValidationError" class="upload-validation-error">{{ uploadValidationError }}</p>

    <div v-if="queue.length" class="queue-list">
      <div v-for="item in queue" :key="`${item.publicId}-${item.size}`" class="queue-item">
        <div class="queue-main">
          <span class="queue-name">{{ item.name }}</span>
          <span class="queue-target">{{ queuePath(item) }}</span>
        </div>
        <span class="queue-size">{{ formatBytes(item.size) }}</span>
        <span class="queue-status" :class="`status--${item.status}`">{{ statusLabel(item.status) }}</span>
      </div>
    </div>

    <div v-if="queue.length" class="panel-actions">
      <button class="btn-primary" :disabled="uploading" @click="emit('upload-all')">
        {{ uploading ? `Subiendo ${uploadProgress}/${queue.length}...` : `Subir ${queue.length} imagen(es)` }}
      </button>
      <button class="btn-secondary" :disabled="uploading" @click="emit('clear-queue')">Limpiar</button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  destination: {
    type: String,
    default: 'uploads'
  },
  queue: {
    type: Array,
    default: () => []
  },
  uploading: {
    type: Boolean,
    default: false
  },
  uploadProgress: {
    type: Number,
    default: 0
  },
  uploadValidationError: {
    type: String,
    default: ''
  },
  formatBytes: {
    type: Function,
    required: true
  },
  queuePath: {
    type: Function,
    required: true
  },
  statusLabel: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['update:destination', 'files-selected', 'upload-all', 'clear-queue'])

const isDragging = ref(false)
const fileInput = ref(null)
const folderInput = ref(null)

function emitImageFiles(fileList) {
  const files = Array.from(fileList || []).filter(file => file.type.startsWith('image/'))
  if (files.length) emit('files-selected', files)
}

function onDrop(event) {
  isDragging.value = false
  emitImageFiles(event.dataTransfer?.files)
}

function onFileSelect(event) {
  emitImageFiles(event.target?.files)
  event.target.value = ''
}
</script>

<style scoped src="@/pages/admin/commonAdminPage.css"></style>
<style scoped src="@/pages/admin/mediaPageShared.css"></style>
