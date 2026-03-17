<template>
  <div class="cotizador-card">
    <CotizadorStepHeader
      :badge="notFoundMode ? 'Paso 1 de 2' : 'Paso 1 de 4'"
      title="Seleccionar equipo"
    >
      <template #description>
        {{ notFoundMode ? 'Escribe la marca y el modelo de tu instrumento.' : 'Elige la marca y el modelo de tu instrumento.' }}
      </template>
    </CotizadorStepHeader>

    <div v-if="!notFoundMode" class="form-grid">
      <label class="field">
        <span>Marca</span>
        <select
          :value="selectedBrand"
          :disabled="loading"
          @change="emit('brand-select', $event.target.value)"
        >
          <option value="">— Selecciona una marca —</option>
          <option v-for="brand in brands" :key="brand.id" :value="brand.id">
            {{ brand.name }}
          </option>
        </select>
      </label>

      <label class="field">
        <span>Modelo</span>
        <select
          :value="selectedModel"
          :disabled="!selectedBrand || loading"
          @change="emit('model-select', $event.target.value)"
        >
          <option value="">— Selecciona un modelo —</option>
          <option v-for="model in models" :key="model.id" :value="model.id">
            {{ model.model }}
          </option>
        </select>
        <span v-if="selectedBrand && models.length === 0 && !loading" class="field-hint">
          No hay modelos registrados para esta marca aún.
        </span>
      </label>
    </div>

    <div v-else class="form-grid">
      <label class="field">
        <span>Marca <em class="required">*</em></span>
        <input
          v-model.trim="manualBrandModel"
          type="text"
          placeholder="Ej: Yamaha, Roland, Korg…"
          autocomplete="off"
        />
      </label>

      <label class="field">
        <span>Modelo <em class="required">*</em></span>
        <input
          v-model.trim="manualModelModel"
          type="text"
          placeholder="Ej: DX7, Juno-106, Minilogue…"
          autocomplete="off"
        />
      </label>
    </div>

    <div v-if="loading && !notFoundMode" class="loading-row">
      <span class="spinner"></span> Cargando…
    </div>

    <div class="not-found-toggle">
      <button
        v-if="!notFoundMode"
        type="button"
        class="btn-link"
        @click="emit('activate-not-found-mode')"
      >
        <i class="fas fa-question-circle"></i>
        Mi instrumento no está en la lista
      </button>

      <button
        v-else
        type="button"
        class="btn-link"
        @click="emit('deactivate-not-found-mode')"
      >
        <i class="fas fa-arrow-left"></i>
        Volver a la lista
      </button>
    </div>

    <div class="actions">
      <router-link to="/" class="btn-secondary">Cancelar</router-link>
      <button
        class="btn-primary"
        :disabled="!canContinueStep1 || loading"
        @click="emit('continue')"
      >
        Siguiente →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CotizadorStepHeader from '@/components/business/CotizadorStepHeader.vue'

const props = defineProps({
  notFoundMode: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  brands: {
    type: Array,
    default: () => []
  },
  selectedBrand: {
    type: [String, Number],
    default: ''
  },
  models: {
    type: Array,
    default: () => []
  },
  selectedModel: {
    type: [String, Number],
    default: ''
  },
  manualBrand: {
    type: String,
    default: ''
  },
  manualModel: {
    type: String,
    default: ''
  },
  canContinueStep1: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'brand-select',
  'model-select',
  'update:manualBrand',
  'update:manualModel',
  'activate-not-found-mode',
  'deactivate-not-found-mode',
  'continue'
])

const manualBrandModel = computed({
  get: () => props.manualBrand,
  set: (value) => emit('update:manualBrand', value)
})

const manualModelModel = computed({
  get: () => props.manualModel,
  set: (value) => emit('update:manualModel', value)
})
</script>

<style scoped>
@import './cotizadorStepShared.css';
</style>
