<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label>Nombre</label>
      <input v-model="form.name" required />
    </div>
    <div>
      <label>Marca (id)</label>
      <input v-model="form.brand_id" />
    </div>
    <div>
      <label>Modelo</label>
      <input v-model="form.model" required />
    </div>
    <div>
      <label>Tipo</label>
      <input v-model="form.type" />
    </div>
    <button type="submit">Guardar</button>
  </form>
</template>
<script setup>
import { ref } from 'vue'
import { useInstruments } from '@/composables/useInstruments'
const { createInstrument } = useInstruments()
const form = ref({ name: '', brand_id: null, model: '', type: '' })
function onSubmit() {
  createInstrument(form.value)
}
</script>
