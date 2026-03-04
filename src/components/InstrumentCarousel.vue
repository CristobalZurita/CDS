<!--
🎠 InstrumentCarousel - Carrusel adaptativo de fotos de instrumentos

Características:
- Flechas izquierda/derecha para navegar
- Miniaturas abajo para saltar directamente
- Adaptativo: 1 foto (sin controles), 2-3 fotos (carrusel completo)
- Transiciones suaves
- Indicador de página (1/2, 1/3, etc)

USO:
<InstrumentCarousel 
  :instrument="instrument"
  @photo-changed="handlePhotoChange"
/>
-->

<template>
  <div class="instrument-carousel">
    <!-- Solo 1 foto: sin carrusel -->
    <div v-if="photos.length === 1" class="carousel-single">
      <img 
        :src="getPhotoPath(photos[0])" 
        :alt="photos[0]"
        class="photo-image"
      />
    </div>

    <!-- 2-3 fotos: carrusel completo -->
    <div v-else class="carousel-container">
      <!-- Foto principal -->
      <div class="carousel-main">
        <!-- Flecha izquierda -->
        <button 
          class="carousel-arrow carousel-arrow-left"
          @click="prevPhoto"
          :disabled="currentIndex === 0"
          aria-label="Foto anterior"
        >
          <i class="fas fa-chevron-left"></i>
        </button>

        <!-- Imagen principal -->
        <div class="carousel-image-wrapper">
          <img 
            :key="currentIndex"
            :src="getPhotoPath(photos[currentIndex])" 
            :alt="photos[currentIndex]"
            class="photo-image"
            @load="onImageLoad"
          />
          
          <!-- Indicador de página (1/2, 1/3) -->
          <div class="carousel-page-indicator">
            {{ currentIndex + 1 }} / {{ photos.length }}
          </div>
        </div>

        <!-- Flecha derecha -->
        <button 
          class="carousel-arrow carousel-arrow-right"
          @click="nextPhoto"
          :disabled="currentIndex === photos.length - 1"
          aria-label="Foto siguiente"
        >
          <i class="fas fa-chevron-right"></i>
        </button>
      </div>

      <!-- Miniaturas abajo -->
      <div class="carousel-thumbnails">
        <button
          v-for="(photo, index) in photos"
          :key="`thumb-${index}`"
          class="thumbnail"
          :class="{ active: currentIndex === index }"
          @click="goToPhoto(index)"
          :aria-label="`Ver foto ${index + 1}`"
        >
          <img 
            :src="getPhotoPath(photo)"
            :alt="`Miniatura ${index + 1}`"
            class="thumbnail-image"
          />
        </button>
      </div>

      <!-- Info de foto (opcional) -->
      <div v-if="showPhotoLabel" class="carousel-photo-label">
        {{ getPhotoLabel(photos[currentIndex]) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  instrument: {
    id: string
    marca: string
    modelo: string
    foto_principal: string
    fotos_adicionales: string[]
  }
  showPhotoLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showPhotoLabel: true
})

const emit = defineEmits<{
  photoChanged: [photoName: string]
}>()

const currentIndex = ref(0)

// Combinar foto principal + adicionales
const photos = computed(() => {
  const all = [props.instrument.foto_principal]
  if (props.instrument.fotos_adicionales?.length > 0) {
    all.push(...props.instrument.fotos_adicionales)
  }
  return Array.from(new Set(all.filter(Boolean)))
})

// Navegar a foto anterior
const prevPhoto = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    emit('photoChanged', photos.value[currentIndex.value])
  }
}

// Navegar a foto siguiente
const nextPhoto = () => {
  if (currentIndex.value < photos.value.length - 1) {
    currentIndex.value++
    emit('photoChanged', photos.value[currentIndex.value])
  }
}

// Ir directamente a una foto
const goToPhoto = (index: number) => {
  currentIndex.value = index
  emit('photoChanged', photos.value[currentIndex.value])
}

// Obtener ruta completa de foto
const getPhotoPath = (photoName: string): string => {
  return `/images/instrumentos/${photoName}.webp`
}

