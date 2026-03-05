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
