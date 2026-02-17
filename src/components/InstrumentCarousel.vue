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
  gap: 1rem;

  // ========== SINGLE PHOTO (1 imagen) ==========
  .carousel-single {
    width: 100%;
    display: flex;
    justify-content: center;

    .photo-image {
      max-width: 100%;
      height: auto;
      max-height: 680px;
      object-fit: contain;
      background: #f7f7f7;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
  }

  // ========== CAROUSEL CONTAINER ==========
  .carousel-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  // ========== CAROUSEL MAIN (con flechas) ==========
  .carousel-main {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    position: relative;
  }

  // ========== IMAGEN PRINCIPAL ==========
  .carousel-image-wrapper {
    flex: 1;
    position: relative;
    display: flex;
    justify-content: center;
    width: 100%;
    max-width: 760px;
    min-height: 420px;
    background: #f7f7f7;
    border-radius: 10px;
    padding: 0.5rem;

    .photo-image {
      width: 100%;
      height: 100%;
      max-height: 680px;
      object-fit: contain;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      animation: fadeIn 0.3s ease-in-out;
    }

    // Indicador de página
    .carousel-page-indicator {
      position: absolute;
      bottom: 12px;
      right: 12px;
      background: rgba(0, 0, 0, 0.7);
      color: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      backdrop-filter: blur(4px);
    }
  }

  // ========== FLECHAS ==========
  .carousel-arrow {
    flex-shrink: 0;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 2px solid #ccc;
    background: white;
    color: #333;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    transition: all 0.3s ease;

    &:hover:not(:disabled) {
      background: #f0f0f0;
      border-color: #333;
      transform: scale(1.1);
    }

    &:active:not(:disabled) {
      transform: scale(0.95);
    }

    &:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    i {
      pointer-events: none;
    }
  }

  .carousel-arrow-left {
    order: -1;
  }

  .carousel-arrow-right {
    order: 1;
  }

  // ========== MINIATURAS ==========
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
    border: 3px solid #ddd;
    border-radius: 6px;
    padding: 3px;
    cursor: pointer;
    overflow: visible;
    background: white;
    transition: all 0.3s ease;

    &:hover {
      border-color: #999;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    &.active {
      border-color: #2c3e50;
      box-shadow: 0 0 0 2px #fff, 0 0 0 4px #2c3e50;
    }

    .thumbnail-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: #f7f7f7;
    }
  }

  // ========== ETIQUETA DE FOTO ==========
  .carousel-photo-label {
    font-size: 14px;
    font-weight: 500;
    color: #666;
    text-align: center;
    padding: 0 1rem;
  }
}

// ========== ANIMACIONES ==========
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

// ========== RESPONSIVE ==========
@media (max-width: 768px) {
  .instrument-carousel {
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
    }

    .thumbnail {
      width: 72px;
      height: 72px;
    }

    .carousel-thumbnails {
      gap: 6px;
      padding: 0 0.5rem;
    }
  }
}

@media (max-width: 480px) {
  .instrument-carousel {
    .carousel-main {
      gap: 0.25rem;
    }

    .carousel-arrow {
      width: 32px;
      height: 32px;
      font-size: 14px;
      border-width: 1.5px;
    }

    .carousel-image-wrapper {
      .photo-image {
        max-height: 520px;
      }

      .carousel-page-indicator {
        font-size: 11px;
        padding: 3px 6px;
      }
    }

    .thumbnail {
      width: 58px;
      height: 58px;
    }
  }
}
</style>
