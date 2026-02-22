<template>
  <div class="quote-generator">
    <h3>Generador de Cotización (IA)</h3>
    <p class="muted">Prueba rápida: selecciona marca y modelo para generar una estimación de ejemplo.</p>

    <div class="controls">
      <select v-model="brand" @change="onChange">
        <option value="">-- Selecciona marca --</option>
        <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>

      <select v-model="model" @change="onChange">
        <option value="">-- Selecciona modelo --</option>
        <option v-for="m in models" :key="m.id" :value="m.id">{{ m.model }}</option>
      </select>

      <button class="btn btn-primary" @click="generate" :disabled="!model">Generar</button>
    </div>

    <div v-if="result" class="result">
      <h4>Resultado de ejemplo</h4>
      <p class="muted">{{ result }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { api } from '@/services/api'
import { useInstrumentsCatalog } from '@/composables/useInstrumentsCatalog'

const brand = ref('')
const model = ref('')
const result = ref(null)

const { brands, getInstrumentsByBrand } = useInstrumentsCatalog()

const models = computed(() => {
  if (!brand.value) return []
  return getInstrumentsByBrand(brand.value)
})

function onChange() {
  result.value = null
}

async function generate() {
  const m = models.value.find(x => x.id === model.value)
  if (!m) return

  result.value = null
  try {
    const res = await api.post('/quotations/estimate', {
      instrument_id: m.id,
      faults: []
    })
    result.value = JSON.stringify(res.data, null, 2)
  } catch (err) {
    result.value = 'Error al generar estimación: ' + (err.response?.data?.detail || err.message)
  }
}
</script>

<style lang="scss" scoped>
@import '@/scss/_core.scss';

.quote-generator {
  padding: $spacer-md;
}

.controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.result {
  margin-top: $spacer-md;
  padding: 0.75rem;
  border-radius: $border-radius-sm;
  background: rgba($color-black, 0.03);
}
</style>