// Obtener etiqueta amigable de foto
const getPhotoLabel = (photoName: string): string => {
  const suffix = photoName.split('_').pop()?.toUpperCase() || 'PRINCIPAL'
  
  const labels: Record<string, string> = {
    [props.instrument.foto_principal]: 'Vista Principal',
    'BACK': 'Vista Trasera',
    'FRONT': 'Vista Frontal',
    'LATERAL': 'Vista Lateral',
    'SIDE': 'Vista Lateral',
    'TOP': 'Vista Superior',
    'BOTTOM': 'Vista Inferior',
    'LEFT': 'Vista Izquierda',
    'RIGHT': 'Vista Derecha'
  }
  
  return labels[photoName] || suffix
}

// Callback cuando se carga imagen (para animaciones)
const onImageLoad = () => {
  // Trigger animación de fade-in si es necesario
}
</script>

<style scoped lang="scss">
.instrument-carousel {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacer-md);
}

.carousel-single,
.carousel-container,
.carousel-image-wrapper {
  width: 100%;
}

.carousel-single,
.carousel-main,
.carousel-image-wrapper {
  display: flex;
  justify-content: center;
}

.carousel-single .photo-image,
.carousel-image-wrapper .photo-image {
  width: 100%;
  height: 100%;
  max-height: 680px;
  object-fit: contain;
  background: #f7f7f7;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}

.carousel-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacer-md);
}

.carousel-main {
  width: 100%;
  align-items: center;
  gap: var(--spacer-md);
  position: relative;
}

.carousel-image-wrapper {
  flex: 1;
  position: relative;
  align-items: center;
  max-width: 760px;
  min-height: 420px;
  padding: 0.5rem;
  background: #f7f7f7;
  border-radius: var(--radius-lg);
}

.carousel-image-wrapper .photo-image {
  animation: fadeIn 0.3s ease-in-out;
}

.carousel-page-indicator {
  position: absolute;
  right: 12px;
  bottom: 12px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  background: rgba(0, 0, 0, 0.7);
  color: var(--color-white);
  font-size: var(--text-xs);
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.carousel-arrow {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border: 2px solid rgba(62, 60, 56, 0.2);
  border-radius: 50%;
  background: var(--color-white);
  color: var(--color-dark);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition:
    background-color var(--transition-base),
    border-color var(--transition-base),
    color var(--transition-base),
    transform var(--transition-base);
}

.carousel-arrow:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-primary) 12%, var(--color-white));
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: scale(1.08);
}

.carousel-arrow:active:not(:disabled) {
  transform: scale(0.96);
}

.carousel-arrow:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.carousel-arrow i {
  pointer-events: none;
}

.carousel-arrow-left {
  order: -1;
}

.carousel-arrow-right {
  order: 1;
}

.carousel-thumbnails {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 0 1rem;
  flex-wrap: wrap;
}

.thumbnail {
  flex-shrink: 0;
  width: 90px;
  height: 90px;
  padding: 3px;
  overflow: visible;
  border: 3px solid rgba(62, 60, 56, 0.16);
  border-radius: var(--radius-sm);
  background: var(--color-white);
  cursor: pointer;
  transition:
    border-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
}

.thumbnail:hover {
  border-color: rgba(62, 60, 56, 0.5);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.thumbnail.active {
  border-color: var(--color-primary);
  box-shadow:
    0 0 0 2px var(--color-white),
    0 0 0 4px var(--color-primary);
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #f7f7f7;
}

.carousel-photo-label {
  padding: 0 1rem;
  color: rgba(62, 60, 56, 0.78);
  font-size: var(--text-sm);
  font-weight: 500;
  text-align: center;
}

@media (max-width: 768px) {
  .carousel-main {
    gap: 0.5rem;
  }

  .carousel-arrow {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }

  .carousel-image-wrapper {
    max-width: 100%;
    min-height: 280px;
  }

  .thumbnail {
    width: 72px;
    height: 72px;
  }

  .carousel-thumbnails {
    padding: 0;
  }
}
</style>
