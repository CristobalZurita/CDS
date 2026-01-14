<template>
  <form @submit.prevent="onSubmit">
    <div>
      <label>Nombre</label>
      <input v-model="form.name" required />
    </div>
    <div>
      <label>Descripción</label>
      <input v-model="form.description" />
    </div>
    <button type="submit">Guardar</button>
  </form>
</template>
<script setup>
import { ref } from 'vue'
import { useCategories } from '@/composables/useCategories'
const { createCategory } = useCategories()
const form = ref({ name: '', description: '' })
function onSubmit() {
  createCategory(form.value)
}
</script>
