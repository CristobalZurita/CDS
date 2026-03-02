<template>
  <div class="card p-3">
    <h5 class="mb-3" data-testid="inventory-form-title">{{ isNew ? 'Crear item' : 'Editar item' }}</h5>
    <form @submit.prevent="onSubmit" data-testid="inventory-form">
      <div class="mb-2">
        <label class="form-label">Nombre</label>
        <input v-model="form.name" class="form-control" data-testid="inventory-name" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Categoría</label>
        <select v-if="categories.length" v-model="form.category_id" class="form-select" data-testid="inventory-category">
          <option :value="null">Sin categoría</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
        <input
          v-else
          v-model="form.category_label"
          class="form-control"
          placeholder="Categoría (requiere catálogo)"
        />
      </div>
      <div class="mb-2 row">
        <div class="col">
          <label class="form-label">SKU</label>
          <input v-model="form.sku" class="form-control" data-testid="inventory-sku" />
        </div>
        <div class="col">
          <label class="form-label">Unidad</label>
          <input v-model="form.stock_unit" class="form-control" />
        </div>
      </div>
      <div class="mb-2 row">
        <div class="col">
          <label class="form-label">Stock</label>
          <input v-model.number="form.stock" type="number" class="form-control" data-testid="inventory-stock" />
        </div>
        <div class="col">
          <label class="form-label">Stock mínimo</label>
          <input v-model.number="form.min_quantity" type="number" class="form-control" data-testid="inventory-min-stock" />
        </div>
      </div>

      <div class="mb-2 row">
        <div class="col">
          <label class="form-label">Precio</label>
          <input v-model.number="form.price" type="number" step="0.01" class="form-control" data-testid="inventory-price" />
        </div>
        <div class="col d-flex align-items-end">
          <div class="form-check me-3">
            <input id="inventory-enabled" v-model="form.enabled" class="form-check-input" data-testid="inventory-enabled" type="checkbox" />
            <label class="form-check-label" for="inventory-enabled">Habilitado</label>
          </div>
          <div class="form-check">
            <input id="inventory-store-visible" v-model="form.store_visible" class="form-check-input" data-testid="inventory-store-visible" type="checkbox" />
            <label class="form-check-label" for="inventory-store-visible">Visible en tienda</label>
          </div>
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label">Imagen (URL)</label>
        <input v-model="form.image_url" class="form-control" data-testid="inventory-image-url" />
      </div>

      <div class="d-flex gap-2 justify-content-end">
        <button type="button" class="btn btn-secondary" data-testid="inventory-cancel" @click="$emit('cancel')">Cancelar</button>
        <button type="submit" class="btn btn-primary" data-testid="inventory-save">Guardar</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, watch } from 'vue'
import { useCategoriesStore } from '@/stores/categories'

const props = defineProps({
  item: {
    type: Object,
    default: null
  }
})

const emits = defineEmits(['save', 'cancel'])

const isNew = computed(() => !props.item)
const categoriesStore = useCategoriesStore()
const categories = computed(() => categoriesStore.categories || [])

const form = reactive({
  name: '',
  category_id: null,
  category_label: '',
  sku: '',
  stock: 0,
  min_quantity: 5,
  stock_unit: '',
  price: 0,
  image_url: '',
  enabled: true,
  store_visible: true,
})

function syncForm(item = props.item) {
  form.name = item?.name || ''
  form.category_id = item?.category_id ?? null
  form.category_label = item?.category || ''
  form.sku = item?.sku || ''
  form.stock = item?.stock ?? 0
  form.min_quantity = item?.min_stock ?? item?.min_quantity ?? 5
  form.stock_unit = item?.stock_unit || ''
  form.price = item?.price ?? 0
  form.image_url = item?.image_url || ''
  form.enabled = item?.enabled ?? true
  form.store_visible = item?.store_visible ?? false
}

function onSubmit() {
  const payload = { ...form, id: props.item?.id }
  if (!payload.category_id && payload.category_label && categories.value.length) {
    const match = categories.value.find(
      (c) => c.name?.toLowerCase() === payload.category_label.toLowerCase()
    )
    if (match) payload.category_id = match.id
  }
  delete payload.category_label
  emits('save', payload)
}

onMounted(() => {
  syncForm()
  if (!categoriesStore.categories?.length) {
    categoriesStore.fetchCategories()
  }
})

watch(() => props.item, (item) => syncForm(item))
</script>
