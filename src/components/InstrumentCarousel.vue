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
