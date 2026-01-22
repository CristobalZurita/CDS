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
const emit = defineEmits(['saved'])
const form = ref({ name: '', description: '' })
async function onSubmit() {
  try {
    await createCategory(form.value)
    emit('saved')
    form.value = { name: '', description: '' }
  } catch (e) {
    console.error('Error creando categoría:', e)
    alert('Error creando categoría')
  }
}
</script>
