<template>
  <form @submit.prevent="onSubmit" data-testid="category-form">
    <div>
      <label>Nombre</label>
      <input v-model="form.name" required data-testid="category-name" />
    </div>
    <div>
      <label>Descripción</label>
      <input v-model="form.description" data-testid="category-description" />
    </div>
    <button type="submit" data-testid="category-save">{{ isEditing ? 'Actualizar' : 'Guardar' }}</button>
  </form>
</template>
<script setup>
import { computed, ref, watch } from 'vue'
import { useCategories } from '@/composables/useCategories'
const { createCategory, updateCategory } = useCategories()
const emit = defineEmits(['saved'])
const props = defineProps({
  category: {
    type: Object,
    default: null
  }
})
const emptyForm = () => ({ name: '', description: '' })
const form = ref(emptyForm())
const isEditing = computed(() => Boolean(props.category?.id))

watch(
  () => props.category,
  (category) => {
    form.value = {
      name: category?.name || '',
      description: category?.description || ''
    }
  },
  { immediate: true }
)

async function onSubmit() {
  try {
    if (isEditing.value) {
      await updateCategory(props.category.id, form.value)
    } else {
      await createCategory(form.value)
    }
    emit('saved')
    form.value = emptyForm()
  } catch (e) {
    console.error('Error guardando categoría:', e)
    alert('Error guardando categoría')
  }
}
</script>
