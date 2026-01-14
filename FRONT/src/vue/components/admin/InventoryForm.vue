<template>
  <div class="card p-3">
    <h5 class="mb-3">{{ isNew ? 'Crear item' : 'Editar item' }}</h5>
    <form @submit.prevent="onSubmit">
      <div class="mb-2">
        <label class="form-label">Nombre</label>
        <input v-model="form.name" class="form-control" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Categoría</label>
        <input v-model="form.category" class="form-control" />
      </div>
      <div class="mb-2 row">
        <div class="col">
          <label class="form-label">SKU</label>
          <input v-model="form.sku" class="form-control" />
        </div>
        <div class="col">
          <label class="form-label">Unidad</label>
          <input v-model="form.stock_unit" class="form-control" />
        </div>
      </div>
      <div class="mb-2 row">
        <div class="col">
          <label class="form-label">Stock</label>
          <input v-model.number="form.stock" type="number" class="form-control" />
        </div>
        <div class="col">
          <label class="form-label">Precio</label>
          <input v-model.number="form.price" type="number" step="0.01" class="form-control" />
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">Imagen (URL)</label>
        <input v-model="form.image_url" class="form-control" />
      </div>

      <div class="d-flex gap-2 justify-content-end">
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">Cancelar</button>
        <button type="submit" class="btn btn-primary">Guardar</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, toRefs, computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  item: {
    type: Object,
    default: null
  }
})

const emits = defineEmits(['save', 'cancel'])

const isNew = computed(() => !props.item)

const form = reactive({
  name: props.item?.name || '',
  category: props.item?.category || '',
  sku: props.item?.sku || '',
  stock: props.item?.stock ?? 0,
  stock_unit: props.item?.stock_unit || '',
  price: props.item?.price ?? 0,
  image_url: props.item?.image_url || ''
})

function onSubmit() {
  // emit a shallow copy
  emits('save', { ...form, id: props.item?.id })
}
</script>

<style scoped>
.card { background: #fff }
</style>
