/**
 * 📋 Ejemplo de uso del InstrumentCarousel
 * Muestra cómo integrar el carrusel en una vista de detalle de instrumento
 */

<template>
  <div class="instrument-detail">
    <div class="instrument-header">
      <h1>{{ instrument.marca }} {{ instrument.modelo }}</h1>
      <span class="badge">{{ instrument.tipos?.[0] || 'Instrumento' }}</span>
    </div>

    <!-- 🎠 CARRUSEL DE FOTOS -->
    <div class="instrument-carousel-section">
      <InstrumentCarousel 
        :instrument="instrument"
        :show-photo-label="true"
        @photo-changed="handlePhotoChange"
      />
    </div>

    <!-- INFO DEL INSTRUMENTO -->
    <div class="instrument-info">
      <div class="info-grid">
        <div class="info-item">
          <label>Marca:</label>
          <span>{{ instrument.marca }}</span>
        </div>
        <div class="info-item">
          <label>Modelo:</label>
          <span>{{ instrument.modelo }}</span>
        </div>
        <div class="info-item">
          <label>Total de fotos:</label>
          <span>{{ totalPhotos }}</span>
        </div>
        <div class="info-item" v-if="instrument.agregado_en">
          <label>Agregado:</label>
          <span>{{ formatDate(instrument.agregado_en) }}</span>
        </div>
      </div>
    </div>

    <!-- DEBUG: foto actual -->
    <div class="debug-info">
      <small>Foto actual: {{ currentPhoto }}</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import InstrumentCarousel from '@/components/InstrumentCarousel.vue'

interface Instrument {
  id: string
  marca: string
  modelo: string
  foto_principal: string
  fotos_adicionales: string[]
  tipos: string[]
  agregado_en?: string
}

interface Props {
  instrument: Instrument
}

const props = defineProps<Props>()

const currentPhoto = ref(props.instrument.foto_principal)

// Total de fotos
const totalPhotos = computed(() => {
  return 1 + (props.instrument.fotos_adicionales?.length || 0)
})

// Manejar cambio de foto
const handlePhotoChange = (photoName: string) => {
  currentPhoto.value = photoName
  console.log(`📷 Cambiada a: ${photoName}`)
}

// Formatear fecha
const formatDate = (isoDate: string): string => {
  return new Date(isoDate).toLocaleDateString('es-ES')
}
</script>

<style scoped lang="scss">
.instrument-detail {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;

  .instrument-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 1rem;

    h1 {
      margin: 0;
      font-size: 28px;
      color: #2c3e50;
    }

    .badge {
      background: #e8f4f8;
      color: #2c5aa0;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
    }
  }

  // Sección del carrusel
  .instrument-carousel-section {
    background: #fafafa;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    border: 1px solid #eee;
  }

  // Info del instrumento
  .instrument-info {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #eee;
    margin-bottom: 1rem;

    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
    }

    .info-item {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;

      label {
        font-size: 12px;
        font-weight: 600;
        color: #999;
        text-transform: uppercase;
      }

      span {
        font-size: 16px;
        color: #333;
        font-weight: 500;
      }
    }
  }

  // Debug info
  .debug-info {
    text-align: center;
    padding: 1rem;
    background: #f5f5f5;
    border-radius: 8px;
    font-size: 12px;
    color: #888;
  }
}

// Responsive
@media (max-width: 768px) {
  .instrument-detail {
    padding: 1rem;

    .instrument-header {
      flex-direction: column;
      align-items: flex-start;

      h1 {
        font-size: 22px;
      }
    }

    .instrument-carousel-section {
      padding: 1rem;
    }

    .instrument-info .info-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
