<template>
  <div class="photo-upload">
    <p v-if="description" class="upload-description">{{ description }}</p>
    
    <!-- Grid de fotos -->
    <div class="photos-grid">
      <!-- Fotos existentes -->
      <div 
        v-for="(photo, index) in photos" 
        :key="photo.id || index"
        class="photo-item"
        :class="{ 'has-preview': photo.preview }"
      >
        <div v-if="photo.preview" class="photo-preview">
          <img :src="photo.preview" :alt="photo.caption || 'Foto'" />
          <button 
            type="button" 
            class="photo-remove"
            @click="removePhoto(index)"
            aria-label="Eliminar foto"
          >
            ×
          </button>
        </div>
        
        <div v-else class="photo-placeholder">
          <span class="photo-icon">📷</span>
        </div>
        
        <input
          v-model="photo.caption"
          type="text"
          class="photo-caption"
          placeholder="Descripción..."
        />
      </div>
      
      <!-- Botón agregar -->
      <button
        v-if="canAddMore"
        type="button"
        class="photo-add"
        @click="triggerFileInput"
      >
        <span class="add-icon">+</span>
        <span class="add-text">Agregar foto</span>
      </button>
    </div>
    
    <!-- Input file oculto -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      multiple
      class="file-input-hidden"
      @change="handleFileChange"
    />
    
    <!-- Error -->
    <p v-if="error" class="upload-error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  max: { type: Number, default: 5 },
  description: { type: String, default: '' },
  maxSize: { type: Number, default: 5 * 1024 * 1024 } // 5MB
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const error = ref('')

// Computed
const photos = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const canAddMore = computed(() => photos.value.length < props.max)

// Métodos
function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event) {
  const files = Array.from(event.target.files)
  error.value = ''
  
  for (const file of files) {
    // Validar tipo
    if (!file.type.startsWith('image/')) {
      error.value = 'Solo se permiten archivos de imagen'
      continue
    }
    
    // Validar tamaño
    if (file.size > props.maxSize) {
      error.value = `La imagen excede el tamaño máximo (${formatSize(props.maxSize)})`
      continue
    }
    
    // Crear preview
    const reader = new FileReader()
    reader.onload = (e) => {
      photos.value.push({
        id: Date.now() + Math.random(),
        file: file,
        preview: e.target.result,
        caption: '',
        name: file.name
      })
    }
    reader.readAsDataURL(file)
  }
  
  // Reset input
  event.target.value = ''
}

function removePhoto(index) {
  photos.value.splice(index, 1)
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.photo-upload {
  width: 100%;
}

.upload-description {
  margin: 0 0 1rem;
  color: var(--cds-text-muted);
  font-size: var(--cds-text-sm);
}

.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.photo-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.photo-preview {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--cds-radius-md);
  overflow: hidden;
  background: var(--cds-light-1);
}

.photo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-remove {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cds-danger);
  color: var(--cds-white);
  border: none;
  border-radius: 50%;
  font-size: 1.25rem;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.photo-remove:hover {
  transform: scale(1.1);
}

.photo-placeholder {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--cds-light-1);
  border-radius: var(--cds-radius-md);
  border: 2px dashed var(--cds-light-4);
}

.photo-icon {
  font-size: 2rem;
  opacity: 0.5;
}

.photo-caption {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--cds-light-3);
  border-radius: var(--cds-radius-sm);
  font-size: var(--cds-text-sm);
  background: var(--cds-white);
}

.photo-caption:focus {
  outline: none;
  border-color: var(--cds-primary);
}

.photo-add {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: transparent;
  border: 2px dashed var(--cds-light-4);
  border-radius: var(--cds-radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--cds-text-muted);
}

.photo-add:hover {
  border-color: var(--cds-primary);
  color: var(--cds-primary);
  background: color-mix(in srgb, var(--cds-primary) 5%, white);
}

.add-icon {
  font-size: 2rem;
  font-weight: 300;
}

.add-text {
  font-size: var(--cds-text-sm);
}

.file-input-hidden {
  display: none;
}

.upload-error {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: var(--cds-invalid-bg);
  border: 1px solid var(--cds-invalid-border);
  border-radius: var(--cds-radius-sm);
  color: var(--cds-invalid-text);
  font-size: var(--cds-text-sm);
}
</style>
